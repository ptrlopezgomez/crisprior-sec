import requests
import streamlit as st

from components.api_client import BACKEND_URL, scan_files

st.set_page_config(
    page_title="Priorización Contextual de Riesgos IaC",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Priorización Contextual de Riesgos de Seguridad en Terraform")
st.markdown(
    """
    Carga tus archivos Terraform (`.tf`) para obtener un baseline de Checkov/tfsec
    reordenado según el contexto real de exposición de red y los controles
    compensatorios presentes, con explicaciones generadas por un LLM local.

    Usa el menú lateral para navegar al **Dashboard** una vez completado el análisis.
    """
)

uploaded_files = st.file_uploader(
    "Archivos Terraform (.tf)", type=["tf"], accept_multiple_files=True
)

if uploaded_files and st.button("Analizar", type="primary"):
    progress_bar = st.progress(0.0, text="Ejecutando Checkov/tfsec...")
    status_text = st.empty()

    def _on_progress(event: dict) -> None:
        if event["type"] == "start":
            total = event["total"]
            if total == 0:
                progress_bar.progress(1.0, text="Sin hallazgos que analizar.")
            else:
                status_text.info(f"Se detectaron {total} hallazgo(s). Generando explicaciones...")
        elif event["type"] == "progress":
            current, total = event["current"], event["total"]
            progress_bar.progress(
                current / total,
                text=f"Analizando hallazgo {current}/{total}: {event['check_id']} ({event['resource']})",
            )

    try:
        result = scan_files(uploaded_files, on_progress=_on_progress)
    except requests.exceptions.HTTPError as exc:
        detail = exc.response.json().get("detail", str(exc)) if exc.response is not None else str(exc)
        st.error(f"El backend rechazó el análisis: {detail}")
    except requests.exceptions.RequestException as exc:
        st.error(f"No se pudo conectar con el backend ({BACKEND_URL}): {exc}")
    except RuntimeError as exc:
        st.error(f"El análisis falló: {exc}")
    else:
        progress_bar.progress(1.0, text="Análisis completado")
        status_text.empty()
        st.session_state["scan_result"] = result
        st.success(
            f"Análisis completado: {len(result['findings'])} hallazgo(s) priorizado(s). "
            "Ve al **Dashboard** en el menú lateral para revisarlos."
        )
        for warning in result.get("warnings", []):
            st.warning(warning)
