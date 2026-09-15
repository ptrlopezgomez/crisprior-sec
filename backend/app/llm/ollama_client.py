"""Cliente para generar explicaciones en prosa vía LLM local con Ollama (HU-06)."""

import ollama

from app.core.config import settings
from app.models.schemas import PrioritizedFinding

_PROMPT_TEMPLATE = """Eres un asistente experto en seguridad de infraestructura cloud (DevSecOps).
Explica en un párrafo breve, en castellano, por qué el siguiente hallazgo tiene la
severidad contextual calculada y qué acción concreta de remediación recomiendas.

Hallazgo: {check_id} - {description}
Recurso: {resource_name} ({resource_type})
Severidad estática original: {static_severity}
Severidad contextual recalculada: {contextual_severity} (score {score}/100)
Expuesto públicamente: {publicly_exposed}
Aislado de red: {network_isolated}
Controles compensatorios presentes: {has_compensating_controls}
{guidelines_section}"""


def generate_explanation(
    finding,
    context,
    contextual_score: float,
    contextual_severity,
    guidelines: list[str] | None = None,
) -> str:
    guidelines_section = ""
    if guidelines:
        bullet_points = "\n".join(f"- {guideline}" for guideline in guidelines)
        guidelines_section = f"\nDirectrices de seguridad relevantes (base de conocimiento):\n{bullet_points}\n"

    prompt = _PROMPT_TEMPLATE.format(
        check_id=finding.check_id,
        description=finding.description,
        resource_name=finding.resource_name,
        resource_type=finding.resource_type,
        static_severity=finding.static_severity.value,
        contextual_severity=contextual_severity.value,
        score=round(contextual_score, 1),
        publicly_exposed=context.publicly_exposed,
        network_isolated=context.network_isolated,
        has_compensating_controls=context.has_compensating_controls,
        guidelines_section=guidelines_section,
    )

    response = ollama.chat(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]
