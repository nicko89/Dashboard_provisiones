import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# CONFIGURACIÓN INICIAL
# ---------------------------
st.set_page_config(
    page_title="Reporte Ejecutivo Provisión Cartera USA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# ESTILO CORPORATIVO PLANO
# ---------------------------
st.markdown(
    """
    <style>
    /* Fondo blanco general */
    .stApp {
        background-color: #ffffff;
        color: #212121;
        font-family: 'Arial', sans-serif;
    }

    /* Encabezado */
    h1, h2, h3, h4, h5, h6 {
        color: #1B5E20;
        font-weight: 600;
        margin: 0;
    }

    /* Texto y párrafos */
    p, span, label, div {
        color: #212121;
        font-size: 14px;
    }

    /* Métricas */
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 6px;
        color: #212121;
    }

    /* Gráficos */
    .js-plotly-plot {
        background-color: #ffffff !important;
        border: none !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# PALETA CORPORATIVA
# ---------------------------
COLOR_PALETTE = ['#1B5E20', '#388E3C', '#8BC34A', '#F4E3B2', '#E57373']

# ---------------------------
# ENCABEZADO
# ---------------------------
col1, col2 = st.columns([1.5, 5])
with col1:
    st.image("assets/Logo.png", width=320)
with col2:
    st.markdown(
        """
        <div style="text-align:center;">
            <h1>Provisión Cartera USA</h1>
            <p>Análisis ejecutivo de provisiones contables</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ---------------------------
# CARGA DE DATOS
# ---------------------------
# Ajusta la ruta a tu archivo CSV/Excel según corresponda
df = pd.read_csv("assets/data_provisiones.csv")  # Ejemplo
df['Fecha'] = pd.to_datetime(df['Fecha'])

# ---------------------------
# FILTROS LATERALES
# ---------------------------
st.sidebar.header("Filtros")
anio_selected = st.sidebar.multiselect(
    "Seleccione Año",
    options=df['Fecha'].dt.year.unique(),
    default=df['Fecha'].dt.year.max()
)

mes_selected = st.sidebar.multiselect(
    "Seleccione Mes",
    options=df['Fecha'].dt.month.unique(),
    default=df['Fecha'].dt.month.max()
)

df_filtered = df[
    (df['Fecha'].dt.year.isin(anio_selected)) &
    (df['Fecha'].dt.month.isin(mes_selected))
]

# ---------------------------
# MÉTRICAS PRINCIPALES
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

total_provision = df_filtered['Provision'].sum()
total_cartera = df_filtered['Cartera'].sum()
indice_provision = (total_provision / total_cartera) * 100 if total_cartera != 0 else 0
promedio_dias_mora = df_filtered['DiasMora'].mean()

col1.metric("Total Provisión", f"${total_provision:,.0f}")
col2.metric("Total Cartera", f"${total_cartera:,.0f}")
col3.metric("Índice de Provisión (%)", f"{indice_provision:.2f}%")
col4.metric("Promedio Días Mora", f"{promedio_dias_mora:.1f}")

st.markdown("---")

# ---------------------------
# GRÁFICO DE EVOLUCIÓN DE PROVISIONES
# ---------------------------
fig_line = px.line(
    df_filtered.groupby('Fecha').sum().reset_index(),
    x='Fecha',
    y='Provision',
    title='Evolución de la Provisión',
    color_discrete_sequence=[COLOR_PALETTE[0]]
)
fig_line.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis_title='Fecha',
    yaxis_title='Provisión',
    title={'x':0.5, 'xanchor': 'center'}
)

st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------
# GRÁFICO DE DISTRIBUCIÓN DE CARTERA POR TIPO
# ---------------------------
fig_pie = px.pie(
    df_filtered.groupby('TipoCartera').sum().reset_index(),
    names='TipoCartera',
    values='Cartera',
    title='Distribución de Cartera por Tipo',
    color_discrete_sequence=COLOR_PALETTE
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')

st.plotly_chart(fig_pie, use_container_width=True)

# ---------------------------
# TABLA RESUMEN
# ---------------------------
st.subheader("Detalle de Provisiones")
st.dataframe(
    df_filtered.sort_values(by='Fecha', ascending=False).reset_index(drop=True),
    use_container_width=True
)
