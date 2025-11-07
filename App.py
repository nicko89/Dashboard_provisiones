import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta

# ===== CONFIGURACION DE LA PAGINA =====
st.set_page_config(page_title="Provision Cartera USA", layout="wide")

# ===== ENCABEZADO CON LOGO =====
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/Logo.png", width=210)
with col2:
    st.markdown("""
        <h2 style="margin-bottom:0; text-align:center;">Dashboard de Provisiones USA</h2>
        <p style="color:gray; margin-top:0; text-align:center;">Analisis interactivo de provisiones contables</p>
    """, unsafe_allow_html=True)
st.markdown("---")

# ===== CARGA DE DATOS =====
@st.cache_data
def cargar_datos():
    # Leer la base principal
    df = pd.read_excel("Data/Base Provision.xlsx")
    df.columns = df.columns.str.strip()
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Intentar leer hoja "Write off" (si existe)
    try:
        df_write = pd.read_excel("Data/Base Provision.xlsx", sheet_name="Write off")
        df_write.columns = df_write.columns.str.strip()
        df_write["Fecha"] = pd.to_datetime(df_write["Fecha"], errors="coerce")
    except Exception:
        df_write = pd.DataFrame(columns=["Fecha", "Amount"])
    
    return df, df_write

df, df_write = cargar_datos()

# ===== FILTRO SOLO 2024 Y 2025 =====
df = df[df["Fecha"].dt.year.isin([2024, 2025])].copy()

# ===== CLASIFICACION DE CLIENTES =====
def tipo_cliente(code):
    if str(code).startswith(("INT", "SH")) or code in [
        "NAC1617", "NAC0986", "NAC0987", "NAC1312", "NAC0740",
        "NAC0756", "NAC1614", "NAC1650"
    ]:
        return "INT"
    return "REGULAR"

df["TipoCliente"] = df["Infor Code"].apply(tipo_cliente)
df = df[df["TipoCliente"] != "INT"].copy()

# ===== CALCULO DE PROVISIONES =====
def provision_91_180(row):
    saldo = row.get("91 - 180", 0)
    if saldo <= 0:
        return 0
    return saldo * (0.20 if row["Fecha"].year == 2024 else 0.03)

def provision_181_270(row):
    saldo = row.get("181 - 270", 0)
    return saldo * 0.50 if saldo > 0 else 0

def provision_271_360(row):
    saldo = row.get("271-360", 0)
    if saldo <= 0:
        return 0
    return saldo * (0.50 if row["Fecha"].year == 2024 else 1.0)

def provision_mayor_360(row):
    saldo = row.get("> 360", 0)
    return saldo if saldo > 0 else 0

df["Provision 91-180"] = df.apply(provision_91_180, axis=1)
df["Provision 181-270"] = df.apply(provision_181_270, axis=1)
df["Provision 271-360"] = df.apply(provision_271_360, axis=1)
df["Provision >360"] = df.apply(provision_mayor_360, axis=1)
df["Total Provision"] = df[
    ["Provision 91-180", "Provision 181-270", "Provision 271-360", "Provision >360"]
].sum(axis=1)

# ===== CAMPOS TEMPORALES =====
df["Año"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month
df["AñoMes"] = df["Fecha"].dt.to_period("M")
df["AñoMes_str"] = df["AñoMes"].astype(str)

# ===== FILTROS =====
st.sidebar.header("🗓️ Filtros de Periodo")
año_sel = st.sidebar.selectbox("Seleccionar año:", sorted(df["Año"].unique(), reverse=True))
meses_disponibles = sorted(df[df["Año"] == año_sel]["Mes"].unique())
mes_sel = st.sidebar.selectbox("Seleccionar mes:", meses_disponibles)

# ===== BUSCADOR =====
st.sidebar.header("🔍 Buscador")
busqueda = st.sidebar.text_input("Buscar Cliente o Infor Code:")

df_filtrado = df[(df["Año"] == año_sel) & (df["Mes"] == mes_sel)].copy()
if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado["Customer"].str.contains(busqueda, case=False, na=False)
        | df_filtrado["Infor Code"].str.contains(busqueda, case=False, na=False)
    ]

# ===== MES ANTERIOR =====
fecha_sel = pd.Timestamp(año_sel, mes_sel, 1)
fecha_ant = fecha_sel - relativedelta(months=1)
df_mes_ant = df[
    (df["Fecha"].dt.year == fecha_ant.year)
    & (df["Fecha"].dt.month == fecha_ant.month)
].copy()
if busqueda:
    df_mes_ant = df_mes_ant[
        df_mes_ant["Customer"].str.contains(busqueda, case=False, na=False)
        | df_mes_ant["Infor Code"].str.contains(busqueda, case=False, na=False)
    ]

# ===== METRICAS =====
total_actual = df_filtrado["Total Provision"].sum()
total_anterior = df_mes_ant["Total Provision"].sum()
variacion = total_actual - total_anterior
porcentaje = (variacion / total_anterior * 100) if total_anterior != 0 else 0

# ===== WRITE OFF DEL MES =====
writeoffs_mes = 0
if not df_write.empty and "Fecha" in df_write.columns and "Amount" in df_write.columns:
    df_write["Año"] = df_write["Fecha"].dt.year
    df_write["Mes"] = df_write["Fecha"].dt.month
    writeoffs_mes = df_write[
        (df_write["Año"] == año_sel) & (df_write["Mes"] == mes_sel)
    ]["Amount"].sum()

# ===== KPI PRINCIPALES =====
col1, col2, col3 = st.columns(3)
col1.metric("Provision Actual", f"${total_actual:,.0f}")
col2.metric("Variacion", f"${variacion:,.0f}", f"{porcentaje:,.1f}%")
col3.metric("Write Off", f"${writeoffs_mes:,.0f}")

st.markdown("---")

# ===== GRAFICA DE TENDENCIA =====
df_tendencia = df.groupby("AñoMes_str", as_index=False)["Total Provision"].sum()
fig = px.line(df_tendencia, x="AñoMes_str", y="Total Provision",
              title="Tendencia de Provisiones", markers=True)
st.plotly_chart(fig, use_container_width=True)

# ===== TABLA DE DETALLE =====
st.subheader("📋 Detalle de Clientes")
st.dataframe(
    df_filtrado[["Customer", "Infor Code", "Total Provision"]].sort_values("Total Provision", ascending=False),
    use_container_width=True
)
