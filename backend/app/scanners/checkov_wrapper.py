"""Wrapper sobre la API de Checkov para obtener el baseline de hallazgos (HU-02)."""

from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner

from app.models.schemas import Severity, StaticFinding

# Checkov OSS no asigna severidad a sus checks nativos (ese metadato solo se
# resuelve contra la plataforma Bridgecrew/Prisma Cloud), por lo que
# `record.severity` llega como None en un entorno self-hosted. Mantenemos una
# tabla local con la severidad "gold standard" acordada por el panel
# DevSecOps para los checks cubiertos por `iac_fixtures/` y usamos MEDIUM
# como valor conservador por defecto para cualquier otro check.
_KNOWN_CHECK_SEVERITIES: dict[str, Severity] = {
    "CKV_AZURE_9": Severity.HIGH,  # RDP accesible desde Internet
    "CKV_AZURE_10": Severity.HIGH,  # SSH accesible desde Internet
    "CKV_AZURE_2": Severity.MEDIUM,  # Managed disk sin cifrado
    "CKV_AZURE_35": Severity.HIGH,  # Storage Account sin default deny
    "CKV_AZURE_44": Severity.MEDIUM,  # Storage Account con TLS desactualizado
    "CKV_AZURE_109": Severity.HIGH,  # Key Vault sin reglas de firewall
    "CKV_AZURE_110": Severity.MEDIUM,  # Key Vault sin purge protection
    "CKV_AZURE_42": Severity.MEDIUM,  # Key Vault sin retención de soft-delete adecuada
    "CKV_AZURE_13": Severity.HIGH,  # App Service sin autenticación integrada
    "CKV_AZURE_14": Severity.HIGH,  # App Service sin HTTPS forzado
    "CKV_AZURE_15": Severity.MEDIUM,  # App Service con TLS desactualizado
}


def scan_with_checkov(terraform_dir: Path) -> list[StaticFinding]:
    """Ejecuta Checkov sobre un directorio de archivos .tf y normaliza la salida."""
    if not terraform_dir.is_dir():
        raise FileNotFoundError(f"El directorio Terraform '{terraform_dir}' no existe")

    runner = Runner()
    report = runner.run(
        root_folder=str(terraform_dir),
        runner_filter=RunnerFilter(framework=["terraform"]),
    )

    findings = []
    for record in report.failed_checks:
        resource_type, _, resource_name = record.resource.partition(".")
        findings.append(
            StaticFinding(
                check_id=record.check_id,
                resource_type=resource_type,
                resource_name=resource_name,
                file_path=record.file_path,
                line_range=tuple(record.file_line_range),
                static_severity=_map_checkov_severity(record.check_id, record.severity),
                source_tool="checkov",
                description=record.check_name,
            )
        )
    return findings


def _map_checkov_severity(check_id: str, raw_severity: str | None) -> Severity:
    mapping = {
        "LOW": Severity.LOW,
        "MEDIUM": Severity.MEDIUM,
        "HIGH": Severity.HIGH,
        "CRITICAL": Severity.CRITICAL,
    }
    if raw_severity:
        resolved = mapping.get(str(raw_severity).upper())
        if resolved is not None:
            return resolved
    return _KNOWN_CHECK_SEVERITIES.get(check_id, Severity.MEDIUM)
