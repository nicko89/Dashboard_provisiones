import pandas as pd
import streamlit as st
import plotly.express as px

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(page_title="Provision Cartera USA", layout="wide")

# ===== CARGA DE DATOS =====
@st.cache_data
def cargar_datos():
    df = pd.read_excel("Data/Base Provision.xlsx")
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df

df = cargar_datos()

# ===== FILTRO SOLO 2024 Y 2025 =====
df = df[df['Fecha'].dt.year.isin([2024, 2025])]

# ===== CÁLCULO DE PROVISIONES CON CONDICIÓN > 0 =====
def provision_91_180(row):
    saldo = row.get('91 - 180', 0)
    if row.get('TipoCliente', '') == 'INT' or saldo <= 0:
        return 0
    if row['Fecha'].year == 2024:
        return saldo * 0.20
    elif row['Fecha'].year == 2025:
        return saldo * 0.03
    return 0

df['Provision 91-180'] = df.apply(provision_91_180, axis=1)
df['Provision 181-270'] = df['181 - 270'].apply(lambda x: x*0.50 if x>0 else 0)

def provision_271_360(row):
    saldo = row.get('271-360', 0)
    if saldo <= 0:
        return 0
    return saldo * (0.50 if row['Fecha'].year == 2024 else 1.0)

df['Provision 271-360'] = df.apply(provision_271_360, axis=1)
df['Provision >360'] = df['> 360'].apply(lambda x: x if x>0 else 0)
df['Total Provision'] = df[['Provision 91-180','Provision 181-270','Provision 271-360','Provision >360']].sum(axis=1)

# ===== DETECTAR ÚLTIMO MES Y MES ANTERIOR =====
df['AñoMes'] = df['Fecha'].dt.to_period('M')
meses_ordenados = df['AñoMes'].sort_values().unique()
ultimo_mes = meses_ordenados[-1]
mes_anterior = meses_ordenados[-2]

# ===== MÉTRICAS =====
total_actual = df[df['AñoMes'] == ultimo_mes]['Total Provision'].sum()
total_anterior = df[df['AñoMes'] == mes_anterior]['Total Provision'].sum()
diferencia = total_actual - total_anterior
porcentaje = (diferencia / total_anterior * 100) if total_anterior != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Mes actual", str(ultimo_mes))
col2.metric("Total Provision Mes Actual", f"${total_actual:,.2f}")
col3.metric("Total Provision Mes Anterior", f"${total_anterior:,.2f}", f"{porcentaje:.2f}%")

# ===== TABLA SOLO ÚLTIMO MES =====
df_ultimo_mes = df[df['AñoMes'] == ultimo_mes].copy()
df_ultimo_mes['Fecha'] = df_ultimo_mes['Fecha'].dt.strftime('%m/%d/%Y')

columnas_finales = [
    'Fecha', 'Infor Code', 'Customer', 'Current', '1 - 90', '91 - 180', '181 - 270',
    '271-360', '> 360', 'TOTAL',
    'Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360', 'Total Provision'
]

st.subheader(f"Datos del último mes ({ultimo_mes})")
st.dataframe(df_ultimo_mes[columnas_finales])

# ===== GRÁFICO 1: Distribución de Provisión por Rango (Último Mes) =====
df_graf1 = df_ultimo_mes.melt(
    id_vars=['Customer'], 
    value_vars=['Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360'],
    var_name='Rango', value_name='Provision'
)

fig1 = px.bar(
    df_graf1, x='Customer', y='Provision', color='Rango',
    title=f"Distribución de Provisión por Rango - {ultimo_mes}", 
    text='Provision'
)
fig1.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
st.plotly_chart(fig1, use_container_width=True)

# ===== GRÁFICO 2: Evolución Total Provision por Mes =====
df_evolucion = df.groupby('AñoMes')['Total Provision'].sum().reset_index()
df_evolucion['AñoMes'] = df_evolucion['AñoMes'].astype(str)

fig2 = px.line(
    df_evolucion, x='AñoMes', y='Total Provision', markers=True,
    title="Evolución de Total Provision por Mes"
)
st.plotly_chart(fig2, use_container_width=True)
