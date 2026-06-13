import streamlit as st
from utils.data_loader import load_data
from utils.registry import descubrir_exploraciones, CATEGORIA_LABELS

st.set_page_config(
    page_title="Incidencia Delictiva Jalisco",
    page_icon="🗺️",
    layout="wide",
)

st.title("🗺️ Exploración de datos — Incidencia Delictiva en Jalisco")

data = load_data()

dummy_activos = [k for k, v in data["is_dummy"].items() if v]
if dummy_activos:
    st.warning(
        f"⚠️ Usando datos **dummy** para: `{', '.join(dummy_activos)}` "
        "(no se encontraron archivos reales en `data/`). "
        "Ver sección **'Cómo conectar datos reales'** al final.",
        icon="⚠️",
    )

st.markdown(
    """
Este espacio reúne las exploraciones de datos del equipo. Cada pestaña
agrupa un tipo de visualización; dentro de cada una puedes elegir qué
exploración ver con el selector.

**¿Eres pasante y quieres agregar tu exploración?** Ve al final de esta
página, sección *"Cómo agregar tu propia exploración"*.
"""
)

exploraciones_por_categoria = descubrir_exploraciones()

if not exploraciones_por_categoria:
    st.info("Todavía no hay exploraciones registradas. Sé la primera persona en agregar una 🎉")
else:
    tabs = st.tabs([
        CATEGORIA_LABELS.get(cat, cat) for cat in exploraciones_por_categoria
    ])

    for tab, (categoria, exploraciones) in zip(tabs, exploraciones_por_categoria.items()):
        with tab:
            opciones = {
                f"{e.titulo}" + (f" — {e.autor}" if e.autor else ""): e
                for e in exploraciones
            }
            seleccion = st.selectbox(
                "Exploración", list(opciones.keys()), key=f"select_{categoria}"
            )
            exploracion = opciones[seleccion]

            if exploracion.descripcion:
                st.caption(exploracion.descripcion)

            exploracion.render(data)

st.divider()

with st.expander("🔍 Cómo agregar tu propia exploración", expanded=False):
    st.markdown(
        """
1. Elige la carpeta que mejor describa tu gráfica dentro de `exploraciones/`:
   - `mapas/` — cualquier cosa con coordenadas / geografía
   - `series_tiempo/` — evolución temporal
   - `correlaciones/` — cruces entre variables
   - `otros/` — todo lo demás

   Si necesitas una categoría nueva, crea la carpeta — aparecerá sola como
   pestaña nueva.

2. Copia el archivo `ejemplo_*.py` de esa carpeta a un archivo nuevo con tu
   nombre, ej. `mapas/ana_bares_vs_robos.py`. (El archivo `ejemplo_*.py`
   se queda como referencia visible — no lo borres, solo cópialo.)

3. Edita `TITULO`, `AUTOR`, `DESCRIPCION`, y la función `render(data)` con tu
   gráfica. `data` ya trae `data["incidentes"]`, `data["h3_vars"]` y
   `data["denue"]` cargados — úsalos con pandas/plotly y dibuja con `st.*`.

4. Guarda el archivo. Al recargar la página, tu exploración aparece sola en
   la pestaña correspondiente, junto a un selector para elegirla.

No necesitas tocar `app.py` ni el código de nadie más.

---

**Reglas que sí importan** (lee esto, evita los errores típicos):

- **Lo único obligatorio es `def render(data): ...`.** `TITULO`, `AUTOR` y
  `DESCRIPCION` son opcionales. Si el archivo no define `render`, se ignora.
- **No estás limitado a Plotly.** Vale cualquier salida de Streamlit
  (`st.dataframe`, `st.map`, `st.bar_chart`, `st.pyplot` de matplotlib,
  `st.altair_chart`, folium…). Pero **si usas una librería nueva, agrégala a
  `requirements.txt`** o al desplegar tronará.
- **Claves de widgets únicas.** Todas las exploraciones comparten una misma
  página: cada `st.selectbox`/`st.multiselect`/etc. necesita `key=` único.
  **Prefija con tu nombre**: `key="ana_mapa_delito"` (si chocan, sale
  `DuplicateWidgetID`).
- **No modifiques `data` en su lugar — copia primero.** Los DataFrames vienen
  de un caché compartido; haz `df = data["incidentes"].copy()` antes de
  agregar/cambiar columnas, o afectas a las demás exploraciones.
- **Maneja el caso vacío.** Si tu filtro deja 0 filas, sal con
  `st.warning(...)`; una excepción dentro de `render` se muestra como caja
  roja y corta esa pestaña.
- **Agrega antes de graficar.** Son ~600k incidentes: usa
  `groupby`/`resample`/`value_counts` (y `@st.cache_data` en pasos pesados)
  antes de dibujar. Nunca mandes cientos de miles de puntos crudos a un mapa
  — revienta memoria. Mira `mapas/ejemplo_mapa_calor.py`: agrega por `h3_9`.
"""
    )
