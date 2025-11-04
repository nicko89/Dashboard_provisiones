import pandas as pd
import streamlit as st

# ===== CONFIGURACIÓN =====
st.set_page_config(page_title="Provision Cartera USA", layout="wide")

# ===== CARGA DE DATOS =====
@st.cache_data
def cargar_datos():
    df = pd.read_excel("Data/Base Provision.xlsx")
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df

df = cargar_datos()

# ===== FILTRO SOLO 2024 =====
df = df[df['Fecha'].dt.year == 2024]

# ===== CÁLCULO DE PROVISIONES =====
df['Provision 91-180'] = df.apply(lambda row: 0 if row.get('TipoCliente', '') == 'INT' else
                                  (row['91 - 180'] * 0.20 if row['Fecha'].year == 2024 and row['91 - 180'] > 0 else 0),
                                  axis=1)

df['Provision 181-270'] = df['181 - 270'] * 0.50
df['Provision 271-360'] = df['271-360'] * 0.50  # solo 2024
df['Provision >360'] = df['> 360']
df['Total Provision'] = df['Provision 91-180'] + df['Provision 181-270'] + df['Provision 271-360'] + df['Provision >360']

# ===== DETECTAR ÚLTIMO MES Y MES ANTERIOR =====
df['AñoMes'] = df['Fecha'].dt.to_period('M')
meses_ordenados = df['AñoMes'].sort_values().unique()
ultimo_mes = meses_ordenados[-1]
mes_anterior = meses_ordenados[-2]

# ===== METRICAS =====
total_actual = df[df['AñoMes'] == ultimo_mes]['Total Provision'].sum()
total_anterior = df[df['AñoMes'] == mes_anterior]['Total Provision'].sum()
diferencia = total_actual - total_anterior
porcentaje = (diferencia / total_anterior * 100) if total_anterior != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Mes actual", str(ultimo_mes))
col2.metric("Total Provision Mes Actual", f"${total_actual:,.2f}")
col3.metric("Cambio vs mes anterior", f"${diferencia:,.2f}", f"{porcentaje:.2f}%")

# ===== TABLA SOLO ÚLTIMO MES =====
df_ultimo_mes = df[df['AñoMes'] == ultimo_mes]

columnas_finales = [
    'Fecha', 'Infor Code', 'Customer', 'Current', '1 - 90', '91 - 180', '181 - 270',
    '271-360', '> 360', 'TOTAL',
    'Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360', 'Total Provision'
]

st.subheader(f"Datos del último mes ({ultimo_mes})")
st.dataframe(df_ultimo_mes[columnas_finales])
