# Fabricar más con menos gente

Rediseño interactivo de un gráfico de la Casa Blanca sobre empleo manufacturero en EE. UU.
Práctica 1 · Modelización y Visualización de Datos · URV.

El gráfico original mostraba solo la variación del empleo entre 2023 y 2026. Este rediseño pone esos datos
en un contexto de 25 años y los compara con la **producción** manufacturera: desde 2000 el empleo cae un 27 %
mientras la producción sube un 7,5 %.

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Archivos

| Archivo | Contenido |
|---|---|
| `app.py` | Toda la aplicación: carga de datos, preprocesamiento, gráficos e interacciones (Streamlit + Plotly + pandas) |
| `data/MANEMP.csv` | Empleo manufacturero, miles de trabajadores, mensual, desestacionalizado (FRED) |
| `data/IPMAN.csv` | Producción industrial manufacturera, índice 2017 = 100, mensual, desestacionalizado (FRED) |

Datos descargados de FRED el 01/10/2026 (enero de 2000 – agosto de 2026).

## Preprocesamiento (funciones de `app.py`)

1. **Outliers** (`marcar_outliers`, `suavizar`): se marcan los meses con |z| > 2 en la variación mensual del empleo
   (enero de 2009 y abril–junio de 2020) y se ofrece una media móvil de 3 meses.
2. **Variable derivada** (`anadir_productividad`): producción por trabajador = IPMAN / MANEMP.
3. **Normalización** (`indexar`): índice = valor / media del año base × 100, para comparar en un mismo eje
   dos magnitudes con unidades distintas.

## Interacciones

| Tipología | Control | Para qué |
|---|---|---|
| Filtrar | Selector de periodo y rango de fechas personalizado | Ver un subconjunto de los datos, incluida la ventana 2023–2026 del gráfico original |
| Reconfigurar | Año base, media móvil | Comprobar que la conclusión no depende del año base ni del ruido mensual |
| Abstraer/Elaborar | Tooltip, capas de recesiones y mandatos | Más detalle bajo demanda (valor absoluto, contexto) |
| Conectar | Periodo, año base y capas compartidos | Un cambio actualiza a la vez las tarjetas y los dos gráficos |
| Explorar | Zoom arrastrando sobre el gráfico | Acercarse a un tramo concreto |

## Resultados (datos hasta agosto de 2026)

| Periodo | Empleo | Producción | Producción por trabajador |
|---|---|---|---|
| 2000–hoy | −26,9 % | +7,5 % | +47,0 % |
| 2000–2007 | −20,5 % | +15,6 % | +45,5 % |
| 2008–hoy | −7,9 % | −6,8 % | +1,1 % |
| 2023–hoy (ventana del gráfico original) | −2,1 % | +1,7 % | +3,8 % |

## Limitaciones

La producción por trabajador es una productividad *aparente*: no separa la automatización de otros factores
(competencia exterior, deslocalización, cambio en lo que se fabrica).

## Uso de IA

El código se escribió con ayuda de un asistente de IA. El planteamiento del rediseño y las decisiones de diseño
son del autor.
