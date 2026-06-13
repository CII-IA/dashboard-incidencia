"""
PLANTILLA — Series de tiempo.

Copia este archivo a uno nuevo con tu nombre en esta misma carpeta
(deja este ejemplo intacto como referencia),
ej. `series_tiempo/luis_tendencia_robos.py`, y modifícalo.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

TITULO = "Ejemplo: Tendencia de incidentes en el tiempo"
AUTOR = "Plantilla"
DESCRIPCION = (
    "Evolución temporal de incidentes con agregación configurable. "
    "Úsalo como base para cualquier análisis de series de tiempo."
)


def render(data: dict) -> None:
    incidentes = data["incidentes"]

    freq_label = st.radio(
        "Agregación", ["Diaria", "Semanal", "Mensual"], index=2,
        horizontal=True, key="series_ejemplo_freq",
    )
    freq = {"Diaria": "D", "Semanal": "W", "Mensual": "MS"}[freq_label]

    serie = (
        incidentes.set_index("fecha")
        .resample(freq)
        .size()
        .rename("incidentes")
        .reset_index()
    )

    fig = px.line(serie, x="fecha", y="incidentes", title=f"Incidentes ({freq_label.lower()})")
    st.plotly_chart(fig, use_container_width=True)
