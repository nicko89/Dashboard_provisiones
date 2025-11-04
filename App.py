import streamlit as st
import pandas as pd

st.set_page_config(page_title = "Provision Cartera USA", layout="wide")

@st.cache_data
def cargar_datos():
    df = pd.read_excel(Data/Base Provision.xlsx)
    return df

df = cargar_datos()

st.title("Provision Cartera USA")
st.subheader("Vista general de los datos")
St.dataframe(df.head())
