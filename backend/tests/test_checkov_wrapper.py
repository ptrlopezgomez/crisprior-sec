import shutil
from pathlib import Path

import pytest

from app.models.schemas import Severity
from app.scanners.checkov_wrapper import scan_with_checkov

IAC_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "iac_fixtures"


def _scan_fixture(tmp_path, relative_path: str):
    shutil.copy(IAC_FIXTURES_DIR / relative_path, tmp_path)
    return scan_with_checkov(tmp_path)


def test_scan_with_checkov_detects_keyvault_firewall_finding(tmp_path):
    findings = _scan_fixture(tmp_path, "keyvault/keyvault_public_network_no_firewall.tf")
    by_check_id = {f.check_id: f for f in findings}

    finding = by_check_id["CKV_AZURE_109"]
    assert finding.resource_type == "azurerm_key_vault"
    assert finding.resource_name == "public_example"
    assert finding.static_severity == Severity.HIGH
    assert finding.source_tool == "checkov"
    assert finding.file_path.endswith("keyvault_public_network_no_firewall.tf")
    assert finding.line_range[0] > 0


def test_scan_with_checkov_detects_storage_tls_finding(tmp_path):
    findings = _scan_fixture(tmp_path, "storage/storage_tls_version_outdated.tf")
    by_check_id = {f.check_id: f for f in findings}

    finding = by_check_id["CKV_AZURE_44"]
    assert finding.resource_type == "azurerm_storage_account"
    assert finding.resource_name == "tls_example"
    assert finding.static_severity == Severity.MEDIUM


def test_scan_with_checkov_detects_app_service_auth_finding(tmp_path):
    findings = _scan_fixture(tmp_path, "app_service/app_service_auth_disabled.tf")
    by_check_id = {f.check_id: f for f in findings}

    finding = by_check_id["CKV_AZURE_13"]
    assert finding.resource_type == "azurerm_linux_web_app"
    assert finding.resource_name == "no_auth_example"
    assert finding.static_severity == Severity.HIGH


def test_scan_with_checkov_returns_empty_list_when_no_findings(tmp_path):
    (tmp_path / "empty.tf").write_text("# sin recursos\n")

    assert scan_with_checkov(tmp_path) == []


def test_scan_with_checkov_raises_for_missing_directory(tmp_path):
    missing_dir = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        scan_with_checkov(missing_dir)
