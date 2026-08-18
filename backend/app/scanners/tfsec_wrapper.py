"""Wrapper sobre el binario tfsec para complementar el baseline de Checkov (HU-02)."""

import json
import subprocess
from pathlib import Path

from app.models.schemas import Severity, StaticFinding


def scan_with_tfsec(terraform_dir: Path) -> list[StaticFinding]:
    """Ejecuta tfsec como subproceso (`tfsec <dir> --format json`) y normaliza la salida.

    TODO (Sprint 1): validar el binario en el PATH, manejar timeouts y
    mapear cada resultado al esquema StaticFinding.
    """
    raise NotImplementedError("Integración con tfsec pendiente (HU-02)")


def _map_tfsec_severity(raw_severity: str | None) -> Severity:
    mapping = {
        "LOW": Severity.LOW,
        "MEDIUM": Severity.MEDIUM,
        "HIGH": Severity.HIGH,
        "CRITICAL": Severity.CRITICAL,
    }
    return mapping.get((raw_severity or "").upper(), Severity.MEDIUM)
