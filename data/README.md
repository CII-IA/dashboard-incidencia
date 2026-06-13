Coloca aquí tus archivos de datos reales (.parquet o .csv) con estos nombres:

- incidentes_delictivos.parquet  (salida de iieg_pipeline.py)
    columnas: fecha, delito, x, y, colonia, municipio, clave_mun, hora,
              bien_afectado, zona_geografica, region, h3_9
- contexto_h3.parquet            (variables por celda H3 res 9)
    mínimo: h3_9 + variables numéricas de contexto
            (infraestructura urbana inv_*  y conteos de POIs poi_*)
- denue_jalisco.parquet          (establecimientos DENUE)
    mínimo: categoria   (opcional: h3_9 para cruces espaciales)

La unidad espacial del proyecto es la celda H3 resolución 9 (~0.1 km²). Como
los incidentes traen h3_9, se cruzan con contexto_h3 sin geometría externa.

Si no existen, todas las exploraciones usan datos DUMMY generados
automáticamente con el mismo esquema (ver utils/data_loader.py), para que
se pueda desarrollar y probar sin esperar a tener los datos reales.

En cuanto coloques los archivos reales aquí, TODAS las exploraciones
(las existentes y las nuevas) empiezan a usarlos automáticamente — nadie
tiene que cambiar su código.
