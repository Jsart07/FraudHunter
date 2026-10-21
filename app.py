import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    try:
        # Intenta cargar desde el CSV en el repositorio
        return pd.read_csv("dataset_fraud_hunter_10k.csv")
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

# Reemplaza tu llamado a pd.read_sql_query con:
df = load_data()