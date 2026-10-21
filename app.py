import pandas as pd
import streamlit as st

# Configuración de página
st.set_page_config(page_title="FraudHunter", page_icon="🛡️", layout="wide")

st.title("🛡️ FraudHunter - Sistema de Detección de Fraude")
st.write("Bienvenido al panel de control de transacciones.")

@st.cache_data
def load_data():
    try:
        return pd.read_csv("dataset_fraud_hunter_10k.csv")
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Mostrar métricas rápidas
    col1, col2 = st.columns(2)
    col1.metric("Total de Registros", len(df))
    col2.metric("Columnas Detectadas", len(df.columns))

    st.subheader("Vista previa de los datos")
    st.dataframe(df.head(100), use_container_width=True)
else:
    st.warning("El archivo CSV no contiene datos o no se pudo cargar.")
