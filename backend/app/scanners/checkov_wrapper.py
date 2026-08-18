"""Wrapper sobre la API de Checkov para obtener el baseline de hallazgos (HU-02)."""

from pathlib import Path

from app.models.schemas import Severity, StaticFinding


def scan_with_checkov(terraform_dir: Path) -> list[StaticFinding]:
    """Ejecuta Checkov sobre un directorio de archivos .tf y normaliza la salida.

    TODO (Sprint 1): invocar checkov.main.run() en modo programático,
    parsear el JSON de salida y mapear cada check al esquema StaticFinding.
    """
    raise NotImplementedError("Integración con Checkov pendiente (HU-02)")


def _map_checkov_severity(raw_severity: str | None) -> Severity:
    mapping = {
        "LOW": Severity.LOW,
        "MEDIUM": Severity.MEDIUM,
        "HIGH": Severity.HIGH,
        "CRITICAL": Severity.CRITICAL,
    }
    return mapping.get((raw_severity or "").upper(), Severity.MEDIUM)
