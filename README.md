# Fabricar más con menos gente

El gráfico original mostraba solo la variación del empleo entre 2023 y 2026. Este rediseño pone esos datos en un contexto de 25 años y los compara con la **producción** manufacturera: desde el año 2000 el empleo cae un 27%
mientras la producción sube un 7,5%.

## Link

https://mv-p1-fase3-link.streamlit.app/#empleo-vs-produccion-indice-media-de-2000-100

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Preprocesamiento (funciones de `app.py`)

1. **Outliers** (`marcar_outliers`, `suavizar`): se marcan los meses con |z| > 2 en la variación mensual del empleo
   (enero de 2009 y abril-junio de 2020) y se ofrece una media móvil de 3 meses.
2. **Variable derivada** (`anadir_productividad`): producción por trabajador = IPMAN / MANEMP.
3. **Normalización** (`indexar`): índice = valor / media del año base × 100, para comparar en un mismo eje
   dos magnitudes con unidades distintas.

## Interacciones

| Tipología | Control | Para qué |
|---|---|---|
| Filtrar | Selector de periodo y rango de fechas personalizado | Ver un subconjunto de los datos, incluida la ventana 2023-2026 del gráfico original |
| Reconfigurar | Año base, media móvil | Comprobar que la conclusión no depende del año base ni del ruido mensual |
| Abstraer/Elaborar | Tooltip, capas de recesiones y mandatos | Más detalle bajo demanda (valor absoluto, contexto) |
| Conectar | Periodo, año base y capas compartidos | Un cambio actualiza a la vez las tarjetas y los dos gráficos |
| Explorar | Zoom arrastrando sobre el gráfico | Acercarse a un tramo concreto |