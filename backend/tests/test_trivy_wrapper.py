import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from app.models.schemas import Severity
from app.scanners.trivy_wrapper import scan_with_trivy

# Payload real capturado ejecutando
# `trivy config iac_fixtures/virtual_machines --format json --quiet`
# (trivy v0.71.2) para fijar el contrato de parseo sin depender del binario en CI.
_TRIVY_PAYLOAD = {
    "Results": [
        {
            # Hallazgo sin recurso identificable en CauseMetadata (ocurre con
            # algunas reglas de trivy, p. ej. checks a nivel de VM/NIC): debe
            # normalizarse con resource_type/resource_name vacíos en vez de romper.
            "Target": "",
            "Misconfigurations": [
                {
                    "ID": "AZU-0068",
                    "Title": "VM Not Attached To Network",
                    "Message": "Virtual machine network interface is not associated with a network security group.",
                    "Severity": "MEDIUM",
                    "CauseMetadata": {"Provider": "Azure", "Service": "compute"},
                }
            ],
        },
        {
            # Entrada agregada sin hallazgos (todos los checks pasaron): no debe
            # generar StaticFinding alguno.
            "Target": ".",
            "MisconfSummary": {"Successes": 53, "Failures": 0},
        },
        {
            "Target": "vm_unmanaged_disk_unencrypted.tf",
            "Misconfigurations": [
                {
                    "ID": "AZU-0038",
                    "Title": "Enable disk encryption on managed disk",
                    "Message": "Managed disk is not encrypted.",
                    "Severity": "HIGH",
                    "CauseMetadata": {
                        "Resource": "azurerm_managed_disk.data_example",
                        "StartLine": 14,
                        "EndLine": 14,
                    },
                }
            ],
        },
        {
            "Target": "vm_rdp_open_public.tf",
            "Misconfigurations": [
                {
                    "ID": "AZU-0049",
                    "Title": "Security group should not allow unrestricted ingress to RDP port from any IP address.",
                    "Message": "Security group rule allows unrestricted ingress to RDP port from any IP address.",
                    "Severity": "CRITICAL",
                    "CauseMetadata": {
                        "Resource": "azurerm_network_security_group.rdp_example",
                        "StartLine": 18,
                        "EndLine": 18,
                    },
                }
            ],
        },
    ]
}


def _completed_process(stdout: str = "", returncode: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["trivy"], returncode=returncode, stdout=stdout, stderr="")


def test_scan_with_trivy_normalizes_results(tmp_path):
    with patch("subprocess.run", return_value=_completed_process(json.dumps(_TRIVY_PAYLOAD))):
        findings = scan_with_trivy(tmp_path)

    assert len(findings) == 3

    unresolved_finding = findings[0]
    assert unresolved_finding.check_id == "AZU-0068"
    assert unresolved_finding.resource_type == ""
    assert unresolved_finding.resource_name == ""
    assert unresolved_finding.static_severity == Severity.MEDIUM
    assert unresolved_finding.source_tool == "trivy"

    disk_finding = findings[1]
    assert disk_finding.check_id == "AZU-0038"
    assert disk_finding.resource_type == "azurerm_managed_disk"
    assert disk_finding.resource_name == "data_example"
    assert disk_finding.file_path == "vm_unmanaged_disk_unencrypted.tf"
    assert disk_finding.line_range == (14, 14)
    assert disk_finding.static_severity == Severity.HIGH
    assert disk_finding.description == "Managed disk is not encrypted."

    rdp_finding = findings[2]
    assert rdp_finding.resource_type == "azurerm_network_security_group"
    assert rdp_finding.resource_name == "rdp_example"
    assert rdp_finding.static_severity == Severity.CRITICAL


def test_scan_with_trivy_returns_empty_list_when_no_issues(tmp_path):
    payload = {"Results": [{"Target": ".", "MisconfSummary": {"Successes": 10, "Failures": 0}}]}
    with patch("subprocess.run", return_value=_completed_process(json.dumps(payload))):
        assert scan_with_trivy(tmp_path) == []


def test_scan_with_trivy_raises_when_binary_missing(tmp_path):
    with patch("subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(RuntimeError, match="trivy"):
            scan_with_trivy(tmp_path)


def test_scan_with_trivy_raises_on_timeout(tmp_path):
    with patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="trivy", timeout=120),
    ):
        with pytest.raises(RuntimeError, match="timeout"):
            scan_with_trivy(tmp_path)


def test_scan_with_trivy_raises_on_unexpected_return_code(tmp_path):
    with patch("subprocess.run", return_value=_completed_process(returncode=2)):
        with pytest.raises(RuntimeError, match="código 2"):
            scan_with_trivy(tmp_path)


def test_scan_with_trivy_raises_for_missing_directory():
    with pytest.raises(FileNotFoundError):
        scan_with_trivy(Path("/definitely/not/a/real/dir"))
