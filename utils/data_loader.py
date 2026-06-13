"""
Carga estandarizada de datos para todas las exploraciones.

Todas las exploraciones reciben los mismos DataFrames a través de un solo
diccionario `data`, para que no importe quién escribió cada gráfica: todas
hablan el mismo "idioma" de columnas.

Si existen archivos reales en /data, se usan esos. Si no, se generan datos
DUMMY con el mismo esquema, para que cualquiera pueda desarrollar y probar
su exploración sin esperar a tener los datos reales.

Archivos reales esperados en /data (cualquiera puede faltar):
    - incidentes_delictivos.parquet  (o .csv)   <- salida de iieg_pipeline.py
        columnas: fecha, delito, x, y, colonia, municipio,
                  clave_mun, hora, bien_afectado, zona_geografica, region, h3_9
    - contexto_h3.parquet (o .csv)   <- variables por celda H3 (res 9)
        columnas mínimas: h3_9 + variables numéricas de contexto
          (infraestructura inv_*  y conteos de POIs poi_*)
    - denue_jalisco.parquet (o .csv) <- establecimientos DENUE
        columnas mínimas: categoria  (+ h3_9 si está disponible)

Unidad espacial del proyecto: celda H3 resolución 9 (~0.1 km²). Los
incidentes traen `h3_9`, lo que permite cruzarlos con `contexto_h3` sin
necesidad de geometría externa.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SEED = 42

REGIONES_JALISCO = {
    "Centro": ["Guadalajara", "Zapopan", "Tlaquepaque", "Tonalá", "El Salto"],
    "Altos Norte": ["Lagos de Moreno", "Encarnación de Díaz"],
    "Altos Sur": ["Tepatitlán de Morelos", "Arandas"],
    "Cienega": ["Ocotlán", "La Barca"],
    "Sureste": ["Tamazula de Gordiano", "Zapotlán el Grande"],
    "Sur": ["Ciudad Guzmán", "Sayula"],
    "Sierra de Amula": ["Tecolotlán", "El Limón"],
    "Costa Sur": ["Autlán de Navarro", "Casimiro Castillo"],
    "Costa Sierra Occidental": ["Puerto Vallarta", "Cabo Corrientes"],
    "Norte": ["Colotlán", "Bolaños"],
    "Valles": ["Ameca", "Tequila"],
    "Lagunas": ["Atotonilco el Alto"],
}
DELITOS = [
    "Robo a vehículo particular", "Robo a casa habitación", "Robo a negocio",
    "Robo a transeúnte", "Violencia familiar", "Homicidio doloso",
    "Lesiones dolosas", "Robo de autopartes", "Fraude", "Extorsión",
]
DENUE_CATEGORIAS = [
    "Bares y cantinas", "Tiendas de conveniencia", "Servicios de salud",
    "Gasolineras", "Escuelas", "Bancos y cajeros", "Mercados", "Hoteles",
    "Farmacias",
]
# Variables de contexto por celda H3 (mismas familias que el proyecto real)
INV_VARS = [
    "inv_banqueta_pct", "inv_alumpub_pct", "inv_drenajep_pct",
    "inv_transcol_pct", "inv_arboles_pct", "inv_guarnici_pct",
]
POI_VARS = [f"poi_{g.split()[0].lower()}" for g in
            ["bancos", "bares", "escuelas", "salud", "conveniencia",
             "hoteles", "gasolineras", "mercados", "farmacias"]]

CENTER_X, CENTER_Y = -103.3496, 20.6597
N_DUMMY_CELLS = 400


def _read_any(name: str) -> pd.DataFrame | None:
    for ext, reader in ((".parquet", pd.read_parquet), (".csv", pd.read_csv)):
        path = DATA_DIR / f"{name}{ext}"
        if path.exists():
            return reader(path)
    return None


def _skewed_weights(k: int, rng: np.random.Generator) -> np.ndarray:
    raw = rng.exponential(scale=1.0, size=k)
    return raw / raw.sum()


def _dummy_h3_ids(rng: np.random.Generator, n: int) -> np.ndarray:
    """IDs H3 sintéticos, estables, compartidos entre incidentes y contexto."""
    return np.array([f"89dummy{i:05d}fff" for i in range(n)])


@st.cache_data(show_spinner=False)
def _dummy_incidentes() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    n = 8000
    fechas = pd.date_range("2023-01-01", "2025-12-31", freq="D")
    region_list = list(REGIONES_JALISCO.keys())
    regiones = rng.choice(region_list, size=n, p=_skewed_weights(len(region_list), rng))
    municipios = [rng.choice(REGIONES_JALISCO[r]) for r in regiones]
    cells = _dummy_h3_ids(rng, N_DUMMY_CELLS)
    return pd.DataFrame({
        "fecha": rng.choice(fechas, size=n),
        "delito": rng.choice(DELITOS, size=n, p=_skewed_weights(len(DELITOS), rng)),
        "x": CENTER_X + rng.normal(0, 0.25, n),
        "y": CENTER_Y + rng.normal(0, 0.25, n),
        "colonia": rng.choice(
            ["Centro", "Las Águilas", "Providencia", "Oblatos",
             "Tlaquepaque Centro", "Santa Tere", "Zona Industrial",
             "Chapalita", "Miravalle", "El Sauz"], size=n),
        "municipio": municipios,
        "clave_mun": [str(rng.integers(1, 125)).zfill(3) for _ in range(n)],
        "hora": rng.integers(0, 24, n),
        "bien_afectado": rng.choice(
            ["Vehículo", "Dinero", "Autopartes", "Electrónicos", "No aplica"], size=n),
        "zona_geografica": rng.choice(["Urbana", "Rural"], size=n, p=[0.85, 0.15]),
        "region": regiones,
        # Las celdas más cargadas concentran más incidentes (señal para correlaciones)
        "h3_9": rng.choice(cells, size=n, p=_skewed_weights(N_DUMMY_CELLS, rng)),
    })


@st.cache_data(show_spinner=False)
def _dummy_contexto_h3() -> pd.DataFrame:
    rng = np.random.default_rng(SEED + 1)
    cells = _dummy_h3_ids(rng, N_DUMMY_CELLS)
    out = {"h3_9": cells}
    for v in INV_VARS:
        out[v] = rng.uniform(0, 1, N_DUMMY_CELLS)
    for v in POI_VARS:
        out[v] = rng.poisson(rng.uniform(0.3, 4.0), N_DUMMY_CELLS).astype(float)
    df = pd.DataFrame(out)
    df["poi_total"] = df[POI_VARS].sum(axis=1)
    return df


@st.cache_data(show_spinner=False)
def _dummy_denue() -> pd.DataFrame:
    rng = np.random.default_rng(SEED + 2)
    n = 3000
    cells = _dummy_h3_ids(rng, N_DUMMY_CELLS)
    return pd.DataFrame({
        "h3_9": rng.choice(cells, size=n),
        "categoria": rng.choice(
            DENUE_CATEGORIAS, size=n, p=_skewed_weights(len(DENUE_CATEGORIAS), rng)),
    })


@st.cache_data(show_spinner=False)
def load_data() -> dict:
    """Devuelve el diccionario estándar de datos para todas las exploraciones.

    Returns
    -------
    dict con llaves:
        "incidentes": DataFrame de incidentes delictivos (incluye `h3_9`)
        "h3_vars":    DataFrame de variables de contexto por celda H3
        "denue":      DataFrame de establecimientos DENUE (incluye `categoria`)
        "is_dummy":   dict {nombre: bool} indicando si cada tabla es dummy
    """
    incidentes = _read_any("incidentes_delictivos")
    h3_vars = _read_any("contexto_h3")
    denue = _read_any("denue_jalisco")

    is_dummy = {
        "incidentes": incidentes is None,
        "h3_vars": h3_vars is None,
        "denue": denue is None,
    }

    if incidentes is None:
        incidentes = _dummy_incidentes()
    else:
        incidentes["fecha"] = pd.to_datetime(incidentes["fecha"], errors="coerce")

    if h3_vars is None:
        h3_vars = _dummy_contexto_h3()

    if denue is None:
        denue = _dummy_denue()

    return {
        "incidentes": incidentes,
        "h3_vars": h3_vars,
        "denue": denue,
        "is_dummy": is_dummy,
    }
