import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.engine.vector_store import get_collection
from app.main import app

IAC_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "iac_fixtures"

client = TestClient(app)


def _upload(tf_paths: list[Path]):
    files = [("files", (p.name, p.read_bytes(), "text/plain")) for p in tf_paths]
    return client.post("/api/v1/scan", files=files)


def _scan(tf_paths: list[Path]) -> tuple[list[dict], dict]:
    """Sube los archivos y devuelve (eventos NDJSON, payload del evento 'result')."""
    response = _upload(tf_paths)
    assert response.status_code == 200, response.text

    events = [json.loads(line) for line in response.text.splitlines() if line.strip()]
    error_events = [e for e in events if e["type"] == "error"]
    assert not error_events, f"el análisis falló a mitad de stream: {error_events}"

    result_events = [e for e in events if e["type"] == "result"]
    assert result_events, "no se recibió ningún evento 'result' en el stream"
    return events, result_events[0]["data"]


@pytest.fixture
def seeded_chromadb(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "chromadb_path", str(tmp_path / "chroma"))
    get_collection.cache_clear()
    collection = get_collection()
    collection.upsert(
        ids=["ssh-guideline"],
        documents=[
            "Un puerto SSH o RDP abierto a 0.0.0.0/0 sin aislamiento de red es una "
            "exposición crítica salvo que exista un Bastion Host o VPN."
        ],
        metadatas=[{"category": "network_exposure"}],
    )
    yield
    get_collection.cache_clear()


def test_scan_rejects_empty_upload():
    response = client.post("/api/v1/scan", files=[])

    assert response.status_code in (400, 422)


def test_scan_rejects_non_terraform_file(tmp_path):
    bad_file = tmp_path / "not_terraform.txt"
    bad_file.write_text("hola")

    response = _upload([bad_file])

    assert response.status_code == 400


def test_scan_rejects_oversized_file(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_size_bytes", 10)
    big_file = tmp_path / "big.tf"
    big_file.write_text("# " + "x" * 100)

    response = _upload([big_file])

    assert response.status_code == 413


def test_scan_streams_progress_events_in_order(seeded_chromadb):
    tf_path = IAC_FIXTURES_DIR / "keyvault" / "keyvault_purge_protection_disabled.tf"

    with patch("app.api.routes.generate_explanation", return_value="explicación simulada"):
        events, payload = _scan([tf_path])

    assert events[0]["type"] == "start"
    total = events[0]["total"]
    assert total == len(payload["findings"])

    progress_events = [e for e in events if e["type"] == "progress"]
    assert [e["current"] for e in progress_events] == list(range(1, total + 1))
    assert all(e["total"] == total for e in progress_events)
    assert all(e["check_id"] and e["resource"] for e in progress_events)

    assert events[-1]["type"] == "result"


def test_scan_orchestrates_full_pipeline(seeded_chromadb):
    tf_path = IAC_FIXTURES_DIR / "virtual_machines" / "vm_open_ssh_public.tf"

    with patch(
        "app.api.routes.generate_explanation",
        return_value="explicación simulada del LLM",
    ):
        _, payload = _scan([tf_path])

    assert payload["findings"], "se esperaba al menos un hallazgo priorizado"

    scores = [f["contextual_score"] for f in payload["findings"]]
    assert scores == sorted(scores, reverse=True)

    for item in payload["findings"]:
        assert item["explanation"] == "explicación simulada del LLM"
        assert 0 <= item["contextual_score"] <= 100

    nsg_findings = [
        f for f in payload["findings"] if f["finding"]["resource_type"] == "azurerm_network_security_group"
    ]
    assert all(f["context"]["publicly_exposed"] for f in nsg_findings)


def test_scan_degrades_gracefully_when_llm_unavailable(seeded_chromadb):
    tf_path = IAC_FIXTURES_DIR / "keyvault" / "keyvault_public_network_no_firewall.tf"

    with patch(
        "app.api.routes.generate_explanation",
        side_effect=ConnectionError("Ollama no accesible"),
    ):
        _, payload = _scan([tf_path])

    assert payload["findings"]
    for item in payload["findings"]:
        assert "[Explicación automática no disponible]" in item["explanation"]

    assert any("Ollama" in warning for warning in payload["warnings"])
    # El warning de degradación se reporta una sola vez, no por cada hallazgo.
    ollama_warnings = [w for w in payload["warnings"] if "Ollama" in w]
    assert len(ollama_warnings) == 1


def test_scan_reports_warning_when_trivy_unavailable(seeded_chromadb):
    tf_path = IAC_FIXTURES_DIR / "keyvault" / "keyvault_purge_protection_disabled.tf"

    with (
        patch("app.api.routes.scan_with_trivy", side_effect=RuntimeError("binario no encontrado")),
        patch("app.api.routes.generate_explanation", return_value="explicación simulada"),
    ):
        _, payload = _scan([tf_path])

    assert payload["findings"]
    assert any("trivy no disponible" in warning for warning in payload["warnings"])


def test_scan_falls_back_to_neutral_context_when_resource_not_resolved():
    tf_path = IAC_FIXTURES_DIR / "keyvault" / "keyvault_purge_protection_disabled.tf"

    with (
        patch(
            "app.api.routes.extract_resource_context",
            side_effect=ValueError("recurso no encontrado"),
        ),
        patch("app.api.routes.generate_explanation", return_value="explicación simulada"),
    ):
        _, payload = _scan([tf_path])

    assert payload["findings"]
    for item in payload["findings"]:
        assert item["context"] == {
            "resource_name": item["finding"]["resource_name"],
            "publicly_exposed": False,
            "network_isolated": False,
            "has_compensating_controls": False,
        }
    assert any("contexto de red" in warning for warning in payload["warnings"])


def test_scan_reports_warning_when_vector_store_unavailable():
    tf_path = IAC_FIXTURES_DIR / "keyvault" / "keyvault_purge_protection_disabled.tf"

    with (
        patch(
            "app.api.routes.query_relevant_guidelines",
            side_effect=RuntimeError("ChromaDB no disponible"),
        ),
        patch("app.api.routes.generate_explanation", return_value="explicación simulada"),
    ):
        _, payload = _scan([tf_path])

    assert payload["findings"]
    warnings = [w for w in payload["warnings"] if "base de conocimiento vectorial" in w]
    assert len(warnings) == 1


def test_scan_emits_error_event_when_checkov_fails_unexpectedly():
    tf_path = IAC_FIXTURES_DIR / "keyvault" / "keyvault_purge_protection_disabled.tf"

    with patch("app.api.routes.scan_with_checkov", side_effect=RuntimeError("fallo inesperado")):
        response = _upload([tf_path])

    assert response.status_code == 200
    events = [json.loads(line) for line in response.text.splitlines() if line.strip()]

    assert events[-1]["type"] == "error"
    assert "fallo inesperado" in events[-1]["message"]
