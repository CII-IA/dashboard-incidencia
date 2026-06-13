"""
PLANTILLA — Mapas y geografía.

Copia este archivo a uno nuevo con tu nombre en esta misma carpeta
(deja este ejemplo intacto como referencia),
ej. `mapas/ana_mapa_calor_robos.py`, y modifícalo.

NOTA de rendimiento: el dataset real tiene ~600k incidentes. Graficar punto
por punto satura memoria (Plotly serializa TODOS los puntos al navegador).
Por eso este ejemplo AGREGA por celda H3 antes de dibujar: el mapa muestra
~16k celdas con su conteo, no 600k puntos. Replica este patrón en tus mapas.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

TITULO = "Ejemplo: Mapa de calor de incidentes (agregado por celda H3)"
AUTOR = "Plantilla"
DESCRIPCION = (
    "Densidad espacial de incidentes agregada por celda H3, filtrable por "
    "tipo de delito. Úsalo como base para mapas de calor, choropleths, etc."
)


@st.cache_data(show_spinner="Agregando incidentes por celda...")
def _agregar_por_celda(incidentes: pd.DataFrame, delitos: tuple) -> pd.DataFrame:
    df = incidentes.dropna(subset=["x", "y"])
    if delitos:
        df = df[df["delito"].isin(delitos)]
    if df.empty:
        return df
    if "h3_9" in df.columns:
        df = df.dropna(subset=["h3_9"])
        agg = df.groupby("h3_9").agg(
            incidentes=("delito", "size"),
            lat=("y", "mean"),
            lon=("x", "mean"),
        ).reset_index()
    else:
        # Sin H3: agrupar redondeando coordenadas (~malla) para no mandar
        # cientos de miles de puntos al navegador.
        g = df.assign(lat=df["y"].round(3), lon=df["x"].round(3))
        agg = g.groupby(["lat", "lon"]).size().rename("incidentes").reset_index()
    return agg


def render(data: dict) -> None:
    incidentes = data["incidentes"]

    delitos_sel = st.multiselect(
        "Filtrar por delito (opcional)",
        sorted(incidentes["delito"].dropna().unique()),
        default=[],
        key="mapas_ejemplo_delito",
    )

    agg = _agregar_por_celda(incidentes, tuple(delitos_sel))

    if agg.empty:
        st.warning("No hay datos con coordenadas para esa selección.")
        return

    st.caption(f"{len(agg):,} celdas · {int(agg['incidentes'].sum()):,} incidentes")

    fig = px.density_mapbox(
        agg, lat="lat", lon="lon", z="incidentes", radius=12,
        center=dict(lat=agg["lat"].mean(), lon=agg["lon"].mean()),
        zoom=8, mapbox_style="open-street-map", height=600,
        hover_data={"incidentes": True, "lat": False, "lon": False},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
