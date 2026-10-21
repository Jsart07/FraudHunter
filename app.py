import pandas as pd
import streamlit as st
from datetime import datetime

# Configuración inicial del panel
st.set_page_config(
    page_title="FraudHunter",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ FraudHunter")
st.caption("SISTEMA INTELIGENTE DE DETECCIÓN Y EVALUACIÓN DE RIESGO EN TIEMPO REAL")

# Carga dinámica del dataset
@st.cache_data
def load_data():
    try:
        return pd.read_csv("dataset_fraud_hunter_10k.csv")
    except Exception as e:
        st.error(f"Error al cargar el archivo de datos: {e}")
        return pd.DataFrame()

if "df_transacciones" not in st.session_state:
    st.session_state.df_transacciones = load_data()

# Pestañas principales de navegación
tab1, tab2, tab3 = st.tabs(["📊 Dashboard General", "⚡ Evaluador en Vivo", "📜 Historial de Operaciones"])

# --- TAB 1: DASHBOARD GENERAL ---
with tab1:
    df = st.session_state.df_transacciones
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Registros", len(df))
        
        fraudes = df[df["es_fraude"] == 1] if "es_fraude" in df.columns else []
        col2.metric("Casos Detectados / Sospechosos", len(fraudes))
        col3.metric("Nivel Global de Riesgo", f"{(len(fraudes)/len(df))*100:.1f}%" if len(df) > 0 else "0%")
        
        st.markdown("---")
        st.subheader("Últimas Transacciones Registradas")
        st.dataframe(df.tail(20), use_container_width=True)
    else:
        st.warning("No hay datos cargados.")

# --- TAB 2: EVALUADOR EN VIVO (CONTROLES INTERACTIVOS) ---
with tab2:
    st.subheader("Evaluador Interactivo en Tiempo Real")
    st.write("Modifica las variables de la operación para recalcular el nivel de riesgo instantáneamente:")

    # Columnas de entrada de datos
    col_input1, col_input2 = st.columns(2)

    with col_input1:
        monto = st.slider("Monto de la Transacción ($)", min_value=10, max_value=10000, value=1500, step=50)
        tipo_operacion = st.selectbox("Tipo de Operación", ["Transferencia bancaria", "Pago QR", "Retiro en Cajero", "Compra Web Internacional"])
        hora_operacion = st.slider("Hora de la Transacción (Formato 24h)", min_value=0, max_value=23, value=14)

    with col_input2:
        ubicacion = st.selectbox("Ubicación del Dispositivo", ["Bogotá, CO", "Medellín, CO", "Cali, CO", "Ubicación Desconocida / VPN"])
        score_crediticio = st.number_input("Puntaje de Crédito / Confianza", min_value=300, max_value=850, value=650)
        cuenta_origen = st.text_input("ID Cuenta Origen", value="ACC-883921")

    # Lógica de reglas / Modelo predictivo para evaluación en vivo
    puntos_riesgo = 0
    
    if monto > 3000:
        puntos_riesgo += 40
    elif monto > 1000:
        puntos_riesgo += 20
        
    if tipo_operacion == "Compra Web Internacional":
        puntos_riesgo += 25
    elif tipo_operacion == "Retiro en Cajero":
        puntos_riesgo += 15
        
    if hora_operacion < 5 or hora_operacion > 23:
        puntos_riesgo += 20
        
    if ubicacion == "Ubicación Desconocida / VPN":
        puntos_riesgo += 30

    # Determinar resultado
    if puntos_riesgo >= 50:
        resultado_evaluacion = "ALTO RIESGO (Sospecha de Fraude)"
        color_alerta = "error"
        es_fraude_flag = 1
    elif puntos_riesgo >= 25:
        resultado_evaluacion = "RIESGO MODERADO (Verificación requerida)"
        color_alerta = "warning"
        es_fraude_flag = 0
    else:
        resultado_evaluacion = "APROBADO (Transacción Segura)"
        color_alerta = "success"
        es_fraude_flag = 0

    st.markdown("---")
    st.subheader("Resultado de la Evaluación")
    
    # Renderizar alerta dinámica
    if color_alerta == "error":
        st.error(f"🚨 Nivel de Riesgo: {puntos_riesgo}% - Status: **{resultado_evaluacion}**")
    elif color_alerta == "warning":
        st.warning(f"⚠️ Nivel de Riesgo: {puntos_riesgo}% - Status: **{resultado_evaluacion}**")
    else:
        st.success(f"✅ Nivel de Riesgo: {puntos_riesgo}% - Status: **{resultado_evaluacion}**")

    # Botón para guardar la transacción ingresada en la base de datos temporal
    if st.button("📌 Guardar Evaluación en el Historial"):
        nueva_fila = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "monto": monto,
            "tipo": tipo_operacion,
            "ubicacion": ubicacion,
            "evaluacion": resultado_evaluacion,
            "es_fraude": es_fraude_flag
        }
        
        st.session_state.df_transacciones = pd.concat(
            [st.session_state.df_transacciones, pd.DataFrame([nueva_fila])],
            ignore_index=True
        )
        st.toast("Transacción agregada al historial con éxito.", icon="✅")

# --- TAB 3: HISTORIAL DE OPERACIONES ---
with tab3:
    st.subheader("Historial General de Operaciones")
    st.dataframe(st.session_state.df_transacciones, use_container_width=True)
    
    # Exportar archivo
    csv_data = st.session_state.df_transacciones.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Historial Completo (CSV)",
        data=csv_data,
        file_name="historial_evaluaciones_fraudhunter.csv",
        mime="text/csv"
    )
