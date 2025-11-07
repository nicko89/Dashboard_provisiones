import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(page_title="Provision cartera USA", layout="wide")

# ===== CSS: fondo e identidad de colores (verde/blanco/gris) =====
st.markdown(
    """
    <style>
    /* Fondo usando la imagen en assets (overlay blanco para legibilidad) */
    .stApp {
        background-image: url("/assets/Fondo.jpg");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }
    .stApp::before{
        content: "";
        position: absolute;
        inset: 0;
        background-color: rgba(255,255,255,0.88); /* overlay blanco predominante */
        z-index: 0;
    }
    /* Header box para mejor legibilidad sobre el fondo */
    .header-box {
        background: rgba(255,255,255,0.95);
        padding: 10px;
        border-radius: 8px;
        z-index: 1;
    }
    /* Títulos y textos */
    h1, h2, h3, h4, h5, h6 { color: #2E7D32 !important; } /* verde primario */
    p, span, div, label { color: #212121 !important; } /* texto oscuro */
    /* Métricas y tarjetas */
    .stMetric {
        background-color: #ffffffaa;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 6px;
    }
    /* Gráficos con fondo blanco */
    .js-plotly-plot {
        background-color: rgba(255,255,255,0.95) !important;
        border-radius: 8px;
        padding: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== ENCABEZADO CON LOGO (logo más grande) =====
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/Logo.png", width=300)  # logo más grande
with col2:
    st.markdown(
        """
        <div class="header-box">
        <h1 style="margin:0; text-align:center;">Provision cartera USA</h1>
        <p style="color:gray; margin:0; text-align:center;">Análisis interactivo de provisiones contables</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ===== CARGA DE DATOS =====
@st.cache_data
def cargar_datos():
    df = pd.read_excel("Data/Base Provision.xlsx")
    df.columns = df.columns.str.strip()
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    # Intento robusto de leer la hoja "Write off" (si existe)
    try:
        df_write = pd.read_excel("Data/Base Provision.xlsx", sheet_name="Write off")
        df_write.columns = df_write.columns.str.strip()
    except Exception:
        df_write = pd.DataFrame()
    return df, df_write

df, df_write = cargar_datos()

# ===== FILTRO SOLO 2024 Y 2025 =====
df = df[df['Fecha'].dt.year.isin([2024, 2025])].copy()

# ===== CLASIFICACIÓN DE CLIENTES =====
def tipo_cliente(code):
    if str(code).startswith(("INT", "SH")) or code in [
        "NAC1617", "NAC0986", "NAC0987", "NAC1312",
        "NAC0740", "NAC0756", "NAC1614", "NAC1650"
    ]:
        return "INT"
    return "REGULAR"

df['TipoCliente'] = df['Infor Code'].apply(tipo_cliente)
df = df[df['TipoCliente'] != "INT"].copy()

# ===== CÁLCULO DE PROVISIONES =====
def provision_91_180(row):
    saldo = row.get('91 - 180', 0)
    if pd.isna(saldo) or saldo <= 0:
        return 0
    return saldo * (0.20 if row['Fecha'].year == 2024 else 0.03)

def provision_181_270(row):
    saldo = row.get('181 - 270', 0)
    return saldo * 0.50 if (not pd.isna(saldo) and saldo > 0) else 0

def provision_271_360(row):
    saldo = row.get('271-360', 0)
    if pd.isna(saldo) or saldo <= 0:
        return 0
    return saldo * (0.50 if row['Fecha'].year == 2024 else 1.0)

def provision_mayor_360(row):
    saldo = row.get('> 360', 0)
    return saldo if (not pd.isna(saldo) and saldo > 0) else 0

df['Provision 91-180'] = df.apply(provision_91_180, axis=1)
df['Provision 181-270'] = df.apply(provision_181_270, axis=1)
df['Provision 271-360'] = df.apply(provision_271_360, axis=1)
df['Provision >360'] = df.apply(provision_mayor_360, axis=1)
df['Total Provision'] = df[['Provision 91-180', 'Provision 181-270',
                            'Provision 271-360', 'Provision >360']].sum(axis=1).fillna(0)

# ===== CAMPOS TEMPORALES =====
df['Año'] = df['Fecha'].dt.year
df['Mes'] = df['Fecha'].dt.month
df['AñoMes'] = df['Fecha'].dt.to_period('M')
df['AñoMes_str'] = df['AñoMes'].astype(str)

# ===== SIDEBAR: filtros, buscador y seleccion de cliente (buscador arriba, cliente debajo) =====
st.sidebar.header("🗓️ Filtros de Periodo")
año_sel = st.sidebar.selectbox("Seleccionar año:", sorted(df['Año'].unique(), reverse=True))
meses_disponibles = sorted(df[df['Año'] == año_sel]['Mes'].unique())
mes_sel = st.sidebar.selectbox("Seleccionar mes:", meses_disponibles)

st.sidebar.header("🔍 Buscador")
if 'busqueda' not in st.session_state:
    st.session_state['busqueda'] = ''
# lista de clientes para selectbox
clientes_list = sorted(df['Customer'].dropna().unique().tolist())
cliente_options = ['Todos'] + clientes_list

st.sidebar.text_input("Buscar Cliente o Infor Code:", key='busqueda')
if 'cliente_detalle' not in st.session_state:
    st.session_state['cliente_detalle'] = 'Todos'
st.sidebar.selectbox("Seleccionar Cliente (detalle):", cliente_options, key='cliente_detalle')

def _clear_filters():
    st.session_state['busqueda'] = ''
    st.session_state['cliente_detalle'] = 'Todos'

st.sidebar.button("Limpiar selección", on_click=_clear_filters)

busqueda = st.session_state.get('busqueda', '')
cliente_detalle = st.session_state.get('cliente_detalle', 'Todos')

# ===== FILTRADO PRINCIPAL POR AÑO/MES y buscador/cliente detalle =====
df_filtrado = df[(df['Año'] == año_sel) & (df['Mes'] == mes_sel)].copy()

if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado['Customer'].str.contains(busqueda, case=False, na=False) |
        df_filtrado['Infor Code'].str.contains(busqueda, case=False, na=False)
    ]

if cliente_detalle and cliente_detalle != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Customer'] == cliente_detalle].copy()

# ===== MES ANTERIOR (filtrado también) =====
fecha_sel = pd.Timestamp(año_sel, mes_sel, 1)
fecha_ant = fecha_sel - relativedelta(months=1)
df_mes_ant = df[(df['Fecha'].dt.year == fecha_ant.year) & (df['Fecha'].dt.month == fecha_ant.month)].copy()

if busqueda:
    df_mes_ant = df_mes_ant[
        df_mes_ant['Customer'].str.contains(busqueda, case=False, na=False) |
        df_mes_ant['Infor Code'].str.contains(busqueda, case=False, na=False)
    ]
if cliente_detalle and cliente_detalle != 'Todos':
    df_mes_ant = df_mes_ant[df_mes_ant['Customer'] == cliente_detalle].copy()

# ===== MÉTRICAS =====
total_actual = df_filtrado['Total Provision'].sum()
total_anterior = df_mes_ant['Total Provision'].sum() if not df_mes_ant.empty else 0
variacion_abs = total_actual - total_anterior
variacion_pct = (variacion_abs / total_anterior * 100) if total_anterior != 0 else 0.0

# ===== CÁLCULO DE WRITE OFF (mejora robusta) =====
# Principio: la hoja 'Write off' es una hoja separada. Aquí seleccionamos la columna de monto más adecuada,
# filtramos por mes/año seleccionado y (si es aplicable) por clientes presentes en df_filtrado.
writeoffs_mes = 0

if not df_write.empty:
    # limpiar nombres
    cols = [c.strip() for c in df_write.columns.tolist()]
    df_write.columns = cols

    # detectar columna fecha
    date_candidates = ['Date', 'Fecha', 'date', 'fecha', 'Check Date', 'CheckDate']
    date_col = next((c for c in cols if c in date_candidates), None)
    if date_col is None:
        # heurística: columna datetime o que contenga 'date'
        for c in cols:
            if 'date' in c.lower():
                date_col = c
                break

    # detectar columna monto preferencialmente en créditos (write-offs suelen estar en Credit)
    preferred_amounts = [
        'Credit (Domestic)', 'Credit (Foreign)', 'Credit', 'Amount', 'Monto',
        'Debit (Domestic)', 'Debit (Foreign)', 'Debit', 'Value', 'Valor'
    ]
    amount_col = next((c for c in preferred_amounts if c in cols), None)
    if amount_col is None:
        # si no hay coincidencia exacta, buscar aproximado
        for c in cols:
            low = c.lower()
            if 'credit' in low or 'amount' in low or 'monto' in low or 'valor' in low or 'debit' in low:
                amount_col = c
                break

    # detectar columna cust/vendor
    cust_candidates = ['Cust/Vendor', 'Cust Vendor', 'Customer', 'Cust', 'Vendor', 'CustVendor', 'Name', 'Cust / Vendor']
    cust_col = next((c for c in cols if c in cust_candidates), None)
    if cust_col is None:
        # heurística
        for c in cols:
            low = c.lower()
            if 'cust' in low or 'vendor' in low or 'name' in low:
                cust_col = c
                break

    # si no encontramos amount_col o date_col, no rompemos la app; avisamos y dejamos 0
    if amount_col is None or date_col is None:
        st.warning("La hoja 'Write off' está presente pero no se reconoció una columna clara de fecha/monto. El indicador Write Offs será 0. Si quieres, dime el nombre exacto de la columna de monto.")
        writeoffs_mes = 0
    else:
        # convertir fecha
        df_write[date_col] = pd.to_datetime(df_write[date_col], errors='coerce')

        # filtrar filas del mes/año seleccionado
        df_write['Año'] = df_write[date_col].dt.year
        df_write['Mes'] = df_write[date_col].dt.month
        df_write_mes = df_write[(df_write['Año'] == año_sel) & (df_write['Mes'] == mes_sel)].copy()

        # eliminar clientes INT si existe cust_col
        if cust_col is not None:
            df_write_mes = df_write_mes[df_write_mes[cust_col].notna()].copy()
            # filtrar que los primeros 3 caracteres no sean 'INT'
            df_write_mes = df_write_mes[~df_write_mes[cust_col].astype(str).str.strip().str[:3].str.upper().eq('INT')]

        # Si hay filtro por cliente en sidebar, sumar sólo para ese cliente
        try:
            # homogeneizar nombres para comparar si se puede
            if cust_col is not None and 'Customer' in df_filtrado.columns and not df_filtrado['Customer'].isna().all():
                # crear columnas comparables en mayúscula/strip
                df_write_mes['_cust_norm'] = df_write_mes[cust_col].astype(str).str.strip().str.upper()
                df_filtrado['_cust_norm'] = df_filtrado['Customer'].astype(str).str.strip().str.upper()

                # Si hay cliente seleccionado diferente a 'Todos', filtrar por ese cliente
                if cliente_detalle and cliente_detalle != 'Todos':
                    target = cliente_detalle.strip().upper()
                    df_write_mes = df_write_mes[df_write_mes['_cust_norm'] == target].copy()
                else:
                    # limitar suma a clientes presentes en df_filtrado (evita sumar writeoffs de otros clientes)
                    clientes_presentes = df_filtrado['_cust_norm'].unique().tolist()
                    df_write_mes = df_write_mes[df_write_mes['_cust_norm'].isin(clientes_presentes)].copy()

            # A estas alturas df_write_mes contiene sólo filas del mes y de clientes relevantes
            # Convertir columna de monto a numérico y sumar. Preferimos columnas de tipo credit (write-off suele ser crédito)
            df_write_mes[amount_col] = pd.to_numeric(df_write_mes[amount_col], errors='coerce').fillna(0)

            # Muchas veces los write-offs aparecen como créditos (valores positivos en 'Credit'), si tu dataset tiene señales distintas,
            # el resultado puede invertirse — aquí asumimos que la columna contiene el monto a sumar tal cual.
            writeoffs_mes = df_write_mes[amount_col].sum()

            # defensiva: si el monto es ridículamente grande, no hacemos nada automático — dejamos que el usuario revise.
            if abs(writeoffs_mes) > 1e10:
                st.warning("El total calculado de Write Offs para el mes parece anómalo (muy grande). Por favor revisa la hoja 'Write off'.")
        except Exception:
            writeoffs_mes = 0

# formateo texto writeoffs (igual que tu DAX)
if writeoffs_mes == 0 or pd.isna(writeoffs_mes):
    writeoffs_texto = "Sin Write offs"
else:
    writeoffs_texto = f"${writeoffs_mes:,.2f}"

# ===== TARJETAS DE MÉTRICAS (2 filas) =====
r1c1, r1c2, r1c3, r1c4, r1c5, r1c6 = st.columns(6)
r1c1.metric("🗓 Año", año_sel)
r1c2.metric("📆 mes seleccionado", mes_sel)
r1c3.write("")
r1c4.write("")
r1c5.write("")
r1c6.write("")

st.markdown("")  # separación

r2c1, r2c2, r2c3, r2c4 = st.columns(4)
r2c1.metric("💰 Total mes anterior", f"${total_anterior:,.2f}")
r2c2.metric("💰 Total mes actual", f"${total_actual:,.2f}")
r2c3.metric("💸 Write Offs", writeoffs_texto)
r2c4.metric("📈 Variación %", f"{variacion_pct:.2f}%")

st.markdown("---")

# ===== TABLA DE CLIENTES =====
st.subheader(f"📋 Total de Provisiones - {año_sel}-{mes_sel:02d}")
df_tabla = df_filtrado.groupby(['Infor Code', 'Customer'], as_index=False)['Total Provision'].sum()
suma_total_prov = df_tabla['Total Provision'].sum()
df_tabla['% del Total'] = (df_tabla['Total Provision'] / suma_total_prov * 100) if suma_total_prov != 0 else 0

st.dataframe(
    df_tabla.style.format({
        "Total Provision": "${:,.2f}",
        "% del Total": "{:.2f}%"
    })
)

# ===== EVOLUCIÓN DE LOS ÚLTIMOS 5 MESES =====
periodo_sel = pd.Period(fecha_sel, freq='M')
ultimos_5 = [periodo_sel - i for i in range(4, -1, -1)]
df_ultimos_5 = df[df['AñoMes'].isin(ultimos_5)].copy()

if busqueda:
    df_ultimos_5 = df_ultimos_5[
        df_ultimos_5['Customer'].str.contains(busqueda, case=False, na=False) |
        df_ultimos_5['Infor Code'].str.contains(busqueda, case=False, na=False)
    ]
if cliente_detalle and cliente_detalle != 'Todos':
    df_ultimos_5 = df_ultimos_5[df_ultimos_5['Customer'] == cliente_detalle].copy()

df_agrupado = (
    df_ultimos_5
    .groupby('AñoMes', as_index=False)['Total Provision']
    .sum()
    .sort_values('AñoMes')
)
df_agrupado['AñoMes_label'] = df_agrupado['AñoMes'].dt.to_timestamp().dt.strftime('%b %Y')

y_max = 50000 if busqueda or (cliente_detalle and cliente_detalle != 'Todos') else 200000

fig_linea = px.line(
    df_agrupado,
    x='AñoMes_label',
    y='Total Provision',
    markers=True,
    title="Evolución mensual de la Provisión Total",
    color_discrete_sequence=['#0072B2']
)
fig_linea.update_traces(line=dict(width=4), marker=dict(size=8))
fig_linea.update_yaxes(
    range=[100000, y_max],
    tick0=100000,
    dtick=50000,
    tickformat=",",
    showgrid=True,
    gridwidth=1,
    gridcolor="rgba(200,200,200,0.35)",
    griddash="dash"
)
fig_linea.update_xaxes(
    title_text="Mes",
    tickmode='array',
    tickvals=df_agrupado['AñoMes_label'],
    ticktext=df_agrupado['AñoMes_label'],
    showgrid=False
)
fig_linea.update_layout(
    yaxis_title="Total Provision ($)",
    xaxis_title="Mes",
    template="plotly_white",
    margin=dict(l=40, r=20, t=60, b=40),
    title_x=0.02
)

st.subheader("📈 Evolución de Total Provision (Últimos 5 meses)")
st.plotly_chart(fig_linea, use_container_width=True)

# ===== COMPARATIVO DE RANGOS =====
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

st.markdown("---")
st.caption("Desarrollado en Streamlit – Dashboard Provisiones © 2025")
