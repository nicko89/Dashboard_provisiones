import streamlit as st 
import pandas as pd
import plotly.express as px
from dateutil.relativedelta import relativedelta

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(
    page_title="Provision Cartera USA", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== FORZAR TEMA CLARO =====
st._config.set_option("theme.base", "light")
st._config.set_option("theme.primaryColor", "#2E7D32")
st._config.set_option("theme.backgroundColor", "#FFFFFF")
st._config.set_option("theme.secondaryBackgroundColor", "#F5F5F5")
st._config.set_option("theme.textColor", "#000000")

# ===== Contraseña =====

PASSWORD = st.secrets.get("PASSWORD","Deco.2025*")   

def login_screen():
    placeholder = st.empty()   

    with placeholder.container():
        st.markdown("## 🔐 Acceso restringido")
        password = st.text_input("Introduce la contraseña:", type="password")
        entrar = st.button("Entrar")

    if entrar:
        if password == PASSWORD:
            st.session_state["logged_in"] = True
            placeholder.empty() 
            return True
        else:
            st.error("❌ Contraseña incorrecta")

    return False


# ===== VERIFICACIÓN =====
if not st.session_state.get("logged_in"):
    if not login_screen():
        st.stop() 

# ===== CSS ESTABLE + FORZAR TEMA CLARO =====
st.markdown("""
<style>

    /* ===============================================
       1. FORZAR TEMA CLARO (SIN ROMPER STREAMLIT)
       =============================================== */
    
    html, body {
        color-scheme: light !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    @media (prefers-color-scheme: dark) {
        html, body {
            color-scheme: light !important;
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
    }

    /* ===============================================
       2. FONDO GENERAL
       =============================================== */

    .stApp {
        background-image: url("https://github.com/nicko89/Dashboard_provisiones/blob/main/assets/Fondo.jpg?raw=true");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }

    .main .block-container {
        background: transparent !important;
    }

    /* ===============================================
       3. SIDEBAR
       =============================================== */

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-right: 1px solid #E0E0E0 !important;
    }

    /* ===============================================
       4. TEXTO GENERALES
       =============================================== */

    h1, h2, h3, h4, h5, h6,
    p, label, .stMarkdown, .stSubheader {
        color: #000000 !important;
    }

    .stSubheader {
        color: #2E7D32 !important;
    }

    /* ===============================================
       5. MÉTRICAS
       =============================================== */

    [data-testid="metric-container"] {
        background: #FFFFFF !important;
        border: 1px solid #D7CCC8 !important;
        border-radius: 8px;
        padding: 8px 16px;
    }

    [data-testid="stMetricValue"],
    [data-testid="metric-value"] {
        color: #000000 !important;
        font-weight: 600 !important;
    }

/* ===============================================
   6. TABLAS — FIX DEFINITIVO STREAMLIT 1.51 + AG-GRID
   =============================================== */

/* Contenedor de la tabla */
div[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
    padding: 4px !important;
    border-radius: 8px !important;
}

/* Fondo del wrapper */
div[data-testid="stDataFrame"] .ag-root-wrapper {
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
    border: 1px solid #E0E0E0 !important;
}

/* HEADER */
div[data-testid="stDataFrame"] .ag-header,
div[data-testid="stDataFrame"] .ag-header-cell,
div[data-testid="stDataFrame"] .ag-header-row {
    background-color: #F5F5F5 !important;
    color: #2E7D32 !important;
    font-weight: 600 !important;
    border-color: #D7CCC8 !important;
}

/* CELDAS */
div[data-testid="stDataFrame"] .ag-cell {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border-color: #E6E6E6 !important;
}

/* CELDAS FILA IMPAR */
div[data-testid="stDataFrame"] .ag-row-odd .ag-cell {
    background-color: #FAFAFA !important;
}

/* TEXTO DE TODA LA TABLA */
div[data-testid="stDataFrame"] * {
    color: #000000 !important;
}

    /* ===============================================
       7. PLOTLY — gráficos sin fondo oscuro
       =============================================== */

    .js-plotly-plot .plot-container .svg-container {
        background-color: rgba(255, 255, 255, 0) !important;
    }

            /* ================================
   SELECTBOX (nuevo motor BaseWeb)
   ================================ */

/* Contenedor del select */
div[data-baseweb="select"] > div {
    border: 2px solid #2E7D32 !important;     /* Color del borde */
    border-radius: 8px !important;            /* Bordes redondeados */
    background-color: #FFFFFF !important;     
    color: #000000 !important;
}

/* Al pasar el mouse */
div[data-baseweb="select"] > div:hover {
    border-color: #1B5E20 !important;
}

/* Al hacer foco (click) */
div[data-baseweb="select"] > div:focus-within {
    box-shadow: 0 0 0 3px rgba(46,125,50,0.25) !important;
    border-color: #1B5E20 !important;
}

/* ================================
   TEXT INPUT
   ================================ */

input[type="text"], textarea {
    border: 2px solid #2E7D32 !important;
    border-radius: 8px !important;
    background-color: #FFFFFF !important;
    color: #000000 !important;
    padding: 6px !important;
}

input[type="text"]:focus, textarea:focus {
    border-color: #1B5E20 !important;
    box-shadow: 0 0 0 3px rgba(46,125,50,0.25) !important;
    outline: none !important;
}
</style>
""", unsafe_allow_html=True)


# ===== PALETA DE COLORES =====
COLOR_PALETTE = [
    "#2E7D32",  # Verde hoja (principal)
    "#66BB6A",  # Verde claro
    "#FFD54F",  # Dorado suave
    "#E57373",  # Rosa floral
    "#D7CCC8",  # Beige arena
]

# ===== ENCABEZADO =====
col1, col2 = st.columns([1.2, 3])
with col1:
    st.image("assets/Logo.png", width= 400)
with col2:
    st.markdown(
        """
        <div class="header-box">
        <h1 style="margin:0; text-align:center; color: #1B5E20 !important; font-size: 3.2rem;">
        📊 Provision Cartera USA
        </h1>
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

# ===== SIDEBAR =====
with st.sidebar:
    # Última fecha registrada
    ultima_fecha = df['Fecha'].max()
    año_default = ultima_fecha.year
    mes_default = ultima_fecha.month

    año_sel = st.selectbox("Seleccionar año:", sorted(df['Año'].unique(), reverse=True), index=list(sorted(df['Año'].unique(), reverse=True)).index(año_default))
    meses_disponibles = sorted(df[df['Año'] == año_sel]['Mes'].unique())
    mes_sel = st.selectbox("Seleccionar mes:", meses_disponibles, index=meses_disponibles.index(mes_default))

    
    st.markdown("---")
    st.markdown("### 🔍 Buscador")

    # Inicializar valores en session_state antes de los widgets
    if 'busqueda' not in st.session_state:
        st.session_state['busqueda'] = ''
    if 'cliente_detalle' not in st.session_state:
        st.session_state['cliente_detalle'] = 'Todos'

    clientes_list = sorted(df['Customer'].dropna().unique().tolist())
    cliente_options = ['Todos'] + clientes_list
    
    st.text_input("Buscar Cliente o Infor Code:", 
                  key='busqueda', 
                  placeholder="Escribe para buscar...")

    st.markdown("### 👥 Selección de Cliente")
    st.selectbox("Seleccionar Cliente:", cliente_options, key='cliente_detalle')

    # ✅ Usar callback para limpiar filtros
    def _clear_filters():
        st.session_state['busqueda'] = ''
        st.session_state['cliente_detalle'] = 'Todos'

    st.button("🧹 Limpiar Filtros", 
              use_container_width=True, 
              on_click=_clear_filters)

# Acceso seguro a los valores
busqueda = st.session_state.get('busqueda', '')
cliente_detalle = st.session_state.get('cliente_detalle', 'Todos')


# ===== FILTRADO PRINCIPAL POR AÑO/MES =====
df_filtrado = df[(df['Año'] == año_sel) & (df['Mes'] == mes_sel)].copy()

if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado['Customer'].astype(str).str.contains(busqueda, case=False, na=False) |
        df_filtrado['Infor Code'].astype(str).str.contains(busqueda, case=False, na=False)
    ]

if cliente_detalle and cliente_detalle != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Customer'] == cliente_detalle].copy()

# ===== MES ANTERIOR =====
fecha_sel = pd.Timestamp(año_sel, mes_sel, 1)
fecha_ant = fecha_sel - relativedelta(months=1)
df_mes_ant = df[(df['Fecha'].dt.year == fecha_ant.year) & (df['Fecha'].dt.month == fecha_ant.month)].copy()

if busqueda:
    df_mes_ant = df_mes_ant[
        df_mes_ant['Customer'].astype(str).str.contains(busqueda, case=False, na=False) |
        df_mes_ant['Infor Code'].astype(str).str.contains(busqueda, case=False, na=False)
    ]
if cliente_detalle and cliente_detalle != 'Todos':
    df_mes_ant = df_mes_ant[df_mes_ant['Customer'] == cliente_detalle].copy()

# ===== CÁLCULO DE MÉTRICAS =====
total_actual = df_filtrado['Total Provision'].sum()
total_anterior = df_mes_ant['Total Provision'].sum() if not df_mes_ant.empty else 0
variacion_abs = total_actual - total_anterior
variacion_pct = (variacion_abs / total_anterior * 100) if total_anterior != 0 else 0.0

# ===== CÁLCULO DE WRITE OFFS =====
writeoffs_mes = 0
if not df_write.empty:
    df_write.columns = [c.strip() for c in df_write.columns.tolist()]
    date_col = next((c for c in df_write.columns if any(x in c.lower() for x in ['date','fecha'])), None)
    amount_col = next((c for c in df_write.columns if any(x in c.lower() for x in ['amount','monto','valor','credit','debit'])), None)
    cust_col = next((c for c in df_write.columns if any(x in c.lower() for x in ['cust','vendor','customer','name'])), None)
    
    if date_col and amount_col:
        df_write[date_col] = pd.to_datetime(df_write[date_col], errors='coerce')
        df_write_mes = df_write[(df_write[date_col].dt.year == año_sel) & (df_write[date_col].dt.month == mes_sel)].copy()
        
        if cust_col:
            df_write_mes = df_write_mes[df_write_mes[cust_col].notna()]
            df_write_mes[cust_col] = df_write_mes[cust_col].astype(str)  # ✅ Corrección para evitar error .str
            if cliente_detalle and cliente_detalle != 'Todos':
                df_write_mes = df_write_mes[df_write_mes[cust_col].str.upper() == cliente_detalle.strip().upper()]
            elif busqueda:
                df_write_mes = df_write_mes[df_write_mes[cust_col].str.contains(busqueda, case=False, na=False)]
        
        df_write_mes[amount_col] = pd.to_numeric(df_write_mes[amount_col], errors='coerce').fillna(0)
        writeoffs_mes = df_write_mes[amount_col].sum()

writeoffs_texto = "Sin Write offs" if writeoffs_mes == 0 or pd.isna(writeoffs_mes) else f"${writeoffs_mes:,.0f}"

# ===== MÉTRICAS =====
st.markdown(f"### 📊 Resumen - {mes_sel}/{año_sel}")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("🗓️ Año", año_sel)
with col2: st.metric("📅 Mes", mes_sel)
with col3: st.write("")
with col4: st.write("")

col5, col6, col7, col8 = st.columns(4)
with col5: st.metric("💰 Mes Anterior", f"${total_anterior:,.0f}")
with col6: st.metric("💸 Write Offs", writeoffs_texto)
with col7: st.metric("💰 Mes Actual", f"${total_actual:,.0f}")
with col8:
    st.metric("📈 Variación", f"${variacion_abs:,.0f}")

    variacion_text = f"{variacion_pct:+.1f}%"
    if variacion_pct < 0:
        st.markdown(f"<div style='color:#1B5E20; font-weight:700; font-size:1.1rem; margin-top:6px;'>↓ {variacion_text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#B71C1C; font-weight:700; font-size:1.1rem; margin-top:6px;'>↑ {variacion_text}</div>", unsafe_allow_html=True)

st.markdown("---")

# ===== TABLA DE CLIENTES =====
st.subheader(f"📋 Total de Provisiones - {año_sel}-{mes_sel:02d}")
df_tabla = df_filtrado.groupby(['Infor Code', 'Customer'], as_index=False)['Total Provision'].sum()
# evitar división por cero si suma = 0
suma_total_prov = df_tabla['Total Provision'].sum()
df_tabla['% del Total'] = (df_tabla['Total Provision'] / suma_total_prov * 100) if suma_total_prov != 0 else 0
df_tabla = df_tabla.sort_values('% del Total', ascending=False)


st.dataframe(
    df_tabla.style.format({
        "Total Provision": "${:,.2f}",
        "% del Total": "{:.2f}%"
    })
)

st.markdown("---")

# ===== GRÁFICO DE LÍNEA =====
periodo_sel = pd.Period(fecha_sel, freq='M')
ultimos_5 = [periodo_sel - i for i in range(4,-1,-1)]
df_ultimos_5 = df[df['AñoMes'].isin(ultimos_5)].copy()
if busqueda:
    df_ultimos_5 = df_ultimos_5[df_ultimos_5['Customer'].astype(str).str.contains(busqueda, case=False, na=False) |
                                df_ultimos_5['Infor Code'].astype(str).str.contains(busqueda, case=False, na=False)]
if cliente_detalle and cliente_detalle != 'Todos':
    df_ultimos_5 = df_ultimos_5[df_ultimos_5['Customer'] == cliente_detalle].copy()

df_agrupado = df_ultimos_5.groupby('AñoMes', as_index=False)['Total Provision'].sum().sort_values('AñoMes')
df_agrupado['AñoMes_label'] = df_agrupado['AñoMes'].dt.to_timestamp().dt.strftime('%b %Y')

fig_linea = px.line(df_agrupado, x='AñoMes_label', y='Total Provision',
                    markers=True, title="Evolución Mensual de la Provisión Total",
                    color_discrete_sequence=[COLOR_PALETTE[0]])
fig_linea.update_traces(line=dict(width=4), marker=dict(size=8),
                        hovertemplate="<b>%{x}</b><br>Provision: $%{y:,.0f}<extra></extra>")
fig_linea.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='black', size=12),
                        xaxis=dict(title_text="Mes", showgrid=False, tickfont=dict(color='black')),
                        yaxis=dict(title_text="Total Provision ($)", tickformat=",",dtick = 10000, showgrid=True,
                                   gridcolor='rgba(128,128,128,0.2)', tickfont=dict(color='black')),
                        title=dict(font=dict(color='black', size=16)),
                        margin=dict(l=40,r=20,t=60,b=40))

st.subheader("📈 Evolución de Total Provision - Ultimos 5 meses")
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
        textfont=dict(color='black')
    )
    fig_pie_ant.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black'),
        title=dict(font=dict(color='black'))
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
        textfont=dict(color='black')
    )
    fig_pie_act.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black'),
        title=dict(font=dict(color='black'))
    )
    st.plotly_chart(fig_pie_act, use_container_width=True)

# ===== PIE DE PÁGINA =====
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; padding: 20px;'>
        <p style='margin: 0; font-size: 0.9rem;'>📊 <strong>Provision Cartera USA</strong> | Reporte Gerencial en Streamlit</p>
        <p style='margin: 5px 0 0 0; font-size: 0.8rem;'>© 2025 - Dashboard de provisiones contables</p>
    </div>
    """,
    unsafe_allow_html=True
)

