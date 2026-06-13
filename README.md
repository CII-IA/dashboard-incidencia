# Dashboard de Exploraciones — Incidencia Delictiva Jalisco

Plantilla de dashboard en Streamlit para que cada colaborador descargue sus
exploraciones de datos en un lugar estandarizado, organizadas por tipo de
visualización.

## Estructura

```
app.py                          # App principal: navegación por categorías
utils/
  data_loader.py                 # Carga estandarizada de datos (real o dummy)
  registry.py                    # Auto-descubre las exploraciones
exploraciones/
  mapas/             ejemplo_mapa_calor.py
  series_tiempo/     ejemplo_tendencia.py
  correlaciones/     ejemplo_correlacion.py
  otros/             ejemplo_otro.py
data/
  (coloca aquí los .parquet/.csv reales)
requirements.txt
```

## Idea general

- Cada **carpeta** dentro de `exploraciones/` es una categoría y se vuelve
  una pestaña en el dashboard automáticamente (incluyendo carpetas nuevas
  que crees).
- Cada **archivo .py** dentro de una carpeta de categoría es una
  exploración independiente. El dashboard la detecta sola, sin tocar
  `app.py`.
- Todas las exploraciones reciben los mismos datos a través de un
  diccionario `data` (`data["incidentes"]`, `data["h3_vars"]`,
  `data["denue"]`), cargado por `utils/data_loader.py`.

## Correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Sin archivos en `data/`, el dashboard arranca con datos **dummy** (mismo
esquema que los reales) — los 4 ejemplos (`ejemplo_*.py`) ya funcionan así
desde el primer momento.

## Agregar tu exploración (pasantes)

1. Elige la carpeta (categoría) que mejor describa tu gráfica, o crea una
   nueva carpeta dentro de `exploraciones/` si no encaja en ninguna —
   aparecerá sola como pestaña nueva.
2. Copia el `ejemplo_*.py` de esa carpeta a un archivo nuevo con tu nombre
   (ej. `mapas/ana_bares_vs_robos.py`). Deja el ejemplo original intacto.
3. Edita `TITULO`, `AUTOR`, `DESCRIPCION` y la función `render(data)` con tu
   gráfica (Streamlit + Plotly).
4. Recarga la app — tu exploración aparece sola en su pestaña, junto a un
   selector para elegirla.

## Streamlit Community Cloud [Desplegado ✅]

1. Sube esta carpeta a un repositorio de GitHub (puede ser privado). ✅
2. Entra a [share.streamlit.io](https://share.streamlit.io) e inicia sesión
   con tu cuenta de GitHub. ✅
3. **"New app"** → selecciona el repo/rama → *main file path*: `app.py`. ✅
4. **Deploy**. Queda en una URL pública tipo `https://tu-app.streamlit.app`,
   corriendo de forma indefinida (se "duerme" sin uso y despierta solo al
   abrir el link — no hay límite de una semana). ✅

Si los `.parquet` reales son muy grandes para el repo (límite ~100 MB,
ideal <25 MB), considera subir una muestra representativa o usar Git LFS.
