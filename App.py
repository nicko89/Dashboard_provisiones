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

# ===== FILTRO POR AÑO =====
df = df[df['Fecha'].dt.year == 2024]  # solo mostrar datos de 2024

# ===== CÁLCULO DE PROVISIONES =====
# Provision 91 a 180
df['Provision 91-180'] = df.apply(lambda row: 0 if row.get('TipoCliente', '') == 'INT' else
                                  (row['91 - 180'] * 0.20 if row['Fecha'].year == 2024 and row['91 - 180'] > 0
                                   else (row['91 - 180'] * 0.03 if row['Fecha'].year == 2025 and row['91 - 180'] > 0 else 0)),
                                  axis=1)

# Provision 181 a 270 - 50% para ambos años
df['Provision 181-270'] = df['181 - 270'] * 0.50

# Provision 271 a 360 - 50% para 2024, 100% para 2025
df['Provision 271-360'] = df.apply(lambda row: row['271-360'] * (0.50 if row['Fecha'].year == 2024 else 1.0), axis=1)

# Provision > 360 - 100% para ambos años
df['Provision >360'] = df['> 360']

# Total Provision
df['Total Provision'] = df['Provision 91-180'] + df['Provision 181-270'] + df['Provision 271-360'] + df['Provision >360']

# ===== MÉTRICAS =====
total_provision = df['Total Provision'].sum()
st.metric("Total Provision", f"${total_provision:,.2f}")

# ===== TABLA COMPLETA =====
# Columnas finales
columnas_finales = [
    'Fecha', 'Infor Code', 'Customer', 'Current', '1 - 90', '91 - 180', '181 - 270',
    '271-360', '> 360', 'TOTAL',
    'Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360', 'Total Provision'
]

st.subheader("Datos con provisiones")
st.dataframe(df[columnas_finales])
