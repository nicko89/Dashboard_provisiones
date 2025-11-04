import streamlit as st
import pandas as pd

# ===== CONFIGURACIÓN =====
st.set_page_config(page_title="Provision Cartera USA", layout="wide")

# ===== CARGA DE DATOS =====
@st.cache_data
def cargar_datos():
    df = pd.read_excel("Data/Base Provision.xlsx")
    # Convertir columna Fecha a datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df

df = cargar_datos()

# ===== MÉTRICAS DEL ÚLTIMO MES =====
# Agrupar por mes/año
df['AñoMes'] = df['Fecha'].dt.to_period('M')

# Ordenar meses
meses_ordenados = df['AñoMes'].sort_values().unique()

# Último mes y mes anterior
ultimo_mes = meses_ordenados[-1]
mes_anterior = meses_ordenados[-2]

# Sumar TOTAL por mes
ultimo_valor = df[df['AñoMes'] == ultimo_mes]['TOTAL'].sum()
valor_anterior = df[df['AñoMes'] == mes_anterior]['TOTAL'].sum()
diferencia = ultimo_valor - valor_anterior
porcentaje = (diferencia / valor_anterior * 100) if valor_anterior != 0 else 0

# Mostrar métricas
col1, col2, col3 = st.columns(3)
col1.metric("Mes actual", str(ultimo_mes))
col2.metric("Total Provisión", f"${ultimo_valor:,.2f}")
col3.metric("Cambio vs mes anterior", f"${diferencia:,.2f}", f"{porcentaje:.2f}%")

# ===== TABLA COMPLETA (opcional) =====
st.subheader("Vista general de los datos")
st.dataframe(df)
