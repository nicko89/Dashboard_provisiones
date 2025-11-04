import pandas as pd
import streamlit as st

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

# ===== CÁLCULO DE PROVISIONES =====
# Provision 91 a 180
def provision_91_180(row):
    if row.get('TipoCliente', '') == 'INT':
        return 0
    if row['Fecha'].year == 2024 and row['91 - 180'] > 0:
        return row['91 - 180'] * 0.20
    elif row['Fecha'].year == 2025 and row['91 - 180'] > 0:
        return row['91 - 180'] * 0.03
    else:
        return 0

df['Provision 91-180'] = df.apply(provision_91_180, axis=1)

# Provision 181 a 270 - 50% ambos años
df['Provision 181-270'] = df['181 - 270'] * 0.50

# Provision 271 a 360 - 50% 2024, 100% 2025
def provision_271_360(row):
    return row['271-360'] * (0.50 if row['Fecha'].year == 2024 else 1.0)
df['Provision 271-360'] = df.apply(provision_271_360, axis=1)

# Provision > 360 - 100% ambos años
df['Provision >360'] = df['> 360']

# Total Provision
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
df_ultimo_mes['Fecha'] = df_ultimo_mes['Fecha'].dt.strftime('%m/%d/%Y')  # Formato MM/DD/YYYY

columnas_finales = [
    'Fecha', 'Infor Code', 'Customer', 'Current', '1 - 90', '91 - 180', '181 - 270',
    '271-360', '> 360', 'TOTAL',
    'Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360', 'Total Provision'
]

st.subheader(f"Datos del último mes ({ultimo_mes})")
st.dataframe(df_ultimo_mes[columnas_finales])


# ===== MÉTRICAS =====
total_actual = df[df['Fecha'].dt.to_period('M') == ultimo_mes]['Total Provision'].sum()
total_anterior = df[df['Fecha'].dt.to_period('M') == mes_anterior]['Total Provision'].sum()
diferencia = total_actual - total_anterior
porcentaje = (diferencia / total_anterior * 100) if total_anterior != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Mes actual", str(ultimo_mes))
col2.metric("Total Provision Mes Actual", f"${total_actual:,.2f}")
col3.metric("Cambio vs mes anterior", f"${diferencia:,.2f}", f"{porcentaje:.2f}%")

# ===== TABLA SOLO ÚLTIMO MES =====
df_ultimo_mes = df[df['Fecha'].dt.to_period('M') == ultimo_mes]

columnas_finales = [
    'Fecha', 'Infor Code', 'Customer', 'Current', '1 - 90', '91 - 180', '181 - 270',
    '271-360', '> 360', 'TOTAL',
    'Provision 91-180', 'Provision 181-270', 'Provision 271-360', 'Provision >360', 'Total Provision'
]

st.subheader(f"Datos del último mes ({ultimo_mes})")
st.dataframe(df_ultimo_mes[columnas_finales])
