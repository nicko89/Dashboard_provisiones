import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta

# ==========================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================================
st.set_page_config(page_title="Provision Cartera USA", layout="wide")

# ===== FONDO CORPORATIVO =====
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: url("assets/fondo_corporativo.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.7);
    }
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.9);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# ENCABEZADO CON LOGO Y TÍTULO
# ==========================================================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/Logo.png", width=210)
with col2:
    st.markdown("""
        <h2 style="margin-bottom:0; text-align:center;">Dashboard de Provisiones USA</h2>
        <p style="color:gray; margin-top:0; text-align:center;">Análisis interactivo de provisiones contables</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================================
# CARGA DE DATOS
# ==========================================================
@st.cache_data
def cargar_datos():
    df_base = pd.read_excel("Data/Base Provision.xlsx")
    df_write = pd.read_excel("Data/Base Provision.xlsx", sheet_name="Write offs")

    # Normalizar nombres de columnas y fechas
    df_base.columns = df_base.columns.str.strip()
    df_write.columns = df_write.columns.str.strip()
    df_base['Fecha'] = pd.to_datetime(df_base['Fecha'])
    df_write['Date'] = pd.to_datetime(df_write['Date'])

    return df_base, df_write

df, df_write = cargar_datos()

# ==========================================================
# FILTRO DE AÑOS (solo 2024 y 2025)
# ==========================================================
df = df[df['Fecha'].dt.year.isin([2024, 2025])].copy()

# ==========================================================
# CLASIFICACIÓN DE CLIENTES
# ==========================================================
def tipo_cliente(code):
    if str(code).startswith(("INT", "SH")) or code in [
        "NAC1617", "NAC0986", "NAC0987", "NAC1312",
        "NAC0740", "NAC0756", "NAC1614", "NAC1650"
    ]:
        return "INT"
    return "REGULAR"

df['TipoCliente'] = df['Infor Code'].apply(tipo_cliente)
df = df[df['TipoCliente'] != "INT"].copy()

# ==========================================================
# CÁLCULO DE PROVISIONES
# ==========================================================
def provision_91_180(row):
    saldo = row.get('91 - 180', 0)
    if saldo <= 0:
        return 0
    return saldo * (0.20 if row['Fecha'].year == 2024 else 0.03)

def provision_181_270(row):
    saldo = row.get('181 - 270', 0)
    return saldo * 0.50 if saldo > 0 else 0

def provision_271_360(row):
    saldo = row.get('271-360', 0)
    if saldo <= 0:
        return 0
    return saldo * (0.50 if row['Fecha'].year == 2024 else 1.0)

def provision_mayor_360(row):
    saldo = row.get('> 360', 0)
    return saldo if saldo > 0 else 0

df['Provision 91-180'] = df.apply(provision_91_180, axis=1)
df['Provision 181-270'] = df.apply(provision_181_270, axis=1)
df['Provision 271-360'] = df.apply(provision_271_360, axis=1)
df['Provision >360'] = df.apply(provision_mayor_360, axis=1)
df['Total Provision'] = df[['Provision 91-180', 'Provision 181-270',
                            'Provision 271-360', 'Provision >360']].sum(axis=1)

# ==========================================================
# CAMPOS TEMPORALES
# ==========================================================
df['Año'] = df['Fecha'].dt.year
df['Mes'] = df['Fecha'].dt.month
df['AñoMes'] = df['Fecha'].dt.to_period('M')
df['AñoMes_str'] = df['AñoMes'].astype(str)

# ==========================================================
# SIDEBAR: FILTROS
# ==========================================================
st.sidebar.header("🗓️ Filtros de Periodo")
año_sel = st.sidebar.selectbox("Seleccionar año:", sorted(df['Año'].unique(), reverse=True))
meses_disponibles = sorted(df[df['Año'] == año_sel]['Mes'].unique())
mes_sel = st.sidebar.selectbox("Seleccionar mes:", meses_disponibles)

# ==========================================================
# BUSCADOR CON BOTÓN DE LIMPIEZA
# ==========================================================
st.sidebar.header("🔍 Buscador")

if "busqueda" not in st.session_state:
    st.session_state.busqueda = ""

def limpiar_busqueda():
    st.session_state.busqueda = ""

busqueda = st.sidebar.text_input("Buscar Cliente o Infor Code:", st.session_state.busqueda, key="busqueda")
st.sidebar.button("🧹 Limpiar búsqueda", on_click=limpiar_busqueda)

# ==========================================================
# FILTRO PRINCIPAL
# ==========================================================
df_filtrado = df[(df['Año'] == año_sel) & (df['Mes'] == mes_sel)].copy()
if st.session_state.busqueda:
    df_filtrado = df_filtrado[
        df_filtrado['Customer'].str.contains(st.session_state.busqueda, case=False, na=False) |
        df_filtrado['Infor Code'].str.contains(st.session_state.busqueda, case=False, na=False)
    ]

# ==========================================================
# MES ANTERIOR
# ==========================================================
fecha_sel = pd.Timestamp(año_sel, mes_sel, 1)
fecha_ant = fecha_sel - relativedelta(months=1)
df_mes_ant = df[(df['Fecha'].dt.year == fecha_ant.year) & (df['Fecha'].dt.month == fecha_ant.month)].copy()

if st.session_state.busqueda:
    df_mes_ant = df_mes_ant[
        df_mes_ant['Customer'].str.contains(st.session_state.busqueda, case=False, na=False) |
        df_mes_ant['Infor Code'].str.contains(st.session_state.busqueda, case=False, na=False)
    ]

# ==========================================================
# MÉTRICAS DE PROVISIONES
# ==========================================================
total_actual = df_filtrado['Total Provision'].sum()
total_anterior = df_mes_ant['Total Provision'].sum() if not df_mes_ant.empty else 0
variacion_abs = total_actual - total_anterior
variacion_pct = (variacion_abs / total_anterior * 100) if total_anterior != 0 else 0

# ==========================================================
# CÁLCULO DE WRITE OFFS (EQUIVALENTE DAX)
# ==========================================================
df_write = df_write[df_write['Cust/Vendor'].notna()]
df_write = df_write[~df_write['Cust/Vendor'].str.startswith("INT")]
df_write['Año'] = df_write['Date'].dt.year
df_write['Mes'] = df_write['Date'].dt.month

writeoffs_mes = df_write[
    (df_write['Año'] == año_sel) & (df_write['Mes'] == mes_sel)
]['Amount'].sum()

writeoffs_texto = "Sin Write offs" if writeoffs_mes == 0 else f"${writeoffs_mes:,.2f}"

# ==========================================================
# TARJETAS DE MÉTRICAS
# ==========================================================
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("🗓 Año", año_sel)
c2.metric("📆 Mes seleccionado", mes_sel)
c3.metric("💰 Total mes anterior", f"${total_anterior:,.2f}")
c4.metric("💰 Total mes actual", f"${total_actual:,.2f}")
c5.metric("📈 Variación %", f"{variacion_pct:.2f}%")
c6.metric("💸 Write Offs", writeoffs_texto)

st.markdown("---")

# ==========================================================
# TABLA DE CLIENTES
# ==========================================================
st.subheader(f"📋 Total de Provisiones - {año_sel}-{mes_sel:02d}")
df_tabla = df_filtrado.groupby(['Infor Code', 'Customer'], as_index=False)['Total Provision'].sum()
df_tabla['% del Total'] = (df_tabla['Total Provision'] / df_tabla['Total Provision'].sum()) * 100

st.dataframe(
    df_tabla.style.format({
        "Total Provision": "${:,.2f}",
        "% del Total": "{:.2f}%"
    })
)

# ==========================================================
# EVOLUCIÓN ÚLTIMOS 5 MESES
# ==========================================================
periodo_sel = pd.Period(fecha_sel, freq='M')
ultimos_5 = [periodo_sel - i for i in range(4, -1, -1)]
df_ultimos_5 = df[df['AñoMes'].isin(ultimos_5)].copy()

if st.session_state.busqueda:
    df_ultimos_5 = df_ultimos_5[
        df_ultimos_5['Customer'].str.contains(st.session_state.busqueda, case=False, na=False) |
        df_ultimos_5['Infor Code'].str.contains(st.session_state.busqueda, case=False, na=False)
    ]

df_agrupado = (
    df_ultimos_5
    .groupby('AñoMes', as_index=False)['Total Provision']
    .sum()
    .sort_values('AñoMes')
)
df_agrupado['AñoMes_label'] = df_agrupado['AñoMes'].dt.to_timestamp().dt.strftime('%b %Y')

y_max = 50000 if st.session_state.busqueda else 200000

fig_linea = px.line(
    df_agrupado,
    x='AñoMes_label',
    y='Total Provision',
    markers=True,
    title="Evolución mensual de la Provisión Total",
    color_discrete_sequence=['#0072B2']
)
fig_linea.update_traces(line=dict(width=4), marker=dict(size=8))
fig_linea.update_yaxes(range=[100000, y_max], tick0=100000, dtick=50000,
                       tickformat=",", showgrid=True, gridwidth=1,
                       gridcolor="rgba(200,200,200,0.35)", griddash="dash")
fig_linea.update_xaxes(title_text="Mes", showgrid=False)
fig_linea.update_layout(yaxis_title="Total Provision ($)",
                        xaxis_title="Mes",
                        template="plotly_white",
                        margin=dict(l=40, r=20, t=60, b=40),
                        title_x=0.02)

st.subheader("📈 Evolución de Total Provision (Últimos 5 meses)")
st.plotly_chart(fig_linea, use_container_width=True)

# ==========================================================
# DISTRIBUCIÓN DE PROVISIONES POR RANGO
# ==========================================================
st.subheader("🥧 Distribución de Provisión por Rango (Comparativo)")

df_pie_ant = df_mes_ant if not df_mes_ant.empty else df_filtrado.copy()
totales_ant = df_pie_ant[['Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360']].sum().to_dict()
totales_act = df_filtrado[['Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360']].sum().to_dict()

df_pie_ant = pd.DataFrame(list(totales_ant.items()), columns=['Rango', 'Total'])
df_pie_act = pd.DataFrame(list(totales_act.items()), columns=['Rango', 'Total'])

col_pie1, col_pie2 = st.columns(2)
with col_pie1:
    fig_pie_ant = px.pie(df_pie_ant, values='Total', names='Rango',
                         title=f"Mes Anterior ({fecha_ant.strftime('%Y-%m')})",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie_ant, use_container_width=True)
with col_pie2:
    fig_pie_act = px.pie(df_pie_act, values='Total', names='Rango',
                         title=f"Mes Seleccionado ({año_sel}-{mes_sel:02d})",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie_act, use_container_width=True)

# ==========================================================
# FOOTER
# ==========================================================
st.markdown("---")
st.caption("Desarrollado en Streamlit – Dashboard Provisiones © 2025")
