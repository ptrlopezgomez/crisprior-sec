# Arquitectura del Sistema (Cap. 5.1)

> Completar con el diagrama de componentes desacoplados en Python durante el Sprint 1-2.

## Flujo de datos (alto nivel)

1. El usuario carga su directorio Terraform en el frontend (Streamlit).
2. El backend (FastAPI) extrae el AST de los archivos `.tf` y construye el grafo de red.
3. Se ejecutan Checkov y tfsec para obtener el baseline de hallazgos.
4. El motor de contexto (`app/engine`) enriquece cada hallazgo con variables
   operacionales (exposición pública, aislamiento de red, controles compensatorios).
5. Se consulta la base vectorial (ChromaDB) para recuperar directrices relevantes
   vía similitud semántica.
6. El LLM local (Ollama) genera la explicación en prosa.
7. El dashboard (Streamlit) muestra los hallazgos reordenados por riesgo contextual.

## Componentes

| Componente | Responsabilidad | Ubicación |
| --- | --- | --- |
| API | Exponer endpoints REST | `backend/app/api` |
| Scanners | Integración Checkov/tfsec | `backend/app/scanners` |
| Engine | Contexto de red + priorización | `backend/app/engine` |
| LLM | Generación de explicaciones | `backend/app/llm` |
| Dashboard | Interfaz de usuario | `frontend/` |
