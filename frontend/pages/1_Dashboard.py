import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard de Riesgos", page_icon="📊", layout="wide")

st.title("📊 Dashboard de Riesgos Priorizados")
st.markdown(
    "Cuadro de mando con las alertas reordenadas por riesgo contextual "
    "y su respectivo informe explicativo de remediación (HU-07)."
)

scan_result = st.session_state.get("scan_result")

if not scan_result:
    st.info(
        "Todavía no hay resultados. Carga tus archivos Terraform en la página "
        "principal y ejecuta el análisis."
    )
else:
    for warning in scan_result.get("warnings", []):
        st.warning(warning)

    findings = scan_result.get("findings", [])
    if not findings:
        st.success("No se encontraron hallazgos en los archivos analizados.")
    else:
        table_rows = [
            {
                "Check": f["finding"]["check_id"],
                "Recurso": f"{f['finding']['resource_type']}.{f['finding']['resource_name']}",
                "Severidad estática": f["finding"]["static_severity"],
                "Severidad contextual": f["contextual_severity"],
                "Score": round(f["contextual_score"], 1),
                "Expuesto": f["context"]["publicly_exposed"],
                "Aislado": f["context"]["network_isolated"],
                "Controles compensatorios": f["context"]["has_compensating_controls"],
                "Herramienta": f["finding"]["source_tool"],
            }
            for f in findings
        ]
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.subheader("Explicaciones de remediación")
        for f in findings:
            resource = f"{f['finding']['resource_type']}.{f['finding']['resource_name']}"
            title = (
                f"{f['finding']['check_id']} · {resource} · "
                f"{f['contextual_severity'].upper()} ({f['contextual_score']:.0f}/100)"
            )
            with st.expander(title):
                st.write(f["explanation"])
