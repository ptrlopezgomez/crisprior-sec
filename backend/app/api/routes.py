import json
import tempfile
from pathlib import Path
from typing import Any, Iterator

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.engine.context_extractor import extract_resource_context
from app.engine.prioritizer import calculate_contextual_score, prioritize, score_to_severity
from app.engine.vector_store import query_relevant_guidelines
from app.llm.ollama_client import generate_explanation
from app.models.schemas import PrioritizedFinding, ResourceContext, ScanResponse, StaticFinding
from app.scanners.checkov_wrapper import scan_with_checkov
from app.scanners.tfsec_wrapper import scan_with_tfsec

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/scan")
async def scan_terraform(files: list[UploadFile]) -> StreamingResponse:
    """Recibe archivos .tf y analiza cada hallazgo (HU-01 a HU-05).

    La respuesta es NDJSON (una línea = un evento JSON), no un único JSON:
    Checkov/tfsec y, sobre todo, el LLM local tardan varios segundos por
    hallazgo, así que se emite un evento de progreso por cada uno en lugar
    de bloquear al cliente sin ninguna señal hasta el final. El último
    evento (`type: "result"`) trae el `ScanResponse` completo; un evento
    `type: "error"` señala un fallo irrecuperable a medio análisis.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No se recibió ningún archivo")

    contents: dict[str, bytes] = {}
    for upload in files:
        if not upload.filename or not upload.filename.endswith(".tf"):
            raise HTTPException(
                status_code=400,
                detail=f"'{upload.filename}' no es un archivo Terraform (.tf) válido",
            )

        data = await upload.read()
        if len(data) > settings.max_upload_size_bytes:
            max_mb = settings.max_upload_size_bytes / (1024 * 1024)
            raise HTTPException(
                status_code=413,
                detail=f"'{upload.filename}' excede el tamaño máximo permitido ({max_mb:.0f}MB)",
            )
        contents[Path(upload.filename).name] = data

    tmp_dir = tempfile.TemporaryDirectory(prefix="crisprior-sec-")
    terraform_dir = Path(tmp_dir.name)
    for filename, data in contents.items():
        (terraform_dir / filename).write_bytes(data)

    return StreamingResponse(_stream_pipeline(terraform_dir, tmp_dir), media_type="application/x-ndjson")


def _event(event_type: str, **payload: Any) -> str:
    return json.dumps({"type": event_type, **payload}) + "\n"


def _stream_pipeline(terraform_dir: Path, tmp_dir: tempfile.TemporaryDirectory) -> Iterator[str]:
    """Generador síncrono: Starlette itera un `StreamingResponse` no-async en
    un threadpool (`iterate_in_threadpool`), así que cada paso bloqueante
    (Checkov, tfsec, ChromaDB, Ollama) libera el event loop de Uvicorn en
    lugar de acapararlo, permitiendo que otras peticiones (p. ej. /health)
    se sigan atendiendo mientras este análisis corre en segundo plano.
    """
    try:
        warnings: list[str] = []

        baseline: list[StaticFinding] = scan_with_checkov(terraform_dir)
        try:
            baseline.extend(scan_with_tfsec(terraform_dir))
        except RuntimeError as exc:
            warnings.append(f"tfsec no disponible, baseline calculado solo con Checkov: {exc}")

        total = len(baseline)
        yield _event("start", total=total)

        prioritized: list[PrioritizedFinding] = []
        for index, finding in enumerate(baseline, start=1):
            yield _event(
                "progress",
                current=index,
                total=total,
                check_id=finding.check_id,
                resource=f"{finding.resource_type}.{finding.resource_name}",
            )

            context = _extract_context_safely(terraform_dir, finding, warnings)
            guidelines = _retrieve_guidelines_safely(finding, context, warnings)
            explanation = _generate_explanation_safely(finding, context, guidelines, warnings)
            prioritized.append(prioritize(finding, context, explanation))

        prioritized.sort(key=lambda item: item.contextual_score, reverse=True)

        # Los mensajes de degradación (tfsec/Ollama/ChromaDB no disponibles) se
        # reportan una sola vez, no por cada hallazgo afectado.
        unique_warnings = list(dict.fromkeys(warnings))
        result = ScanResponse(findings=prioritized, warnings=unique_warnings)
        yield _event("result", data=result.model_dump())
    except Exception as exc:  # noqa: BLE001 - último recurso: el stream ya empezó con status 200
        yield _event("error", message=str(exc))
    finally:
        tmp_dir.cleanup()


def _extract_context_safely(
    terraform_dir: Path, finding: StaticFinding, warnings: list[str]
) -> ResourceContext:
    try:
        return extract_resource_context(terraform_dir, finding.resource_type, finding.resource_name)
    except ValueError:
        warnings.append(
            "No se pudo resolver el contexto de red para uno o más recursos; "
            "se asumió un contexto neutro (sin evidencia de exposición ni de aislamiento)."
        )
        return ResourceContext(
            resource_name=finding.resource_name,
            publicly_exposed=False,
            network_isolated=False,
            has_compensating_controls=False,
        )


def _retrieve_guidelines_safely(
    finding: StaticFinding, context: ResourceContext, warnings: list[str]
) -> list[str]:
    query_text = (
        f"{finding.description} ({finding.resource_type}). "
        f"Expuesto públicamente: {context.publicly_exposed}. "
        f"Aislado de red: {context.network_isolated}."
    )
    try:
        return query_relevant_guidelines(query_text)
    except Exception:  # noqa: BLE001 - dependencia externa (ChromaDB/modelo de embeddings)
        warnings.append(
            "La base de conocimiento vectorial (ChromaDB) no está disponible; "
            "las explicaciones se generaron sin directrices de referencia."
        )
        return []


def _generate_explanation_safely(
    finding: StaticFinding,
    context: ResourceContext,
    guidelines: list[str],
    warnings: list[str],
) -> str:
    score = calculate_contextual_score(finding, context)
    severity = score_to_severity(score)
    try:
        return generate_explanation(finding, context, score, severity, guidelines)
    except Exception:  # noqa: BLE001 - el LLM local (Ollama) es una dependencia externa opcional
        warnings.append(
            "El LLM local (Ollama) no está disponible; se devolvió una explicación de reemplazo."
        )
        guideline_hint = guidelines[0] if guidelines else "sin directriz asociada disponible"
        return (
            f"[Explicación automática no disponible] Severidad contextual recalculada: "
            f"{severity.value} (score {score:.1f}/100). Directriz relevante: {guideline_hint}"
        )
