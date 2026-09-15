"""Wrapper sobre el binario trivy para complementar el baseline de Checkov (HU-02).

Sustituye a tfsec, que Aqua Security archivó y fusionó dentro de Trivy
(`trivy config`), heredando el mismo motor de reglas de Terraform.
"""

import json
import subprocess
from pathlib import Path

from app.models.schemas import Severity, StaticFinding

_TIMEOUT_SECONDS = 120
# A diferencia de tfsec, `trivy config` devuelve siempre 0 (incluso con
# hallazgos) salvo que se pase `--exit-code`, que no usamos; cualquier
# código distinto de 0 indica un fallo real del binario.
_EXPECTED_RETURN_CODES = (0,)


def scan_with_trivy(terraform_dir: Path) -> list[StaticFinding]:
    """Ejecuta trivy como subproceso (`trivy config <dir> --format json`) y normaliza la salida."""
    if not terraform_dir.is_dir():
        raise FileNotFoundError(f"El directorio Terraform '{terraform_dir}' no existe")

    try:
        result = subprocess.run(
            ["trivy", "config", str(terraform_dir), "--format", "json", "--quiet"],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "El binario 'trivy' no está instalado o no está disponible en el PATH"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"trivy superó el timeout de {_TIMEOUT_SECONDS}s al analizar {terraform_dir}"
        ) from exc

    if result.returncode not in _EXPECTED_RETURN_CODES:
        raise RuntimeError(
            f"trivy finalizó con código {result.returncode}: {result.stderr.strip()}"
        )

    payload = json.loads(result.stdout) if result.stdout.strip() else {}

    findings = []
    for scan_result in payload.get("Results") or []:
        file_path = scan_result.get("Target", "")
        for raw in scan_result.get("Misconfigurations") or []:
            cause_metadata = raw.get("CauseMetadata") or {}
            resource_type, _, resource_name = cause_metadata.get("Resource", "").partition(".")
            findings.append(
                StaticFinding(
                    check_id=raw.get("ID", ""),
                    resource_type=resource_type,
                    resource_name=resource_name,
                    file_path=file_path,
                    line_range=(
                        cause_metadata.get("StartLine", 0),
                        cause_metadata.get("EndLine", 0),
                    ),
                    static_severity=_map_trivy_severity(raw.get("Severity")),
                    source_tool="trivy",
                    description=raw.get("Message") or raw.get("Title", ""),
                )
            )
    return findings


def _map_trivy_severity(raw_severity: str | None) -> Severity:
    mapping = {
        "LOW": Severity.LOW,
        "MEDIUM": Severity.MEDIUM,
        "HIGH": Severity.HIGH,
        "CRITICAL": Severity.CRITICAL,
    }
    return mapping.get((raw_severity or "").upper(), Severity.MEDIUM)
