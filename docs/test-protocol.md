# Protocolo de Pruebas y Baseline (Cap. 6.1)

## Dataset

50 archivos Terraform (`iac_fixtures/`) con fallas conocidas en Virtual Machines,
Storage, Key Vault y App Service, cada uno con un `.expected.json` anotado por el
panel de expertos DevSecOps ("gold standard").

## Métricas

| KPI | Métrica | Umbral mínimo |
| --- | --- | --- |
| Técnico | Correlación de Spearman (ρ) vs. panel de expertos | ρ ≥ 0.80 |
| Técnico | F1-Score de clasificación | ≥ 0.85 |
| Técnico | Latencia de inferencia (FastAPI) | < 200 ms/archivo |
| Operacional | Reducción de fatiga por alertas | ≥ 30% |
| Negocio | Satisfacción (encuesta Likert 1-5) | ≥ 4.0/5.0 |

## Procedimiento

1. Ejecutar Checkov y tfsec sobre `iac_fixtures/` para obtener el baseline estático.
2. Ejecutar el motor de priorización contextual sobre el mismo conjunto.
3. Comparar la severidad contextual calculada contra `gold_contextual_severity`
   de cada fixture.
4. Calcular ρ de Spearman y F1-Score.
5. Registrar resultados en este documento por cada Sprint Review.
