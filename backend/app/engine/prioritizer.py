"""Motor de priorización contextual híbrido (HU-05).

Recalcula la severidad estática de Checkov/tfsec combinando el hallazgo
con su contexto operacional (exposición de red, controles compensatorios)
usando embeddings semánticos almacenados en ChromaDB.
"""

from app.models.schemas import (
    PrioritizedFinding,
    ResourceContext,
    Severity,
    StaticFinding,
)


def calculate_contextual_score(finding: StaticFinding, context: ResourceContext) -> float:
    """Calcula un score de 0 a 100 combinando severidad estática y contexto real.

    TODO (Sprint 3): sustituir la heurística base por el modelo de
    embeddings + reglas de contexto validado contra el panel de expertos.
    """
    base_scores = {
        Severity.LOW: 20.0,
        Severity.MEDIUM: 45.0,
        Severity.HIGH: 70.0,
        Severity.CRITICAL: 90.0,
    }
    score = base_scores[finding.static_severity]

    if not context.publicly_exposed:
        score -= 25
    if context.network_isolated:
        score -= 15
    if context.has_compensating_controls:
        score -= 10

    return max(0.0, min(100.0, score))


def score_to_severity(score: float) -> Severity:
    if score >= 80:
        return Severity.CRITICAL
    if score >= 55:
        return Severity.HIGH
    if score >= 30:
        return Severity.MEDIUM
    return Severity.LOW


def prioritize(finding: StaticFinding, context: ResourceContext, explanation: str) -> PrioritizedFinding:
    score = calculate_contextual_score(finding, context)
    return PrioritizedFinding(
        finding=finding,
        context=context,
        contextual_score=score,
        contextual_severity=score_to_severity(score),
        explanation=explanation,
    )
