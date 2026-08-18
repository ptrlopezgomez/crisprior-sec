"""Extracción de variables de contexto de red desde el AST de Terraform (HU-03)."""

from pathlib import Path

from app.models.schemas import ResourceContext


def extract_resource_context(terraform_dir: Path, resource_name: str) -> ResourceContext:
    """Analiza el grafo de recursos para determinar exposición pública,
    aislamiento de red y presencia de controles compensatorios.

    TODO (Sprint 2): construir el grafo de dependencias (NSGs, subnets,
    reglas de firewall) y detectar patrones de exposición (0.0.0.0/0).
    """
    raise NotImplementedError("Extracción de contexto de red pendiente (HU-03)")
