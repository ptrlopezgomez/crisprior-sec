import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from app.models.schemas import Severity
from app.scanners.tfsec_wrapper import scan_with_tfsec

# Payload real capturado ejecutando `tfsec iac_fixtures/virtual_machines --format json`
# (tfsec v1.28.14) para fijar el contrato de parseo sin depender del binario en CI.
_TFSEC_PAYLOAD = {
    "results": [
        {
            "rule_id": "AVD-AZU-0038",
            "long_id": "azure-compute-enable-disk-encryption",
            "description": "Managed disk is not encrypted.",
            "severity": "HIGH",
            "resource": "azurerm_managed_disk.data_example",
            "location": {
                "filename": "/repo/iac_fixtures/virtual_machines/vm_unmanaged_disk_unencrypted.tf",
                "start_line": 14,
                "end_line": 14,
            },
        },
        {
            "rule_id": "AVD-AZU-0048",
            "long_id": "azure-network-disable-rdp-from-internet",
            "description": "Security group rule allows ingress to RDP port from multiple public internet addresses.",
            "severity": "CRITICAL",
            "resource": "azurerm_network_security_group.rdp_example",
            "location": {
                "filename": "/repo/iac_fixtures/virtual_machines/vm_rdp_open_public.tf",
                "start_line": 18,
                "end_line": 18,
            },
        },
    ]
}


def _fake_run(returncode: int, stdout: str = "", stderr: str = ""):
    def _run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)

    return _run


def test_scan_with_tfsec_normalizes_results(tmp_path):
    with patch("subprocess.run", side_effect=_fake_run(1, stdout=json.dumps(_TFSEC_PAYLOAD))):
        findings = scan_with_tfsec(tmp_path)

    assert len(findings) == 2

    disk_finding = findings[0]
    assert disk_finding.check_id == "azure-compute-enable-disk-encryption"
    assert disk_finding.resource_type == "azurerm_managed_disk"
    assert disk_finding.resource_name == "data_example"
    assert disk_finding.static_severity == Severity.HIGH
    assert disk_finding.source_tool == "tfsec"
    assert disk_finding.line_range == (14, 14)

    rdp_finding = findings[1]
    assert rdp_finding.static_severity == Severity.CRITICAL
    assert rdp_finding.resource_name == "rdp_example"


def test_scan_with_tfsec_returns_empty_list_when_no_issues(tmp_path):
    with patch("subprocess.run", side_effect=_fake_run(0, stdout=json.dumps({"results": None}))):
        assert scan_with_tfsec(tmp_path) == []


def test_scan_with_tfsec_raises_when_binary_missing(tmp_path):
    with patch("subprocess.run", side_effect=FileNotFoundError()):
        with pytest.raises(RuntimeError, match="tfsec"):
            scan_with_tfsec(tmp_path)


def test_scan_with_tfsec_raises_on_timeout(tmp_path):
    with patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="tfsec", timeout=120),
    ):
        with pytest.raises(RuntimeError, match="timeout"):
            scan_with_tfsec(tmp_path)


def test_scan_with_tfsec_raises_on_unexpected_return_code(tmp_path):
    with patch("subprocess.run", side_effect=_fake_run(2, stderr="boom")):
        with pytest.raises(RuntimeError, match="boom"):
            scan_with_tfsec(tmp_path)


def test_scan_with_tfsec_raises_for_missing_directory():
    with pytest.raises(FileNotFoundError):
        scan_with_tfsec(Path("/definitely/not/a/real/dir"))
