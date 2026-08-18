# Sistema Inteligente para Priorización Contextual de Riesgos de Seguridad en Infraestructura Cloud con Terraform

Framework híbrido de segundo nivel que enriquece los hallazgos de analizadores estáticos de IaC (Checkov, tfsec) con análisis de contexto de red y explicaciones en lenguaje natural, para reducir la fatiga por alertas en flujos DevSecOps sobre Microsoft Azure.

**Grupo 3012G** — Seminario de Innovación en Inteligencia Artificial, UNIR.

## Alcance

- Proveedor: Microsoft Azure
- Servicios cubiertos: Virtual Machines, Storage, Key Vault, App Service
- Analizadores base: Checkov, tfsec
- Motor de contexto: embeddings (Sentence Transformers) + ChromaDB
- Generación de explicaciones: LLM local vía Ollama (Mistral-7B / Llama 3)

## Estructura del repositorio

```
backend/          FastAPI: API, motor de priorización, integración LLM y scanners
frontend/         Streamlit: dashboard interactivo
iac_fixtures/     50 archivos Terraform de prueba con fallas conocidas (protocolo de validación)
chromadb/         Scripts de inicialización de la base de datos vectorial
docs/             Entregables del TFM y documentación de soporte
scripts/          Utilidades de setup y CI
.github/workflows/ Pipelines de CI (lint, tests, escaneo IaC)
```

## Requisitos previos

- Python 3.11+
- [Ollama](https://ollama.com) instalado localmente con el modelo `mistral` descargado
- Checkov y tfsec instalados (`pip install checkov`, ver [tfsec docs](https://aquasecurity.github.io/tfsec/))

## Puesta en marcha

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (en otra terminal)
cd frontend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Equipo (Grupo 3012G)

| Integrante | Rol |
| --- | --- |
| López Barrón, Carlos Iván | Product Owner / IA |
| López Gómez, Pedro Manuel | Scrum Master / Frontend |
| Monterroza Barrios, Rafael Enrique | Dev / DevSecOps |
| Sánchez Galicia, Enrique Cheny | Dev / DevSecOps |
| Zerón Hernández, Alejandro Raúl | Dev / DevSecOps |

## Metodología

Scrum con sprints quincenales. Ver `docs/` para el Product Backlog, Definition of Ready/Done y protocolo de validación experimental.
