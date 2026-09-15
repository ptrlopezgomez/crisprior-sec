import json
import shutil
from pathlib import Path

import pytest

from app.engine.context_extractor import extract_resource_context

IAC_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "iac_fixtures"


def _load_fixture_cases():
    cases = []
    for expected_path in sorted(IAC_FIXTURES_DIR.glob("*/*.expected.json")):
        tf_path = expected_path.with_name(expected_path.name.removesuffix(".expected.json") + ".tf")
        expected = json.loads(expected_path.read_text())
        resource_type, _, resource_name = expected["resource_name"].partition(".")
        cases.append(
            pytest.param(
                tf_path,
                resource_type,
                resource_name,
                expected["context"],
                id=expected_path.stem,
            )
        )
    return cases


@pytest.mark.parametrize("tf_path,resource_type,resource_name,expected_context", _load_fixture_cases())
def test_extract_resource_context_matches_gold_standard(
    tmp_path, tf_path, resource_type, resource_name, expected_context
):
    # Cada fixture es un escenario independiente (HU-08); se copia de forma
    # aislada para que el grafo de recursos no mezcle NSGs/VMs de fixtures
    # vecinos que solo comparten carpeta por convención de nombrado.
    shutil.copy(tf_path, tmp_path)

    context = extract_resource_context(tmp_path, resource_type, resource_name)

    assert context.publicly_exposed == expected_context["publicly_exposed"]
    assert context.network_isolated == expected_context["network_isolated"]
    assert context.has_compensating_controls == expected_context["has_compensating_controls"]


def test_extract_resource_context_raises_for_unknown_resource(tmp_path):
    shutil.copy(IAC_FIXTURES_DIR / "storage" / "storage_public_no_controls.tf", tmp_path)

    with pytest.raises(ValueError):
        extract_resource_context(tmp_path, "azurerm_storage_account", "does_not_exist")
