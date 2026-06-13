"""
Auto-descubrimiento de exploraciones.

Cada pasante agrega un archivo .py dentro de `exploraciones/<categoria>/`.
Ese archivo debe definir:

    TITULO = "Nombre corto de la gráfica"
    AUTOR  = "Nombre del pasante"            (opcional)
    DESCRIPCION = "Qué muestra esta gráfica"  (opcional)

    def render(data: dict) -> None:
        ...  # usa st.* para dibujar, recibe data["incidentes"], etc.

Este módulo escanea las carpetas de `exploraciones/`, importa cada archivo
y construye un diccionario {categoria: [exploraciones...]} para que `app.py`
las muestre sin que nadie tenga que registrar nada a mano.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

EXPLORACIONES_DIR = Path(__file__).resolve().parent.parent / "exploraciones"

# Nombres "bonitos" para las categorías (= nombres de carpeta)
CATEGORIA_LABELS = {
    "mapas": "🗺️ Mapas y geografía",
    "series_tiempo": "📈 Series de tiempo",
    "correlaciones": "🔗 Correlaciones",
    "otros": "🧪 Otras exploraciones",
}


@dataclass
class Exploracion:
    titulo: str
    autor: str
    descripcion: str
    render: callable
    archivo: str


def _cargar_modulo(path: Path):
    mod_name = f"exploraciones_dyn_{path.stem}_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


def descubrir_exploraciones() -> dict[str, list[Exploracion]]:
    resultado: dict[str, list[Exploracion]] = {}

    if not EXPLORACIONES_DIR.exists():
        return resultado

    for categoria_dir in sorted(EXPLORACIONES_DIR.iterdir()):
        if not categoria_dir.is_dir() or categoria_dir.name.startswith("_"):
            continue

        exploraciones = []
        for archivo in sorted(categoria_dir.glob("*.py")):
            if archivo.name.startswith("__"):
                continue
            try:
                module = _cargar_modulo(archivo)
            except Exception as e:
                exploraciones.append(Exploracion(
                    titulo=f"⚠️ Error en {archivo.name}",
                    autor="",
                    descripcion=str(e),
                    render=lambda data, _e=e: _mostrar_error(_e),
                    archivo=archivo.name,
                ))
                continue

            if not hasattr(module, "render"):
                continue

            exploraciones.append(Exploracion(
                titulo=getattr(module, "TITULO", archivo.stem),
                autor=getattr(module, "AUTOR", ""),
                descripcion=getattr(module, "DESCRIPCION", ""),
                render=module.render,
                archivo=archivo.name,
            ))

        if exploraciones:
            resultado[categoria_dir.name] = exploraciones

    return resultado


def _mostrar_error(e: Exception):
    import streamlit as st
    st.error(f"Esta exploración tiene un error y no se pudo cargar:\n\n```\n{e}\n```")
