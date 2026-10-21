import pandas as pd
import streamlit as st
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(
    page_title="FraudHunter",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ FraudHunter")
st.caption("SISTEMA INTELLIGENTE DE DETECCIÓN Y EVALUACIÓN DE RIESGO EN TIEMPO REAL")

# 2. Cargar datos base del CSV
@st.cache_data
def load_initial_data():
    try:
        return pd.read_csv("dataset_fraud_hunter_10k.csv")
    except Exception as e:
        st.error(f"Error al cargar el dataset inicial: {e}")
        return pd.DataFrame()

# Guardar los datos en el estado de la sesión para poder agregar registros en vivo
if "df_transacciones" not in st.session_state:
    st.session_state.df_transacciones = load_initial_data()

# 3. Pestañas principales de la aplicación
tab1, tab2, tab3 = st.tabs(["📊 Dashboard General", "⚡ Evaluador en Vivo", "📜 Historial de Operaciones"])

# --- TAB 1: DASHBOARD GENERAL ---
with tab1:
    df = st.session_state.df_transacciones
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Transacciones", len(df))
        
        # Si tienes columna de fraude o riesgo, calculas métricas reales
        if "es_fraude" in df.columns:
            fraudes = df[df["es_fraude"] == 1]
            col2.metric("Casos Sospechosos / Fraudes", len(fraudes))
            col3.metric("Tasa de Riesgo", f"{(len(fraudes)/len(df))*100:.1f}%")
        else:
            col2.metric("Estado del Sistema", "Activo")
            col3.metric("Fuente de Datos", "CSV + En Vivo")

        st.markdown("---")
        st.subheader("Muestra de Datos Recientes")
        st.dataframe(df.tail(50), use_container_width=True)
    else:
        st.warning("No hay datos cargados actualmente.")

# --- TAB 2: EVALUADOR EN VIVO (AGREGAR REGISTROS) ---
with tab2:
    st.subheader("Evaluación de Transacción en Tiempo Real")
    st.write("Ingresa los detalles de la operación para evaluarla y agregarla al historial.")

    with st.form("form_nueva_transaccion"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            monto = st.number_input("Monto de la Transacción ($)", min_value=1.0, value=150.0, step=10.0)
            tipo_op = st.selectbox("Tipo de Operación", ["Transferencia", "Pago QR", "Retiro Cajero", "Compra Web"])
        
        with col_b:
            origen = st.text_input("Cuenta / Usuario Origen", value="USR-9921")
            ubicacion = st.text_input("Ubicación de Origen", value="Bogotá, CO")

        # Regla simple de evaluación visual
        riesgo_calculado = "Alto Riesgo ⚠️" if monto > 2000 else "Bajo Riesgo ✅"
        
        submitted = st.form_submit_button("Evaluar y Registrar Transacción")
        
        if submitted:
            # Crear nueva fila de datos
            nueva_transaccion = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "monto": monto,
                "tipo": tipo_op,
                "origen": origen,
                "ubicacion": ubicacion,
                "evaluacion": riesgo_calculado,
                "es_fraude": 1 if monto > 2000 else 0
            }
            
            # Agregar la transacción al estado actual
            st.session_state.df_transacciones = pd.concat(
                [st.session_state.df_transacciones, pd.DataFrame([nueva_transaccion])], 
                ignore_index=True
            )
            
            st.success(f"Transacción registrada con éxito. Resultado: **{riesgo_calculado}**")

# --- TAB 3: HISTORIAL DE OPERACIONES ---
with tab3:
    st.subheader("Historial Completo")
    st.dataframe(st.session_state.df_transacciones, use_container_width=True)
    
    # Botón para descargar el dataset con las transacciones agregadas
    csv_bytes = st.session_state.df_transacciones.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Historial Actualizado (CSV)",
        data=csv_bytes,
        file_name="historial_fraudhunter_actualizado.csv",
        mime="text/csv"
    )
