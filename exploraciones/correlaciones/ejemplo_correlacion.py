"""
PLANTILLA — Correlaciones.

Copia este archivo a uno nuevo con tu nombre en esta misma carpeta
(deja este ejemplo intacto como referencia),
ej. `correlaciones/diana_alumbrado_vs_robos.py`, y modifícalo.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

TITULO = "Ejemplo: Variable de contexto vs. incidentes por celda H3"
AUTOR = "Plantilla"
DESCRIPCION = (
    "Cruza una variable de contexto de la celda H3 (infraestructura urbana "
    "INV o conteo de POIs DENUE) contra el número de incidentes en esa misma "
    "celda. Úsalo como base para explorar qué factores acompañan a la "
    "incidencia delictiva."
)


@st.cache_data(show_spinner="Cruzando incidentes con contexto H3...")
def _perfil_por_celda(incidentes: pd.DataFrame, h3_vars: pd.DataFrame) -> pd.DataFrame:
    conteo = (
        incidentes.dropna(subset=["h3_9"])
        .groupby("h3_9").size()
        .rename("n_incidentes")
        .reset_index()
    )
    perfil = h3_vars.merge(conteo, on="h3_9", how="left")
    perfil["n_incidentes"] = perfil["n_incidentes"].fillna(0)
    return perfil


def render(data: dict) -> None:
    incidentes = data["incidentes"]
    h3_vars = data["h3_vars"]

    if "h3_9" not in incidentes.columns:
        st.warning("Los incidentes no traen columna `h3_9`; no se puede cruzar por celda.")
        return

    perfil = _perfil_por_celda(incidentes, h3_vars)

    numeric_cols = [
        c for c in perfil.columns
        if c not in ("h3_9", "n_incidentes")
        and pd.api.types.is_numeric_dtype(perfil[c])
    ]
    if not numeric_cols:
        st.info("`contexto_h3` no tiene variables numéricas para comparar.")
        return

    # Sugerir una variable interesante por defecto si existe
    default = "poi_bares" if "poi_bares" in numeric_cols else numeric_cols[0]
    var_x = st.selectbox(
        "Variable de contexto (celda H3)", numeric_cols,
        index=numeric_cols.index(default), key="corr_ejemplo_var",
    )

    solo_activas = st.checkbox(
        "Solo celdas con ≥1 incidente", value=False, key="corr_ejemplo_activas"
    )
    df = perfil[perfil["n_incidentes"] > 0] if solo_activas else perfil

    fig = px.scatter(
        df, x=var_x, y="n_incidentes",
        hover_data=["h3_9"],
        trendline="ols",
        opacity=0.5,
        title=f"Incidentes por celda H3 vs. {var_x}",
    )
    st.plotly_chart(fig, use_container_width=True)
