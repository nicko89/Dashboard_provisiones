import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(page_title="Provision Cartera USA", layout="wide")

# ===== CSS MEJORADO - FONDO OSCURO =====
st.markdown("""
<style>
/* Fondo y overlay oscuro */
.stApp {background-image: url("/assets/Fondo.jpg"); background-size: cover; background-attachment: fixed; background-repeat: no-repeat;}
.stApp::before {content: ""; position: absolute; inset: 0; background-color: rgba(0,0,0,0.85); z-index: 0;}
/* Header */
.header-box {background: rgba(255,255,255,0.95); padding: 20px; border-radius: 10px; border-left: 5px solid #2E7D32; box-shadow: 0 4px 15px rgba(0,0,0,0.3); text-align: center; margin-bottom: 10px;}
/* Títulos y texto blanco */
h1,h2,h3,h4,h5,h6,p,span,div,label,.stMarkdown,.stSubheader {color: white !important;}
/* Métricas */
[data-testid="metric-container"] {background: rgba(30,30,30,0.9); border: 1px solid #444; border-radius: 10px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);}
[data-testid="metric-label"] {color: white !important; font-weight: 600 !important;}
[data-testid="metric-value"] {color: white !important; font-weight: 700 !important;}
[data-testid="metric-delta"] {color: #81C784 !important; font-weight: 600 !important;}
/* Gráficos sin fondo */
.js-plotly-plot, .plotly {background-color: transparent !important; border-radius: 10px;}
.gtitle, .xtitle, .ytitle {color: black !important; font-weight: 600 !important;}
/* Sidebar */
.css-1d391kg, .css-1lcbmhc {background-color: rgba(40,40,40,0.9) !important;}
.stSidebar h1,.stSidebar h2,.stSidebar h3,.stSidebar p,.stSidebar label,.stSidebar div {color: white !important;}
.stTextInput input, .stSelectbox select, .stSelectbox span {color: white !important; background-color: rgba(60,60,60,0.9) !important; border: 1px solid #666 !important; border-radius: 6px;}
/* Dataframe */
.dataframe {background-color: rgba(30,30,30,0.9); color: white !important; border-radius: 8px; border: 1px solid #444;}
/* Botones */
.stButton button {background-color: #2E7D32; color: white; border-radius: 6px; border: none; padding: 8px 16px; font-weight: 500;}
.stButton button:hover {background-color: #1B5E20; color: white;}
/* Separadores */
.stMarkdown hr {margin: 2rem 0; border: none; height: 1px; background: linear-gradient(90deg, transparent, #2E7D32, transparent);}
</style>
""", unsafe_allow_html=True)

# ===== PALETA DE COLORES PARA GRÁFICOS =====
COLOR_PALETTE = ['#2E7D32', '#4CAF50', '#81C784', '#C8E6C9', '#1B5E20']

# ===== ENCABEZADO =====
col1, col2 = st.columns([1,3])
with col1:
    st.image("assets/Logo.png", width=250)
with col2:
    st.markdown("""
    <div class="header-box">
        <h1 style="margin:0; text-align:center; color: #1B5E20 !important; font-size: 2.2rem;">
            📊 Provision Cartera USA
        </h1>
    </div>
    """, unsafe_allow_html=True)

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
    if str(code).startswith(("INT","SH")) or code in ["NAC1617","NAC0986","NAC0987","NAC1312","NAC0740","NAC0756","NAC1614","NAC1650"]:
        return "INT"
    return "REGULAR"
df['TipoCliente'] = df['Infor Code'].apply(tipo_cliente)
df = df[df['TipoCliente']!="INT"].copy()

# ===== CÁLCULO DE PROVISIONES =====
def provision_91_180(row): return 0 if pd.isna(row.get('91 - 180',0)) or row['91 - 180']<=0 else row['91 - 180']*(0.2 if row['Fecha'].year==2024 else 0.03)
def provision_181_270(row): return row.get('181 - 270',0)*0.5 if (not pd.isna(row.get('181 - 270',0)) and row['181 - 270']>0) else 0
def provision_271_360(row): return 0 if pd.isna(row.get('271-360',0)) or row['271-360']<=0 else row['271-360']*(0.5 if row['Fecha'].year==2024 else 1.0)
def provision_mayor_360(row): return row.get('> 360',0) if (not pd.isna(row.get('> 360',0)) and row['> 360']>0) else 0

df['Provision 91-180'] = df.apply(provision_91_180, axis=1)
df['Provision 181-270'] = df.apply(provision_181_270, axis=1)
df['Provision 271-360'] = df.apply(provision_271_360, axis=1)
df['Provision >360'] = df.apply(provision_mayor_360, axis=1)
df['Total Provision'] = df[['Provision 91-180','Provision 181-270','Provision 271-360','Provision >360']].sum(axis=1).fillna(0)

# ===== CAMPOS TEMPORALES =====
df['Año'] = df['Fecha'].dt.year
df['Mes'] = df['Fecha'].dt.month
df['AñoMes'] = df['Fecha'].dt.to_period('M')
df['AñoMes_str'] = df['AñoMes'].astype(str)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### 🗓️ Filtros de Periodo")
    año_sel = st.selectbox("Seleccionar año:", sorted(df['Año'].unique(), reverse=True))
    meses_disponibles = sorted(df[df['Año']==año_sel]['Mes'].unique())
    mes_sel = st.selectbox("Seleccionar mes:", meses_disponibles)
    
    st.markdown("---")
    st.markdown("### 🔍 Buscador")
    if 'busqueda' not in st.session_state: st.session_state['busqueda'] = ''
    clientes_list = sorted(df['Customer'].dropna().unique().tolist())
    cliente_options = ['Todos'] + clientes_list
    st.text_input("Buscar Cliente o Infor Code:", key='busqueda', placeholder="Escribe para buscar...")
    st.markdown("### 👥 Selección de Cliente")
    st.selectbox("Seleccionar Cliente:", cliente_options, key='cliente_detalle')
    
    def _clear_filters():
        st.session_state['busqueda'] = ''
        st.session_state['cliente_detalle'] = 'Todos'
    if st.button("🧹 Limpiar Filtros", use_container_width=True):
        _clear_filters()
        st.rerun()

busqueda = st.session_state.get('busqueda','')
cliente_detalle = st.session_state.get('cliente_detalle','Todos')

# ===== FILTRADO PRINCIPAL =====
df_filtrado = df[(df['Año']==año_sel) & (df['Mes']==mes_sel)].copy()
if busqueda:
    df_filtrado = df_filtrado[df_filtrado['Customer'].str.contains(busqueda, case=False, na=False) | df_filtrado['Infor Code'].str.contains(busqueda, case=False, na=False)]
if cliente_detalle!='Todos': df_filtrado = df_filtrado[df_filtrado['Customer']==cliente_detalle].copy()

# ===== MES ANTERIOR =====
fecha_sel = pd.Timestamp(año_sel, mes_sel, 1)
fecha_ant = fecha_sel - relativedelta(months=1)
df_mes_ant = df[(df['Fecha'].dt.year==fecha_ant.year) & (df['Fecha'].dt.month==fecha_ant.month)].copy()
if busqueda:
    df_mes_ant = df_mes_ant[df_mes_ant['Customer'].str.contains(busqueda, case=False, na=False) | df_mes_ant['Infor Code'].str.contains(busqueda, case=False, na=False)]
if cliente_detalle!='Todos': df_mes_ant = df_mes_ant[df_mes_ant['Customer']==cliente_detalle].copy()

# ===== MÉTRICAS =====
total_actual = df_filtrado['Total Provision'].sum()
total_anterior = df_mes_ant['Total Provision'].sum() if not df_mes_ant.empty else 0
variacion_abs = total_actual - total_anterior
variacion_pct = (variacion_abs/total_anterior*100) if total_anterior!=0 else 0.0

# ===== WRITE OFFS =====
writeoffs_mes = 0
if not df_write.empty:
    cols = [c.strip() for c in df_write.columns.tolist()]
    df_write.columns = cols
    date_col = next((c for c in cols if any(x in c.lower() for x in ['date','fecha'])), None)
    amount_col = next((c for c in cols if any(x in c.lower() for x in ['amount','monto','valor','credit','debit'])), None)
    cust_col = next((c for c in cols if any(x in c.lower() for x in ['cust','vendor','customer','name'])), None)
    
    if date_col and amount_col:
        df_write[date_col] = pd.to_datetime(df_write[date_col], errors='coerce')
        df_write_mes = df_write[(df_write[date_col].dt.year==año_sel) & (df_write[date_col].dt.month==mes_sel)].copy()
        if cust_col:
            df_write_mes = df_write_mes[df_write_mes[cust_col].notna() & ~df_write_mes[cust_col].astype(str).str.strip().str[:3].str.upper().eq('INT')]
            if cliente_detalle!='Todos': df_write_mes = df_write_mes[df_write_mes[cust_col].astype(str).str.strip().str.upper()==cliente_detalle.strip().upper()]
            elif busqueda: df_write_mes = df_write_mes[df_write_mes[cust_col].str.contains(busqueda, case=False, na=False)]
        df_write_mes[amount_col] = pd.to_numeric(df_write_mes[amount_col], errors='coerce').fillna(0)
        writeoffs_mes = df_write_mes[amount_col].sum()

writeoffs_texto = "Sin Write offs" if writeoffs_mes==0 or pd.isna(writeoffs_mes) else f"${writeoffs_mes:,.0f}"

# ===== MÉTRICAS REORGANIZADAS =====
st.markdown(f"### 📊 Resumen - {mes_sel}/{año_sel}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🗓️ Año", año_sel)
col2.metric("📅 Mes", mes_sel)
col5, col6, col7, col8 = st.columns(4)
col5.metric("💰 Mes Anterior", f"${total_anterior:,.0f}")
col6.metric("💸 Write Offs", writeoffs_texto)
col7.metric("💰 Mes Actual", f"${total_actual:,.0f}")
col8.metric("📈 Variación", f"${variacion_abs:,.0f}", delta=f"{variacion_pct:+.1f}%")

st.markdown("---")

# ===== TABLA DE CLIENTES =====
st.subheader("📋 Detalle de Provisiones por Cliente")
df_tabla = df_filtrado.groupby(['Infor Code','Customer'], as_index=False)['Total Provision'].sum()
suma_total_prov = df_tabla['Total Provision'].sum()
df_tabla['% del Total'] = df_tabla['Total Provision']/suma_total_prov*100 if suma_total_prov!=0 else 0
df_tabla = df_tabla.sort_values('Total Provision', ascending=False)
st.dataframe(df_tabla.style.format({"Total Provision":"${:,.2f}","% del Total":"{:.2f}%"}), use_container_width=True, height=400)

# ===== EVOLUCIÓN ÚLTIMOS 5 MESES =====
periodo_sel = pd.Period(fecha_sel, freq='M')
ultimos_5 = [periodo_sel - i for i in range(4,-1,-1)]
df_ultimos_5 = df[df['AñoMes'].isin(ultimos_5)].copy()
if busqueda:
    df_ultimos_5 = df_ultimos_5[df_ultimos_5['Customer'].str.contains(busqueda, case=False, na=False) | df_ultimos_5['Infor Code'].str.contains(busqueda, case=False, na=False)]
if cliente_detalle!='Todos': df_ultimos_5 = df_ultimos_5[df_ultimos_5['Customer']==cliente_detalle].copy()
df_agrupado = df_ultimos_5.groupby('AñoMes', as_index=False)['Total Provision'].sum().sort_values('AñoMes')
df_agrupado['AñoMes_label'] = df_agrupado['AñoMes'].dt.to_timestamp().dt.strftime('%b %Y')
fig_linea = px.line(df_agrupado, x='AñoMes_label', y='Total Provision', markers=True, title="Evolución Mensual de la Provisión Total", color_discrete_sequence=[COLOR_PALETTE[0]])
fig_linea.update_traces(line=dict(width=4), marker=dict(size=8), hovertemplate="<b>%{x}</b><br>Provision: $%{y:,.0f}<extra></extra>")
fig_linea.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='black', size=12), xaxis=dict(title_text="Mes", showgrid=False, tickfont=dict(color='black')), yaxis=dict(title_text="Total Provision ($)", tickformat=",", showgrid=True, gridcolor='rgba(128,128,128,0.2)', tickfont=dict(color='black')), title=dict(font=dict(color='black', size=16)), margin=dict(l=40,r=20,t=60,b=40))
st.subheader("📈 Evolución de Total Provision (Últimos 5 meses)")
st.plotly_chart(fig_linea, use_container_width=True)

# ===== DISTRIBUCIÓN POR RANGO =====
st.subheader("🥧 Distribución de Provisión por Rango de Edad")
totales_ant = df_mes_ant[['Provision 91-180','Provision 181-270','Provision 271-360','Provision >360']].sum().to_dict() if not df_mes_ant.empty else df_filtrado[['Provision 91-180','Provision 181-270','Provision 271-360','Provision >360']].sum().to_dict()
totales_act = df_filtrado[['Provision 91-180','Provision 181-270','Provision 271-360','Provision >360']].sum().to_dict()
rango_names = {'Provision 91-180':'91-180 días','Provision 181-270':'181-270 días','Provision 271-360':'271-360 días','Provision >360':'>360 días'}
df_pie_ant = pd.DataFrame(list(totales_ant.items()), columns=['Rango','Total']); df_pie_ant['Rango'] = df_pie_ant['Rango'].map(rango_names)
df_pie_act = pd.DataFrame(list(totales_act.items()), columns=['Rango','Total']); df_pie_act['Rango'] = df_pie_act['Rango'].map(rango_names)
col_pie1,col_pie2 = st.columns(2)
with col_pie1:
    fig_pie_ant = px.pie(df_pie_ant, values='Total', names='Rango', title=f"Mes Anterior ({fecha_ant.strftime('%Y-%m')})", color_discrete_sequence=COLOR_PALETTE)
    fig_pie_ant.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color='black'))
    fig_pie_ant.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='black'), title=dict(font=dict(color='black')))
    st.plotly_chart(fig_pie_ant, use_container_width=True)
with col_pie2:
    fig_pie_act = px.pie(df_pie_act, values='Total', names='Rango',
                         title=f"Mes Actual ({año_sel}-{mes_sel:02d})",
                         color_discrete_sequence=COLOR_PALETTE)
    fig_pie_act.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color='black'))
    fig_pie_act.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black'),
        title=dict(font=dict(color='black'))
    )
    st.plotly_chart(fig_pie_act, use_container_width=True)
