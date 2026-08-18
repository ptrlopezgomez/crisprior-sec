import streamlit as st

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

if uploaded_files:
    st.info(f"{len(uploaded_files)} archivo(s) cargado(s). Integración con el backend pendiente (HU-01).")
