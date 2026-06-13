"""
PLANTILLA — Otras exploraciones.

Esta carpeta es para cualquier gráfica que no encaje en mapas, series de
tiempo o correlaciones: distribuciones, conteos, tablas, lo que sea.

Copia este archivo a uno nuevo con tu nombre en esta misma carpeta
(deja este ejemplo intacto como referencia),
ej. `otros/pablo_categorias_denue.py`, y modifícalo.
"""

import plotly.express as px
import streamlit as st

TITULO = "Ejemplo: Distribución de establecimientos DENUE"
AUTOR = "Plantilla"
DESCRIPCION = "Conteo de establecimientos por categoría (DENUE)."


def render(data: dict) -> None:
    denue = data["denue"]

    df = denue["categoria"].value_counts().reset_index()
    df.columns = ["categoria", "establecimientos"]

    fig = px.pie(df, names="categoria", values="establecimientos",
                  title="Establecimientos DENUE por categoría")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True, hide_index=True)
