"""Wrapper sobre el binario tfsec para complementar el baseline de Checkov (HU-02)."""

import json
import subprocess
from pathlib import Path

from app.models.schemas import Severity, StaticFinding

_TIMEOUT_SECONDS = 120
# tfsec devuelve 0 (sin hallazgos) o 1 (hallazgos encontrados) en ejecuciones
# normales; cualquier otro código indica un fallo real del binario.
_EXPECTED_RETURN_CODES = (0, 1)


def scan_with_tfsec(terraform_dir: Path) -> list[StaticFinding]:
    """Ejecuta tfsec como subproceso (`tfsec <dir> --format json`) y normaliza la salida."""
    if not terraform_dir.is_dir():
        raise FileNotFoundError(f"El directorio Terraform '{terraform_dir}' no existe")

    try:
        result = subprocess.run(
            ["tfsec", str(terraform_dir), "--format", "json", "--no-color"],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "El binario 'tfsec' no está instalado o no está disponible en el PATH"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"tfsec superó el timeout de {_TIMEOUT_SECONDS}s al analizar {terraform_dir}"
        ) from exc

    if result.returncode not in _EXPECTED_RETURN_CODES:
        raise RuntimeError(
            f"tfsec finalizó con código {result.returncode}: {result.stderr.strip()}"
        )

    payload = json.loads(result.stdout) if result.stdout.strip() else {}

    findings = []
    for raw in payload.get("results") or []:
        resource_type, _, resource_name = raw.get("resource", "").partition(".")
        location = raw.get("location") or {}
        findings.append(
            StaticFinding(
                check_id=raw.get("long_id") or raw.get("rule_id", ""),
                resource_type=resource_type,
                resource_name=resource_name,
                file_path=location.get("filename", ""),
                line_range=(location.get("start_line", 0), location.get("end_line", 0)),
                static_severity=_map_tfsec_severity(raw.get("severity")),
                source_tool="tfsec",
                description=raw.get("description", ""),
            )
        )
    return findings


def _map_tfsec_severity(raw_severity: str | None) -> Severity:
    mapping = {
        "LOW": Severity.LOW,
        "MEDIUM": Severity.MEDIUM,
        "HIGH": Severity.HIGH,
        "CRITICAL": Severity.CRITICAL,
    }
    return mapping.get((raw_severity or "").upper(), Severity.MEDIUM)
