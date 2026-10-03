"""
Práctica 1 — Modelización y Visualización de Datos (URV)
Rediseño interactivo: empleo vs. producción manufacturera en EE. UU. (2000–actualidad)

Ejecutar:  streamlit run app.py

Datos (FRED, Federal Reserve Bank of St. Louis), en la carpeta data/:
  MANEMP.csv  empleo manufacturero, miles de trabajadores, mensual, desestacionalizado
  IPMAN.csv   producción industrial manufacturera, índice 2017 = 100, mensual, desestacionalizado
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Colores: los mismos en título, tarjetas y líneas. Se evita rojo/verde a propósito.
C_EMPLEO, C_PRODUCCION, C_PRODUCTIVIDAD = "#d4572a", "#2563c9", "#6b46c1"

RECESIONES = [("2001-03-01", "2001-11-30"), ("2007-12-01", "2009-06-30"), ("2020-02-01", "2020-04-30")]
MANDATOS = [("2001-01-20", "Bush"), ("2009-01-20", "Obama"), ("2017-01-20", "Trump"),
            ("2021-01-20", "Biden"), ("2025-01-20", "Trump")]
INICIO_ORIGINAL = "2023-01-01"  # primer mes que mostraba el gráfico de la Casa Blanca


# ───────────────────────────── PREPROCESAMIENTO ─────────────────────────────

@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Lee los dos CSV de FRED y los une por fecha, conservando solo los meses con ambas series."""
    empleo = pd.read_csv("data/MANEMP.csv", parse_dates=["observation_date"])
    produccion = pd.read_csv("data/IPMAN.csv", parse_dates=["observation_date"])
    df = empleo.merge(produccion, on="observation_date", how="inner")
    df = df.rename(columns={"observation_date": "fecha", "MANEMP": "empleo", "IPMAN": "produccion"})
    return df.dropna().sort_values("fecha").reset_index(drop=True)


def marcar_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """PREPROCESAMIENTO 1 (outliers): marca los meses en que la variación mensual del empleo
    se aleja más de 2 desviaciones típicas de la media (|z| > 2)."""
    variacion = df["empleo"].diff()
    z = (variacion - variacion.mean()) / variacion.std()
    return df.assign(outlier=z.abs() > 2)


def suavizar(df: pd.DataFrame, meses: int = 3) -> pd.DataFrame:
    """PREPROCESAMIENTO 1 (suavizado): media móvil de 3 meses, para que un mes aislado
    no domine la lectura de la tendencia."""
    df = df.copy()
    for columna in ["empleo", "produccion"]:
        df[columna] = df[columna].rolling(meses, min_periods=1).mean()
    return df


def anadir_productividad(df: pd.DataFrame) -> pd.DataFrame:
    """PREPROCESAMIENTO 2 (variable derivada): producción por trabajador = producción / empleo."""
    return df.assign(productividad=df["produccion"] / df["empleo"])


def indexar(df: pd.DataFrame, anio_base: int) -> pd.DataFrame:
    """PREPROCESAMIENTO 3 (normalización): índice = valor / media del año base × 100.
    Convierte dos magnitudes con unidades distintas en una misma escala relativa."""
    df = df.copy()
    base = df[df["fecha"].dt.year == anio_base]
    for columna in ["empleo", "produccion", "productividad"]:
        df[f"i_{columna}"] = df[columna] / base[columna].mean() * 100
    return df


# ───────────────────────────────── UTILIDADES ─────────────────────────────────

def pct(serie: pd.Series) -> str:
    """Variación porcentual entre el primer y el último valor, con formato español."""
    cambio = (serie.iloc[-1] / serie.iloc[0] - 1) * 100
    signo = "+" if cambio >= 0 else "−"
    return f"{signo}{abs(cambio):.1f} %".replace(".", ",")


def miles(valor: float) -> str:
    return f"{valor:,.0f}".replace(",", ".")


def capas_de_contexto(fig: go.Figure, fin: pd.Timestamp, recesiones: bool, mandatos: bool, etiquetas: bool):
    """Añade al gráfico las bandas de recesión, la ventana del gráfico original y los mandatos."""
    if recesiones:
        for inicio_r, fin_r in RECESIONES:
            fig.add_shape(type="rect", x0=inicio_r, x1=fin_r, y0=0, y1=1, yref="paper",
                          fillcolor="rgba(128,128,128,0.18)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=INICIO_ORIGINAL, x1=fin, y0=0, y1=1, yref="paper",
                  fillcolor="rgba(212,87,42,0.10)", line_width=0, layer="below")
    if etiquetas:
        fig.add_annotation(x=INICIO_ORIGINAL, y=1, yref="paper", text="gráfico original", showarrow=False,
                           xanchor="left", yanchor="top", font=dict(size=11, color=C_EMPLEO))
    if mandatos:
        for fecha, nombre in MANDATOS:
            fig.add_shape(type="line", x0=fecha, x1=fecha, y0=0, y1=1, yref="paper",
                          line=dict(color="gray", width=1, dash="dash"))
            if etiquetas:
                fig.add_annotation(x=fecha, y=0, yref="paper", text=nombre, showarrow=False,
                                   xanchor="left", yanchor="bottom", font=dict(size=10, color="gray"))
    fig.add_hline(y=100, line=dict(color="gray", width=1, dash="dot"))


def formato(fig: go.Figure, titulo_y: str, rango_x, rango_y, alto: int):
    fig.update_layout(height=alto, margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    fig.update_xaxes(range=rango_x, showgrid=False, title_text="Fecha (datos mensuales)",
                     tickformat="%m/%Y", hoverformat="%m/%Y")
    fig.update_yaxes(range=rango_y, title_text=titulo_y)


# ─────────────────────────────────── PÁGINA ───────────────────────────────────

st.set_page_config(page_title="Fabricar más con menos gente", layout="wide")

datos = marcar_outliers(cargar_datos())
primer_mes, ultimo_mes = datos["fecha"].iloc[0], datos["fecha"].iloc[-1]

st.caption("REDISEÑO · EMPLEO Y PRODUCCIÓN MANUFACTURERA EN EE. UU.")
st.title("Fabricar :blue[más] con :orange[menos] gente")
st.write(
    "El gráfico original medía la industria solo por los empleos de 2023–2026. Con 25 años de contexto "
    "se ve otra historia: hoy la industria de EE. UU. produce más que en 2000 con casi un 27 % menos de "
    "trabajadores. Los cambios de los últimos años son una fracción mínima de ese cambio."
)

# Controles ---------------------------------------------------------------------
PERIODOS = {
    "2000–hoy": (primer_mes, ultimo_mes, None),
    "2000–2007": (primer_mes, pd.Timestamp("2007-12-01"),
                  "La producción sube mientras el empleo cae: es el tramo en el que de verdad se fabrica "
                  "más con menos gente y la producción por trabajador se dispara."),
    "2008–hoy": (pd.Timestamp("2008-01-01"), ultimo_mes,
                 "Desde 2008 la producción no ha vuelto a su máximo de finales de 2007 y el empleo se ha "
                 "estabilizado. La producción por trabajador acaba casi donde estaba: el gran salto es anterior."),
    "Ventana del gráfico original": (pd.Timestamp(INICIO_ORIGINAL), ultimo_mes,
                                     "Este es el tramo que mostraba el gráfico original. Con el eje vertical "
                                     "de todo el periodo, la variación de 2023–2026 apenas mueve las líneas."),
    "Personalizado": (primer_mes, ultimo_mes, None),
}

col_periodo, col_base = st.columns([4, 1])
periodo = col_periodo.radio("Periodo", list(PERIODOS), horizontal=True)
anios_completos = [a for a, n in datos["fecha"].dt.year.value_counts().sort_index().items() if n == 12]
anio_base = col_base.selectbox("Año base (= 100)", anios_completos)

inicio, fin, explicacion = PERIODOS[periodo]
if periodo == "Personalizado":
    inicio, fin = st.slider("Rango de fechas", min_value=primer_mes.to_pydatetime(),
                            max_value=ultimo_mes.to_pydatetime(),
                            value=(primer_mes.to_pydatetime(), ultimo_mes.to_pydatetime()), format="MM/YYYY")
    inicio, fin = pd.Timestamp(inicio), pd.Timestamp(fin)

col_a, col_b, col_c = st.columns(3)
ver_recesiones = col_a.toggle("Recesiones (NBER)", value=True)
ver_mandatos = col_b.toggle("Mandatos presidenciales", value=False)
usar_media_movil = col_c.toggle("Media móvil de 3 meses", value=False)

# Preprocesamiento según los controles ------------------------------------------
df = suavizar(datos) if usar_media_movil else datos
df = indexar(anadir_productividad(df), anio_base)
visible = df[(df["fecha"] >= inicio) & (df["fecha"] <= fin)]
if len(visible) < 2:
    st.warning("Elige un rango de al menos dos meses.")
    st.stop()

# Tarjetas: variación entre el primer y el último mes visibles -------------------
tramo = f"{visible['fecha'].iloc[0]:%m/%Y} → {visible['fecha'].iloc[-1]:%m/%Y}"
t1, t2, t3 = st.columns(3)
t1.metric("Empleo manufacturero", pct(visible["empleo"]))
t1.caption(f"{miles(visible['empleo'].iloc[0])} → {miles(visible['empleo'].iloc[-1])} mil trabajadores · {tramo}")
t2.metric("Producción manufacturera", pct(visible["produccion"]))
t2.caption(tramo)
t3.metric("Producción por trabajador", pct(visible["productividad"]))
t3.caption(tramo)

if explicacion:
    st.info(explicacion)

# Gráfico 1: empleo vs. producción ----------------------------------------------
# El eje vertical usa siempre el rango de TODO el periodo: al acercarse a 2023–2026 la escala
# no se reajusta, y así los cambios pequeños no parecen grandes (el truco del original).
rango_x = [inicio, fin]
ambos = pd.concat([df["i_empleo"], df["i_produccion"]])
rango_y = [ambos.min() - 3, ambos.max() + 3]

st.subheader(f"Empleo vs. producción (índice, media de {anio_base} = 100)")
fig = go.Figure()
fig.add_scatter(x=df["fecha"], y=df["i_produccion"], name="Producción (IPMAN)",
                line=dict(color=C_PRODUCCION, width=2.5), customdata=df["produccion"],
                hovertemplate="%{y:.1f}  (IPMAN %{customdata:.1f})")
fig.add_scatter(x=df["fecha"], y=df["i_empleo"], name="Empleo (MANEMP)",
                line=dict(color=C_EMPLEO, width=2.5), customdata=df["empleo"],
                hovertemplate="%{y:.1f}  (%{customdata:,.0f} mil trabajadores)")
atipicos = df[df["outlier"]]
fig.add_scatter(x=atipicos["fecha"], y=atipicos["i_empleo"], name="Mes atípico (|z| > 2)", mode="markers",
                marker=dict(size=8, color="rgba(0,0,0,0)", line=dict(color=C_EMPLEO, width=1.5)),
                hovertemplate="mes atípico")
capas_de_contexto(fig, ultimo_mes, ver_recesiones, ver_mandatos, etiquetas=True)
formato(fig, f"Índice ({anio_base} = 100)", rango_x, rango_y, alto=460)
st.plotly_chart(fig, width="stretch")

# Gráfico 2: producción por trabajador (mismo periodo, año base y capas) ---------
st.subheader(f"Producción por trabajador (índice, media de {anio_base} = 100)")
fig2 = go.Figure()
fig2.add_scatter(x=df["fecha"], y=df["i_productividad"], name="Producción por trabajador",
                 line=dict(color=C_PRODUCTIVIDAD, width=2.5), hovertemplate="%{y:.1f}")
capas_de_contexto(fig2, ultimo_mes, ver_recesiones, ver_mandatos, etiquetas=False)
formato(fig2, f"Índice ({anio_base} = 100)", rango_x,
        [df["i_productividad"].min() - 3, df["i_productividad"].max() + 3], alto=300)
fig2.update_layout(showlegend=False)
st.plotly_chart(fig2, width="stretch")

# Pie -----------------------------------------------------------------------------
st.caption(
    f"**Fuente:** FRED (Federal Reserve Bank of St. Louis): MANEMP, empleo en miles, e IPMAN, índice de "
    f"producción industrial manufacturera; ambas mensuales y desestacionalizadas. Datos hasta {ultimo_mes:%m/%Y}.  \n"
    "**Método:** cada serie se divide entre su media del año base y se multiplica por 100. Recesiones según el NBER.  \n"
    "**Limitación:** la producción por trabajador es una productividad aparente: no separa la automatización de "
    "otros factores (competencia exterior, deslocalización, cambio en lo que se fabrica)."
)
