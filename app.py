import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="FraudHunter - Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Encabezado principal
st.title("🛡️ FraudHunter")
st.caption("SISTEMA INTELIGENTE DE DETECCIÓN Y EVALUACIÓN DE RIESGO EN TIEMPO REAL")

# Cargar dataset
@st.cache_data
def load_data():
    try:
        return pd.read_csv("dataset_fraud_hunter_10k.csv")
    except Exception as e:
        st.error(f"Error al cargar el conjunto de datos: {e}")
        return pd.DataFrame()

if "df_transacciones" not in st.session_state:
    st.session_state.df_transacciones = load_data()

df = st.session_state.df_transacciones

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["📊 Dashboard General", "⚡ Evaluador en Vivo", "📜 Historial de Operaciones"])

# ==========================================
# --- TAB 1: DASHBOARD GENERAL (GRÁFICOS) ---
# ==========================================
with tab1:
    if not df.empty:
        # Métricas clave superiores
        col1, col2, col3, col4 = st.columns(4)
        
        total_tx = len(df)
        fraudes_count = len(df[df["es_fraude"] == 1]) if "es_fraude" in df.columns else 0
        tasa_fraude = (fraudes_count / total_tx * 100) if total_tx > 0 else 0
        monto_total = df["monto"].sum() if "monto" in df.columns else 0

        col1.metric("Total Transacciones", f"{total_tx:,}")
        col2.metric("Casos de Fraude", f"{fraudes_count:,}", delta_color="inverse")
        col3.metric("Tasa de Riesgo", f"{tasa_fraude:.2f}%")
        col4.metric("Monto Procesado", f"${monto_total:,.2f}")

        st.markdown("---")

        # Sección de Gráficos de Barras y Visualizaciones
        st.subheader("📈 Análisis de Fraude y Distribución")
        
        g_col1, g_col2 = st.columns(2)

        with g_col1:
            # Gráfico de barras: Fraude por Tipo de Operación / Categoría
            col_categoria = "tipo" if "tipo" in df.columns else ("categoria" if "categoria" in df.columns else None)
            if col_categoria and "es_fraude" in df.columns:
                df_grouped = df.groupby([col_categoria, "es_fraude"]).size().reset_index(name="Cantidad")
                df_grouped["Estado"] = df_grouped["es_fraude"].map({0: "Legítimo", 1: "Fraude"})
                
                fig_bar = px.bar(
                    df_grouped,
                    x=col_categoria,
                    y="Cantidad",
                    color="Estado",
                    barmode="group",
                    title="<b>Transacciones por Tipo de Operación y Estado</b>",
                    color_discrete_map={"Legítimo": "#2ecc71", "Fraude": "#e74c3c"}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No se encontró columna de categoría para generar el gráfico de barras.")

        with g_col2:
            # Gráfico de barras / Histograma: Distribución de Montos
            if "monto" in df.columns and "es_fraude" in df.columns:
                fig_hist = px.histogram(
                    df,
                    x="monto",
                    color="es_fraude",
                    nbins=30,
                    title="<b>Distribución de Montos Evaluados</b>",
                    color_discrete_map={0: "#3498db", 1: "#e74c3c"},
                    labels={"es_fraude": "Es Fraude"}
                )
                st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Muestra del Dataset")
        st.dataframe(df.head(100), use_container_width=True)
    else:
        st.warning("No hay datos cargados para generar el dashboard.")

# ==========================================
# --- TAB 2: EVALUADOR EN VIVO -----------
# ==========================================
with tab2:
    st.subheader("⚡ Evaluador de Riesgo en Tiempo Real")
    st.write("Ingresa los datos de la transacción para analizar el riesgo y visualizar el resultado en el modelo.")

    col_a, col_b = st.columns(2)

    with col_a:
        monto_input = st.number_input("Monto de la Transacción ($)", min_value=1.0, value=2500.0, step=50.0)
        tipo_input = st.selectbox("Tipo de Operación", ["Transferencia bancaria", "Pago QR", "Retiro Cajero", "Compra Web Internacional"])
        hora_input = st.slider("Hora de la Operación (0-23h)", 0, 23, 2)

    with col_b:
        ubicacion_input = st.selectbox(
    "Ubicación", 
    [
        "Bogotá, CO", 
        "Medellín, CO", 
        "Cali, CO", 
        "Barranquilla, CO", 
        "Cartagena, CO", 
        "Bucaramanga, CO", 
        "Pereira, CO", 
        "Manizales, CO", 
        "Cúcuta, CO", 
        "Santa Marta, CO", 
        "Ibagué, CO", 
        "Pasto, CO", 
        "Villavicencio, CO", 
        "Ubicación Desconocida / VPN"
    ]
)
        origen_input = st.text_input("Cuenta / Cliente Origen", value="CLI-88492")
        score_input = st.slider("Score de Confianza del Usuario", 300, 850, 580)

    # Cálculo dinámico del score de riesgo
    score_riesgo = 0
    if monto_input > 3000: score_riesgo += 40
    elif monto_input > 1000: score_riesgo += 20

    if tipo_input == "Compra Web Internacional": score_riesgo += 25
    if ubicacion_input == "Ubicación Desconocida / VPN": score_riesgo += 25
    if hora_input < 5 or hora_input > 23: score_riesgo += 15
    if score_input < 500: score_riesgo += 15

    es_fraude_calc = 1 if score_riesgo >= 50 else 0
    estado_eval = "ALTO RIESGO (Fraude Detectado)" if es_fraude_calc == 1 else "TRANSACCIÓN SEGURA"

    st.markdown("---")
    st.subheader("Resultado de la Evaluación")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        if es_fraude_calc == 1:
            st.error(f"🚨 **{estado_eval}**\n\nNivel de Riesgo Calculado: **{score_riesgo}%**")
        else:
            st.success(f"✅ **{estado_eval}**\n\nNivel de Riesgo Calculado: **{score_riesgo}%**")

    with res_col2:
        # Gráfico tipo medidor / barra para la transacción actual
        fig_gauge = px.bar(
            x=[score_riesgo],
            y=["Riesgo"],
            orientation='h',
            range_x=[0, 100],
            title="<b>Indicador de Riesgo Individual (%)</b>",
            color_discrete_sequence=["#e74c3c" if score_riesgo >= 50 else "#2ecc71"]
        )
        fig_gauge.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    if st.button("📌 Registrar Transacción en el Historial"):
        nueva_tx = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "monto": monto_input,
            "tipo": tipo_input,
            "ubicacion": ubicacion_input,
            "origen": origen_input,
            "evaluacion": estado_eval,
            "es_fraude": es_fraude_calc
        }
        st.session_state.df_transacciones = pd.concat(
            [st.session_state.df_transacciones, pd.DataFrame([nueva_tx])],
            ignore_index=True
        )
        st.toast("Transacción agregada correctamente al historial.", icon="✅")

# ==========================================
# --- TAB 3: HISTORIAL DE OPERACIONES ------
# ==========================================
with tab3:
    st.subheader("Historial Completo de Operaciones")
    st.dataframe(st.session_state.df_transacciones, use_container_width=True)

    csv_export = st.session_state.df_transacciones.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Completo (CSV)",
        data=csv_export,
        file_name="reporte_fraudhunter_completo.csv",
        mime="text/csv"
    )
