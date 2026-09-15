import pytest

from app.engine.prioritizer import calculate_contextual_score, prioritize, score_to_severity
from app.models.schemas import ResourceContext, Severity, StaticFinding

EXPOSED_CONTEXT = ResourceContext(
    resource_name="example",
    publicly_exposed=True,
    network_isolated=False,
    has_compensating_controls=False,
)

MITIGATED_CONTEXT = ResourceContext(
    resource_name="example",
    publicly_exposed=False,
    network_isolated=True,
    has_compensating_controls=True,
)


def _finding(severity: Severity) -> StaticFinding:
    return StaticFinding(
        check_id="CKV_TEST_1",
        resource_type="azurerm_storage_account",
        resource_name="example",
        file_path="main.tf",
        line_range=(1, 5),
        static_severity=severity,
        source_tool="checkov",
        description="hallazgo de prueba",
    )


@pytest.mark.parametrize(
    "severity,expected_base",
    [
        (Severity.LOW, 20.0),
        (Severity.MEDIUM, 45.0),
        (Severity.HIGH, 70.0),
        (Severity.CRITICAL, 90.0),
    ],
)
def test_calculate_contextual_score_base_severity_with_exposed_context(severity, expected_base):
    score = calculate_contextual_score(_finding(severity), EXPOSED_CONTEXT)

    assert score == expected_base


def test_calculate_contextual_score_reduces_for_mitigating_context():
    score = calculate_contextual_score(_finding(Severity.CRITICAL), MITIGATED_CONTEXT)

    # 90 base - 25 (no expuesto) - 15 (aislado) - 10 (controles compensatorios)
    assert score == 40.0


def test_calculate_contextual_score_is_clamped_to_zero():
    score = calculate_contextual_score(_finding(Severity.LOW), MITIGATED_CONTEXT)

    assert score == 0.0


@pytest.mark.parametrize(
    "score,expected_severity",
    [
        (0.0, Severity.LOW),
        (29.9, Severity.LOW),
        (30.0, Severity.MEDIUM),
        (54.9, Severity.MEDIUM),
        (55.0, Severity.HIGH),
        (79.9, Severity.HIGH),
        (80.0, Severity.CRITICAL),
        (100.0, Severity.CRITICAL),
    ],
)
def test_score_to_severity_thresholds(score, expected_severity):
    assert score_to_severity(score) == expected_severity


def test_prioritize_builds_prioritized_finding_with_explanation():
    finding = _finding(Severity.HIGH)
    result = prioritize(finding, EXPOSED_CONTEXT, "explicación de prueba")

    assert result.finding == finding
    assert result.context == EXPOSED_CONTEXT
    assert result.contextual_score == 70.0
    assert result.contextual_severity == Severity.HIGH
    assert result.explanation == "explicación de prueba"
