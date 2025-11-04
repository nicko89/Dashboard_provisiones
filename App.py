import streamlit as st
import pandas as pd
import calendar

# ===== CONFIGURACIÓN =====
st.set_page_config(page_title="Provision Cartera USA", layout="wide")

# ===== CARGA DE DATOS =====
@st.cache_data
def cargar_datos():
    df = pd.read_excel("Data/Base Provision.xlsx")
    return df

df = cargar_datos()

# ===== MÉTRICAS DEL ÚLTIMO MES =====
# Convertir nombre del mes a número para ordenar correctamente
df['Mes_Num'] = df['Mes'].apply(lambda x: list(calendar.month_name).index(x.capitalize()))

# Ordenar por año y mes
df_ordenado = df.sort_values(by=['Año', 'Mes_Num'])

# Tomar último mes y mes anterior
ultimo_mes = df_ordenado.iloc[-1]
mes_anterior = df_ordenado.iloc[-2]

# Calcular métricas
ultimo_valor = ultimo_mes['Total Provisión']
valor_anterior = mes_anterior['Total Provisión']
diferencia = ultimo_valor - valor_anterior
porcentaje = (diferencia / valor_anterior * 100) if valor_anterior != 0 else 0

# Mostrar métricas en columnas
col1, col2, col3 = st.columns(3)
col1.metric("Mes actual", f"{ultimo_mes['Mes'].capitalize()} {ultimo_mes['Año']}")
col2.metric("Total Provisión", f"${ultimo_valor:,.2f}")
col3.metric("Cambio vs mes anterior", f"${diferencia:,.2f}", f"{porcentaje:.2f}%")

# ===== OPCIONAL: TABLA COMPLETA =====
st.subheader("Vista general de los datos")
st.dataframe(df)
