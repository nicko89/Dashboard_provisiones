import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(
    page_title="Provision Cartera USA",
    layout="wide",
    page_icon="📊"
)

# ===== PALETA DE COLORES PROFESIONAL =====
COLOR_PALETTE = [
    '#2E86AB',  # Azul profesional
    '#A23B72',  # Magenta corporativo
    '#F18F01',  # Naranja energético
    '#C73E1D',  # Rojo terroso
    '#3B8EA5',  # Azul claro
    '#6A8EAE',  # Azul grisáceo
    '#F0B67F',  # Durazno suave
    '#5B8E7D'   # Verde azulado
]

# ===== TEMA PROFESIONAL - DISEÑO LIMPIO =====
st.markdown("""
<style>
    /* FONDO BLANCO PROFESIONAL */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* CONTENEDOR PRINCIPAL */
    .main .block-container {
        background-color: #FFFFFF;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* HEADER ELEGANTE */
    .header-container {
        background: linear-gradient(135deg, #2E86AB 0%, #3B8EA5 100%);
        padding: 2.5rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(46, 134, 171, 0.15);
        text-align: center;
        color: white;
    }
    
    /* TIPOGRAFÍA PROFESIONAL */
    h1, h2, h3 {
        color: #2C3E50 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    h1 {
        font-size: 2.5rem;
        color: white !important;
    }
    
    h2 {
        font-size: 1.8rem;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    h3 {
        font-size: 1.4rem;
        color: #34495E !important;
    }
    
    /* MÉTRICAS ELEGANTES */
    [data-testid="metric-container"] {
        background: #F8F9FA;
        border: 1px solid #E9ECEF;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }
    
    [data-testid="metric-label"] {
        color: #6C757D !important;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    [data-testid="metric-value"] {
        color: #2C3E50 !important;
        font-weight: 700;
        font-size: 1.8rem;
    }
    
    [data-testid="metric-delta"] {
        font-weight: 600;
    }
    
    /* SIDEBAR MODERNO */
    [data-testid="stSidebar"] {
        background: #F8F9FA;
        border-right: 1px solid #E9ECEF;
    }
    
    .stSidebar h3 {
        color: #2E86AB !important;
        border-bottom: 1px solid #2E86AB;
        padding-bottom: 0.5rem;
    }
    
    /* BOTONES ELEGANTES */
    .stButton button {
        background: linear-gradient(135deg, #2E86AB 0%, #3B8EA5 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(46, 134, 171, 0.3);
    }
    
    /* INPUTS MODERNOS */
    .stTextInput input, .stSelectbox select, .stSelectbox span {
        border: 1px solid #CED4DA;
        border-radius: 8px;
        padding: 0.5rem;
        background: white;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #2E86AB;
        box-shadow: 0 0 0 2px rgba(46, 134, 171, 0.1);
    }
    
    /* TABLAS ELEGANTES */
    .dataframe {
        background: white !important;
        border: 1px solid #E9ECEF;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* GRÁFICOS CON ESTILO */
    .js-plotly-plot, .plotly {
        background: white !important;
        border-radius: 10px;
        border: 1px solid #E9ECEF;
    }
    
    /* SEPARADORES */
    .stMarkdown hr {
        margin: 2.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #2E86AB, transparent);
    }
    
    /* TARJETAS DE CONTENIDO */
    .content-card {
        background: white;
        border: 1px solid #E9ECEF;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* MEJORAS DE ESPACIADO */
    .st-emotion-cache-1y4p8pa {
        padding: 2rem 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ===== ENCABEZADO ELEGANTE =====
st.markdown("""
<div class="header-container">
    <h1>📊 DASHBOARD DE PROVISIONES</h1>
    <p style="font-size: 1.2rem; opacity: 0.9; margin: 0;">Análisis y Gestión de Cartera USA</p>
</div>
""", unsafe_allow_html=True)

# ===== CARGA DE DATOS =====
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("Data/Base Provision.xlsx")
        df.columns = df.columns.str.strip()
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        
        try:
            df_write = pd.read_excel("Data/Base Provision.xlsx", sheet_name="Write off")
            df_write.columns = df_write.columns.str.strip()
        except Exception:
            df_write = pd.DataFrame()
            
        return df, df_write
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

df, df_write = cargar_datos()

if df.empty:
    st.warning("No se pudieron cargar los datos. Verifique la conexión con los archivos.")
    st.stop()

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

# ===== SIDEBAR PROFESIONAL =====
with st.sidebar:
    st.markdown("### 🎛️ Panel de Control")
    
    # Filtros de periodo
    st.markdown("**Filtros de Periodo**")
    año_sel = st.selectbox("Año:", sorted(df['Año'].unique(), reverse=True))
    meses_disponibles = sorted(df[df['Año'] == año_sel]['Mes'].unique())
    mes_sel = st.selectbox("Mes:", meses_disponibles)
    
    st.markdown("---")
    
    # Buscador mejorado
    st.markdown("**🔍 Búsqueda Avanzada**")
    
    # Inicializar session_state
    if 'busqueda' not in st.session_state:
        st.session_state.busqueda = ''
    if 'cliente_detalle' not in st.session_state:
        st.session_state.cliente_detalle = 'Todos'
    
    # Buscador seguro
    busqueda_input = st.text_input(
        "Buscar cliente o código:",
        value=st.session_state.busqueda,
        placeholder="Ingrese nombre o código...",
        key="busqueda_input"
    )
    
    # Actualizar session_state
    if busqueda_input != st.session_state.busqueda:
        st.session_state.busqueda = busqueda_input
    
    # Selección de cliente
    clientes_list = sorted(df['Customer'].dropna().unique().tolist())
    cliente_options = ['Todos los clientes'] + clientes_list
    
    cliente_seleccionado = st.selectbox(
        "Cliente específico:",
        cliente_options,
        index=cliente_options.index(st.session_state.cliente_detalle) if st.session_state.cliente_detalle in cliente_options else 0,
        key="cliente_select"
    )
    
    if cliente_seleccionado != st.session_state.cliente_detalle:
        st.session_state.cliente_detalle = cliente_seleccionado
    
    # Botón de limpiar
    if st.button("🔄 Restablecer Filtros", use_container_width=True):
        st.session_state.busqueda = ''
        st.session_state.cliente_detalle = 'Todos los clientes'
        st.rerun()
    
    st.markdown("---")
    st.markdown("*Dashboard desarrollado para análisis de provisiones*")

# ===== FILTRADO PRINCIPAL =====
df_filtrado = df[(df['Año'] == año_sel) & (df['Mes'] == mes_sel)].copy()

# Aplicar filtros de búsqueda de forma segura
if st.session_state.busqueda:
    mask = (
        df_filtrado['Customer'].astype(str).str.contains(st.session_state.busqueda, case=False, na=False) |
        df_filtrado['Infor Code'].astype(str).str.contains(st.session_state.busqueda, case=False, na=False)
    )
    df_filtrado = df_filtrado[mask]

if st.session_state.cliente_detalle and st.session_state.cliente_detalle != 'Todos los clientes':
    df_filtrado = df_filtrado[df_filtrado['Customer'] == st.session_state.cliente_detalle]

# ===== MES ANTERIOR =====
fecha_sel = pd.Timestamp(año_sel, mes_sel, 1)
fecha_ant = fecha_sel - relativedelta(months=1)
df_mes_ant = df[(df['Fecha'].dt.year == fecha_ant.year) & (df['Fecha'].dt.month == fecha_ant.month)].copy()

# Aplicar mismos filtros al mes anterior
if st.session_state.busqueda:
    mask_ant = (
        df_mes_ant['Customer'].astype(str).str.contains(st.session_state.busqueda, case=False, na=False) |
        df_mes_ant['Infor Code'].astype(str).str.contains(st.session_state.busqueda, case=False, na=False)
    )
    df_mes_ant = df_mes_ant[mask_ant]

if st.session_state.cliente_detalle and st.session_state.cliente_detalle != 'Todos los clientes':
    df_mes_ant = df_mes_ant[df_mes_ant['Customer'] == st.session_state.cliente_detalle]

# ===== CÁLCULO DE MÉTRICAS =====
total_actual = df_filtrado['Total Provision'].sum()
total_anterior = df_mes_ant['Total Provision'].sum() if not df_mes_ant.empty else 0
variacion_abs = total_actual - total_anterior
variacion_pct = (variacion_abs / total_anterior * 100) if total_anterior != 0 else 0.0

# ===== CÁLCULO DE WRITE OFF MEJORADO Y SEGURO =====
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
        
        if cust_col and not df_write_mes.empty:
            # Asegurar que la columna sea string antes de usar .str
            df_write_mes[cust_col] = df_write_mes[cust_col].astype(str)
            
            # Filtrar INT
            df_write_mes = df_write_mes[
                df_write_mes[cust_col].notna() &
                ~df_write_mes[cust_col].str.strip().str[:3].str.upper().eq('INT')
            ]
            
            # Aplicar filtros de búsqueda
            if st.session_state.cliente_detalle and st.session_state.cliente_detalle != 'Todos los clientes':
                df_write_mes = df_write_mes[
                    df_write_mes[cust_col].str.strip().str.upper() == 
                    st.session_state.cliente_detalle.strip().upper()
                ]
            elif st.session_state.busqueda:
                df_write_mes = df_write_mes[
                    df_write_mes[cust_col].str.contains(st.session_state.busqueda, case=False, na=False)
                ]
        
        if not df_write_mes.empty and amount_col in df_write_mes.columns:
            df_write_mes[amount_col] = pd.to_numeric(df_write_mes[amount_col], errors='coerce').fillna(0)
            writeoffs_mes = df_write_mes[amount_col].sum()

writeoffs_texto = "Sin Write offs" if writeoffs_mes == 0 or pd.isna(writeoffs_mes) else f"${writeoffs_mes:,.0f}"

# ===== TARJETAS DE MÉTRICAS PRINCIPALES =====
st.markdown("### 📈 Resumen Ejecutivo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Provisión Actual",
        value=f"${total_actual:,.0f}",
        delta=f"${variacion_abs:,.0f}" if variacion_abs != 0 else None,
        delta_color="normal" if variacion_abs >= 0 else "inverse"
    )

with col2:
    st.metric(
        label="Provisión Anterior", 
        value=f"${total_anterior:,.0f}",
        delta=f"{variacion_pct:+.1f}%" if total_anterior != 0 else "N/A"
    )

with col3:
    st.metric(
        label="Write Offs",
        value=writeoffs_texto
    )

with col4:
    st.metric(
        label="Clientes Activos",
        value=f"{len(df_filtrado['Customer'].unique()):,}"
    )

st.markdown("---")

# ===== TABLA DE CLIENTES MEJORADA =====
st.markdown("### 👥 Detalle por Cliente")

if not df_filtrado.empty:
    df_tabla = df_filtrado.groupby(['Infor Code', 'Customer'], as_index=False)['Total Provision'].sum()
    suma_total_prov = df_tabla['Total Provision'].sum()
    df_tabla['% del Total'] = (df_tabla['Total Provision'] / suma_total_prov * 100) if suma_total_prov != 0 else 0
    df_tabla = df_tabla.sort_values('Total Provision', ascending=False)

    # Formatear la tabla
    styled_df = df_tabla.style.format({
        "Total Provision": "${:,.2f}",
        "% del Total": "{:.2f}%"
    }).background_gradient(subset=['Total Provision'], cmap='Blues')

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )
else:
    st.info("No hay datos disponibles para los filtros seleccionados.")

st.markdown("---")

# ===== GRÁFICO DE EVOLUCIÓN =====
st.markdown("### 📊 Evolución Temporal")

periodo_sel = pd.Period(fecha_sel, freq='M')
ultimos_5 = [periodo_sel - i for i in range(4, -1, -1)]
df_ultimos_5 = df[df['AñoMes'].isin(ultimos_5)].copy()

# Aplicar filtros de forma segura
if st.session_state.busqueda:
    mask_5 = (
        df_ultimos_5['Customer'].astype(str).str.contains(st.session_state.busqueda, case=False, na=False) |
        df_ultimos_5['Infor Code'].astype(str).str.contains(st.session_state.busqueda, case=False, na=False)
    )
    df_ultimos_5 = df_ultimos_5[mask_5]

if st.session_state.cliente_detalle and st.session_state.cliente_detalle != 'Todos los clientes':
    df_ultimos_5 = df_ultimos_5[df_ultimos_5['Customer'] == st.session_state.cliente_detalle]

if not df_ultimos_5.empty:
    df_agrupado = (
        df_ultimos_5
        .groupby('AñoMes', as_index=False)['Total Provision']
        .sum()
        .sort_values('AñoMes')
    )
    df_agrupado['AñoMes_label'] = df_agrupado['AñoMes'].dt.to_timestamp().dt.strftime('%b %Y')

    fig_linea = px.line(
        df_agrupado,
        x='AñoMes_label',
        y='Total Provision',
        markers=True,
        title="Tendencia de Provisiones - Últimos 5 Meses",
        color_discrete_sequence=[COLOR_PALETTE[0]]
    )

    fig_linea.update_traces(
        line=dict(width=3),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Provision: $%{y:,.0f}<extra></extra>"
    )

    fig_linea.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2C3E50'),
        xaxis=dict(
            title_text="Periodo",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            tickfont=dict(color='#2C3E50')
        ),
        yaxis=dict(
            title_text="Total Provisión ($)",
            tickformat=",",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            tickfont=dict(color='#2C3E50')
        ),
        title=dict(
            font=dict(color='#2C3E50', size=16)
        ),
        margin=dict(l=40, r=20, t=60, b=40)
    )

    st.plotly_chart(fig_linea, use_container_width=True)
else:
    st.info("No hay datos suficientes para mostrar la evolución temporal.")

# ===== COMPARATIVO DE RANGOS =====
st.markdown("### 🥧 Distribución por Antigüedad")

col_pie1, col_pie2 = st.columns(2)

with col_pie1:
    if not df_mes_ant.empty:
        df_pie_ant = df_mes_ant.copy()
    else:
        df_pie_ant = df_filtrado.copy()
    
    totales_ant = df_pie_ant[['Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360']].sum().to_dict()
    df_pie_ant = pd.DataFrame(list(totales_ant.items()), columns=['Rango', 'Total'])
    
    rango_names = {
        'Provision 91-180': '91-180 días',
        'Provision 181-270': '181-270 días', 
        'Provision 271-360': '271-360 días',
        'Provision >360': '>360 días'
    }
    df_pie_ant['Rango'] = df_pie_ant['Rango'].map(rango_names)
    
    fig_pie_ant = px.pie(
        df_pie_ant, 
        values='Total', 
        names='Rango',
        title=f"Distribución Anterior ({fecha_ant.strftime('%b %Y')})",
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_pie_ant.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont=dict(size=11)
    )
    fig_pie_ant.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2C3E50')
    )
    st.plotly_chart(fig_pie_ant, use_container_width=True)

with col_pie2:
    totales_act = df_filtrado[['Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360']].sum().to_dict()
    df_pie_act = pd.DataFrame(list(totales_act.items()), columns=['Rango', 'Total'])
    df_pie_act['Rango'] = df_pie_act['Rango'].map(rango_names)
    
    fig_pie_act = px.pie(
        df_pie_act, 
        values='Total', 
        names='Rango',
        title=f"Distribución Actual ({año_sel}-{mes_sel:02d})",
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_pie_act.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont=dict(size=11)
    )
    fig_pie_act.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2C3E50')
    )
    st.plotly_chart(fig_pie_act, use_container_width=True)

# ===== PIE DE PÁGINA ELEGANTE =====
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6C757D; padding: 2rem 0;'>
    <p style='margin: 0; font-size: 0.9rem; font-weight: 500;'>
        📊 <strong>Dashboard de Provisiones Cartera USA</strong> | Desarrollado con Streamlit
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem;'>
        Sistema de análisis financiero profesional • © 2025
    </p>
</div>
""", unsafe_allow_html=True)
