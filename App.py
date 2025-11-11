import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(page_title="Provision Cartera USA", layout="wide")

# ===== PALETA DE COLORES CORPORATIVOS =====
COLOR_PALETTE = [
    '#85994C',  # Verde Oliva/Verde Musgo
    '#B0C950',  # Verde Chartreuse/Lima
    '#A5333F',  # Rojo Borgoña/Vino
    '#A59288',  # Beige/Topo Claro
    '#775F4A',  # Marrón Oscuro/Café
    '#D9733D',  # Naranja Quemado/Óxido
    '#99687B',  # Malva/Ciruela Rosácea
    '#5E3B42'   # Marrón Vino/Borgoña Oscuro
]

# ===== CSS MEJORADO - FONDO BLANCO COMPLETO =====
st.markdown(
    """
    <style>
    /* FONDO PRINCIPAL - BLANCO SOLIDO */
    .stApp {
        background-color: #FFFFFF !important;
        background-image: none !important;
    }
    
    /* CONTENEDOR PRINCIPAL TRANSPARENTE */
    .main .block-container {
        background-color: transparent !important;
        padding: 20px;
        margin: 0px;
    }
    
    /* HEADER CON FONDO BLANCO Y BORDES COLOR CORPORATIVO */
    .header-box {
        background: #FFFFFF;
        padding: 25px;
        border-radius: 15px;
        border: 3px solid #A5333F;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* TÍTULOS EN NEGRO */
    h1, h2, h3, h4, h5, h6 { 
        color: #000000 !important; 
        font-weight: 700 !important;
    }
    
    /* TEXTO GENERAL EN NEGRO */
    p, span, div, label, .stMarkdown, .stSubheader { 
        color: #000000 !important; 
        font-weight: 500 !important;
    }
    
    /* MÉTRICAS CON FONDO BLANCO Y BORDE COLOR CORPORATIVO */
    [data-testid="metric-container"] {
        background: #FFFFFF !important;
        border: 2px solid #85994C;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* LABELS DE MÉTRICAS EN NEGRO */
    [data-testid="metric-label"] {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* VALORES DE MÉTRICAS EN NEGRO */
    [data-testid="metric-value"] {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 24px !important;
    }
    
    /* DELTA DE MÉTRICAS - COLOR CORPORATIVO */
    [data-testid="metric-delta"] {
        color: #A5333F !important;
        font-weight: 600 !important;
    }
    
    /* GRÁFICOS CON FONDO BLANCO */
    .js-plotly-plot, .plotly {
        background-color: #FFFFFF !important;
        border-radius: 12px;
        border: 1px solid #DDDDDD;
    }
    
    /* TÍTULOS DE GRÁFICOS EN NEGRO */
    .gtitle, .xtitle, .ytitle {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* EJES Y TEXTO DE GRÁFICOS EN NEGRO */
    .xtick text, .ytick text, .legend text {
        color: #000000 !important;
    }
    
    /* LÍNEAS DE GRID EN GRÁFICOS */
    .gridlayer .xgrid, .gridlayer .ygrid {
        stroke: rgba(0,0,0,0.1) !important;
    }
    
    /* SIDEBAR CON FONDO BLANCO */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #FFFFFF !important;
        border-right: 2px solid #A5333F;
    }
    
    /* TEXTO DEL SIDEBAR EN NEGRO */
    .stSidebar h1, .stSidebar h2, .stSidebar h3, 
    .stSidebar p, .stSidebar label, .stSidebar div {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* INPUTS DEL SIDEBAR */
    .stTextInput input, .stSelectbox select, .stSelectbox span {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        border: 2px solid #85994C !important;
        border-radius: 8px;
        font-weight: 500 !important;
    }
    
    /* DATAFRAME CON FONDO BLANCO */
    .dataframe {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        border: 2px solid #A5333F;
    }
    
    /* BOTONES MEJORADOS */
    .stButton button {
        background-color: #A5333F;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #5E3B42;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* SEPARADORES CON COLOR CORPORATIVO */
    .stMarkdown hr {
        margin: 2rem 0;
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent, #A5333F, transparent);
    }
    
    /* CONTENEDOR DE GRÁFICOS CON FONDO BLANCO */
    .element-container {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #DDDDDD;
    }
    
    /* REMOVER CUALQUIER OVERLAY OSCURO */
    .stApp::before {
        content: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== ENCABEZADO MEJORADO =====
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/Logo.png", width=300)  # Logo más grande
with col2:
    st.markdown(
        """
        <div class="header-box">
        <h1 style="margin:0; text-align:center; color: #A5333F !important; font-size: 2.5rem; font-weight: 800;">
        📊 PROVISION CARTERA USA
        </h1>
        <p style="margin:10px 0 0 0; text-align:center; color: #333 !important; font-size: 1.2rem; font-weight: 600;">
        Dashboard de Análisis y Gestión
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
# ===== CARGA DE DATOS =====
@st.cache_data
def cargar_datos():
    df = pd.read_excel("Data/Base Provision.xlsx")
    df.columns = df.columns.str.strip()
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
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

# ===== SIDEBAR MEJORADO =====
with st.sidebar:
    st.markdown("### 🗓️ Filtros de Periodo")
    año_sel = st.selectbox("Seleccionar año:", sorted(df['Año'].unique(), reverse=True))
    meses_disponibles = sorted(df[df['Año'] == año_sel]['Mes'].unique())
    mes_sel = st.selectbox("Seleccionar mes:", meses_disponibles)
    
    st.markdown("---")
    st.markdown("### 🔍 Buscador")
    
    # Inicializar session_state para búsqueda
    if 'busqueda' not in st.session_state:
        st.session_state.busqueda = ''
    if 'cliente_detalle' not in st.session_state:
        st.session_state.cliente_detalle = 'Todos'
    
    # Buscador funcional
    busqueda_input = st.text_input(
        "Buscar Cliente o Infor Code:",
        value=st.session_state.busqueda,
        placeholder="Escribe para buscar...",
        key="busqueda_input"
    )
    
    # Actualizar session_state cuando cambia la búsqueda
    if busqueda_input != st.session_state.busqueda:
        st.session_state.busqueda = busqueda_input
    
    st.markdown("### 👥 Selección de Cliente")
    clientes_list = sorted(df['Customer'].dropna().unique().tolist())
    cliente_options = ['Todos'] + clientes_list
    
    cliente_seleccionado = st.selectbox(
        "Seleccionar Cliente:",
        cliente_options,
        index=cliente_options.index(st.session_state.cliente_detalle) if st.session_state.cliente_detalle in cliente_options else 0,
        key="cliente_select"
    )
    
    # Actualizar session_state cuando cambia la selección
    if cliente_seleccionado != st.session_state.cliente_detalle:
        st.session_state.cliente_detalle = cliente_seleccionado
    
    def _clear_filters():
        st.session_state.busqueda = ''
        st.session_state.cliente_detalle = 'Todos'
        st.rerun()
    
    if st.button("🧹 Limpiar Filtros", use_container_width=True):
        _clear_filters()

# ===== FILTRADO PRINCIPAL POR AÑO/MES =====
df_filtrado = df[(df['Año'] == año_sel) & (df['Mes'] == mes_sel)].copy()

# Aplicar filtros de búsqueda
if st.session_state.busqueda:
    df_filtrado = df_filtrado[
        df_filtrado['Customer'].str.contains(st.session_state.busqueda, case=False, na=False) |
        df_filtrado['Infor Code'].str.contains(st.session_state.busqueda, case=False, na=False)
    ]

if st.session_state.cliente_detalle and st.session_state.cliente_detalle != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Customer'] == st.session_state.cliente_detalle].copy()

# ===== MES ANTERIOR =====
fecha_sel = pd.Timestamp(año_sel, mes_sel, 1)
fecha_ant = fecha_sel - relativedelta(months=1)
df_mes_ant = df[(df['Fecha'].dt.year == fecha_ant.year) & (df['Fecha'].dt.month == fecha_ant.month)].copy()

# Aplicar mismos filtros al mes anterior
if st.session_state.busqueda:
    df_mes_ant = df_mes_ant[
        df_mes_ant['Customer'].str.contains(st.session_state.busqueda, case=False, na=False) |
        df_mes_ant['Infor Code'].str.contains(st.session_state.busqueda, case=False, na=False)
    ]
if st.session_state.cliente_detalle and st.session_state.cliente_detalle != 'Todos':
    df_mes_ant = df_mes_ant[df_mes_ant['Customer'] == st.session_state.cliente_detalle].copy()

# ===== CÁLCULO DE MÉTRICAS =====
total_actual = df_filtrado['Total Provision'].sum()
total_anterior = df_mes_ant['Total Provision'].sum() if not df_mes_ant.empty else 0
variacion_abs = total_actual - total_anterior
variacion_pct = (variacion_abs / total_anterior * 100) if total_anterior != 0 else 0.0

# ===== CÁLCULO DE WRITE OFF MEJORADO =====
writeoffs_mes = 0

if not df_write.empty:
    cols = [c.strip() for c in df_write.columns.tolist()]
    df_write.columns = cols
    
    date_col = next((c for c in cols if any(x in c.lower() for x in ['date', 'fecha'])), None)
    amount_col = next((c for c in cols if any(x in c.lower() for x in ['amount', 'monto', 'valor', 'credit', 'debit'])), None)
    cust_col = next((c for c in cols if any(x in c.lower() for x in ['cust', 'vendor', 'customer', 'name'])), None)
    
    if date_col and amount_col:
        df_write[date_col] = pd.to_datetime(df_write[date_col], errors='coerce')
        
        df_write_mes = df_write[
            (df_write[date_col].dt.year == año_sel) & 
            (df_write[date_col].dt.month == mes_sel)
        ].copy()
        
        if cust_col:
            df_write_mes = df_write_mes[
                df_write_mes[cust_col].notna() &
                ~df_write_mes[cust_col].astype(str).str.strip().str[:3].str.upper().eq('INT')
            ]
            
            if st.session_state.cliente_detalle and st.session_state.cliente_detalle != 'Todos':
                df_write_mes = df_write_mes[
                    df_write_mes[cust_col].astype(str).str.strip().str.upper() == 
                    st.session_state.cliente_detalle.strip().upper()
                ]
            elif st.session_state.busqueda:
                df_write_mes = df_write_mes[
                    df_write_mes[cust_col].str.contains(st.session_state.busqueda, case=False, na=False)
                ]
        
        df_write_mes[amount_col] = pd.to_numeric(df_write_mes[amount_col], errors='coerce').fillna(0)
        writeoffs_mes = df_write_mes[amount_col].sum()

# Formatear texto de Write Offs
if writeoffs_mes == 0 or pd.isna(writeoffs_mes):
    writeoffs_texto = "Sin Write offs"
else:
    writeoffs_texto = f"${writeoffs_mes:,.0f}"

# ===== MÉTRICAS REORGANIZADAS =====
st.markdown(f"### 📊 Resumen - {mes_sel}/{año_sel}")

# Primera línea - Año y Mes
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🗓️ Año", año_sel)
with col2:
    st.metric("📅 Mes", mes_sel)
with col3:
    st.write("")
with col4:
    st.write("")

# Segunda línea - Métricas financieras
col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("💰 Mes Anterior", f"${total_anterior:,.0f}")
with col6:
    st.metric("💸 Write Offs", writeoffs_texto)
with col7:
    st.metric("💰 Mes Actual", f"${total_actual:,.0f}")
with col8:
    delta_text = f"${variacion_abs:,.0f} | {variacion_pct:+.1f}%"
    st.metric("📈 Variación", f"${variacion_abs:,.0f}", delta=f"{variacion_pct:+.1f}%")

st.markdown("---")

# ===== TABLA DE CLIENTES =====
st.subheader(f"📋 Detalle de Provisiones por Cliente")
df_tabla = df_filtrado.groupby(['Infor Code', 'Customer'], as_index=False)['Total Provision'].sum()
suma_total_prov = df_tabla['Total Provision'].sum()
df_tabla['% del Total'] = (df_tabla['Total Provision'] / suma_total_prov * 100) if suma_total_prov != 0 else 0

# Ordenar por provision descendente
df_tabla = df_tabla.sort_values('Total Provision', ascending=False)

# Aplicar formato
styled_df = df_tabla.style.format({
    "Total Provision": "${:,.2f}",
    "% del Total": "{:.2f}%"
})

st.dataframe(
    styled_df,
    use_container_width=True,
    height=400
)

st.markdown("---")

# ===== EVOLUCIÓN DE LOS ÚLTIMOS 5 MESES =====
periodo_sel = pd.Period(fecha_sel, freq='M')
ultimos_5 = [periodo_sel - i for i in range(4, -1, -1)]
df_ultimos_5 = df[df['AñoMes'].isin(ultimos_5)].copy()

# Aplicar filtros
if st.session_state.busqueda:
    df_ultimos_5 = df_ultimos_5[
        df_ultimos_5['Customer'].str.contains(st.session_state.busqueda, case=False, na=False) |
        df_ultimos_5['Infor Code'].str.contains(st.session_state.busqueda, case=False, na=False)
    ]
if st.session_state.cliente_detalle and st.session_state.cliente_detalle != 'Todos':
    df_ultimos_5 = df_ultimos_5[df_ultimos_5['Customer'] == st.session_state.cliente_detalle].copy()

df_agrupado = (
    df_ultimos_5
    .groupby('AñoMes', as_index=False)['Total Provision']
    .sum()
    .sort_values('AñoMes')
)
df_agrupado['AñoMes_label'] = df_agrupado['AñoMes'].dt.to_timestamp().dt.strftime('%b %Y')

# Gráfico de línea con colores corporativos
fig_linea = px.line(
    df_agrupado,
    x='AñoMes_label',
    y='Total Provision',
    markers=True,
    title="Evolución Mensual de la Provisión Total",
    color_discrete_sequence=[COLOR_PALETTE[1]]  # Verde Lima
)

# Configurar gráfico con tema claro
fig_linea.update_traces(
    line=dict(width=4), 
    marker=dict(size=8),
    hovertemplate="<b>%{x}</b><br>Provision: $%{y:,.0f}<extra></extra>"
)

fig_linea.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='black', size=12),
    xaxis=dict(
        title_text="Mes",
        showgrid=False,
        tickfont=dict(color='black')
    ),
    yaxis=dict(
        title_text="Total Provision ($)",
        tickformat=",",
        showgrid=True,
        gridcolor='rgba(0,0,0,0.1)',
        tickfont=dict(color='black')
    ),
    title=dict(
        font=dict(color='black', size=16)
    ),
    margin=dict(l=40, r=20, t=60, b=40)
)

st.subheader("📈 Evolución de Total Provision (Últimos 5 meses)")
st.plotly_chart(fig_linea, use_container_width=True)

# ===== COMPARATIVO DE RANGOS =====
st.subheader("🥧 Distribución de Provisión por Rango de Edad")

df_pie_ant = df_mes_ant if not df_mes_ant.empty else df_filtrado.copy()
totales_ant = df_pie_ant[['Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360']].sum().to_dict()
totales_act = df_filtrado[['Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360']].sum().to_dict()

# Crear DataFrames para los gráficos de pie
df_pie_ant = pd.DataFrame(list(totales_ant.items()), columns=['Rango', 'Total'])
df_pie_act = pd.DataFrame(list(totales_act.items()), columns=['Rango', 'Total'])

# Mejorar nombres de rangos
rango_names = {
    'Provision 91-180': '91-180 días',
    'Provision 181-270': '181-270 días', 
    'Provision 271-360': '271-360 días',
    'Provision >360': '>360 días'
}
df_pie_ant['Rango'] = df_pie_ant['Rango'].map(rango_names)
df_pie_act['Rango'] = df_pie_act['Rango'].map(rango_names)

col_pie1, col_pie2 = st.columns(2)

with col_pie1:
    fig_pie_ant = px.pie(
        df_pie_ant, 
        values='Total', 
        names='Rango',
        title=f"Mes Anterior ({fecha_ant.strftime('%Y-%m')})",
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_pie_ant.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont=dict(color='white', size=12)
    )
    fig_pie_ant.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black'),
        title=dict(font=dict(color='black')),
        legend=dict(font=dict(color='black'))
    )
    st.plotly_chart(fig_pie_ant, use_container_width=True)

with col_pie2:
    fig_pie_act = px.pie(
        df_pie_act, 
        values='Total', 
        names='Rango',
        title=f"Mes Actual ({año_sel}-{mes_sel:02d})",
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_pie_act.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont=dict(color='black', size=12)
    )
    fig_pie_act.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title=dict(font=dict(color='black')),
        legend=dict(font=dict(color='black'))
    )
    st.plotly_chart(fig_pie_act, use_container_width=True)

# ===== PIE DE PÁGINA =====
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #cccccc; padding: 20px;'>
        <p style='margin: 0; font-size: 0.9rem;'>📊 <strong>Provision Cartera USA</strong> | Desarrollado en Streamlit</p>
        <p style='margin: 5px 0 0 0; font-size: 0.8rem;'>© 2025 - Dashboard de provisiones contables</p>
    </div>
    """,
    unsafe_allow_html=True
)
