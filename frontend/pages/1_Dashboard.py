import streamlit as st

st.set_page_config(page_title="Dashboard de Riesgos", page_icon="📊", layout="wide")

st.title("📊 Dashboard de Riesgos Priorizados")
st.markdown(
    "Cuadro de mando con las alertas reordenadas por riesgo contextual "
    "y su respectivo informe explicativo de remediación (HU-07)."
)

st.info("Pendiente de conexión con el endpoint `/api/v1/scan` del backend.")
