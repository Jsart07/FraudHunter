import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from supabase import create_client, ClientOptions

# Configuración de página
st.set_page_config(
    page_title="FraudHunter - Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ FraudHunter")
st.caption("SISTEMA INTELIGENTE DE DETECCIÓN Y EVALUACIÓN DE RIESGO EN TIEMPO REAL (BD CONECTADA)")

# Lectura directa
raw_url = st.secrets.get("SUPABASE_URL", "").strip().strip('"').strip("'")
raw_key = st.secrets.get("SUPABASE_KEY", "").strip().strip('"').strip("'")

# Forzar URL limpia
if not raw_url.startswith("https://"):
    raw_url = f"https://{raw_url}"

try:
    supabase = create_client(raw_url, raw_key)
except Exception as e:
    st.error(f"Error al inicializar cliente Supabase: {e}")

# Cargar datos desde Supabase
def load_data():
    try:
        response = supabase.table("transacciones").select("*").execute()
        df = pd.DataFrame(response.data)
        if df.empty:
            return pd.read_csv("dataset_fraud_hunter_10k.csv")
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.read_csv("dataset_fraud_hunter_10k.csv")

df = load_data()

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["📊 Dashboard General", "⚡ Evaluador en Vivo", "📜 Historial de Operaciones"])

# --- TAB 1: DASHBOARD ---
with tab1:
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        total_tx = len(df)
        fraudes_count = len(df[df["es_fraude"] == 1]) if "es_fraude" in df.columns else 0
        tasa_fraude = (fraudes_count / total_tx * 100) if total_tx > 0 else 0
        monto_total = df["monto"].sum() if "monto" in df.columns else 0

        col1.metric("Total Transacciones", f"{total_tx:,}")
        col2.metric("Casos de Fraude", f"{fraudes_count:,}")
        col3.metric("Tasa de Riesgo", f"{tasa_fraude:.2f}%")
        col4.metric("Monto Procesado", f"${monto_total:,.2f}")

        st.markdown("---")
        st.subheader("📈 Análisis Visual de Transacciones")
        
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            if "tipo" in df.columns and "es_fraude" in df.columns:
                df_grouped = df.groupby(["tipo", "es_fraude"]).size().reset_index(name="Cantidad")
                df_grouped["Estado"] = df_grouped["es_fraude"].map({0: "Legítimo", 1: "Fraude"})
                fig_bar = px.bar(
                    df_grouped, x="tipo", y="Cantidad", color="Estado", barmode="group",
                    title="<b>Transacciones por Tipo de Operación</b>",
                    color_discrete_map={"Legítimo": "#2ecc71", "Fraude": "#e74c3c"}
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        with g_col2:
            if "monto" in df.columns and "es_fraude" in df.columns:
                fig_hist = px.histogram(
                    df, x="monto", color="es_fraude", nbins=30,
                    title="<b>Distribución de Montos Evaluados</b>",
                    color_discrete_map={0: "#3498db", 1: "#e74c3c"}
                )
                st.plotly_chart(fig_hist, use_container_width=True)

        st.dataframe(df.tail(50), use_container_width=True)

# --- TAB 2: EVALUADOR EN VIVO ---
with tab2:
    st.subheader("⚡ Evaluador de Riesgo en Tiempo Real")
    col_a, col_b = st.columns(2)

    with col_a:
        monto_input = st.number_input("Monto de la Transacción ($)", min_value=1.0, value=2500.0, step=50.0)
        tipo_input = st.selectbox("Tipo de Operación", ["Transferencia bancaria", "Pago QR", "Retiro Cajero", "Compra Web Internacional"])
        hora_input = st.slider("Hora de la Operación (0-23h)", 0, 23, 2)

    with col_b:
        ubicacion_input = st.selectbox("Ubicación", ["Bogotá, CO", "Medellín, CO", "Cali, CO", "Barranquilla, CO", "Cartagena, CO", "Bucaramanga, CO", "Ubicación Desconocida / VPN"])
        origen_input = st.text_input("Cuenta / Cliente Origen", value="CLI-88492")
        score_input = st.slider("Score de Confianza del Usuario", 300, 850, 580)

    # Cálculo de riesgo
    score_riesgo = 0
    if monto_input > 3000: score_riesgo += 40
    elif monto_input > 1000: score_riesgo += 20
    if tipo_input == "Compra Web Internacional": score_riesgo += 25
    if ubicacion_input == "Ubicación Desconocida / VPN": score_riesgo += 25
    if hora_input < 5 or hora_input > 23: score_riesgo += 15

    es_fraude_calc = 1 if score_riesgo >= 50 else 0
    estado_eval = "ALTO RIESGO (Fraude Detectado)" if es_fraude_calc == 1 else "TRANSACCIÓN SEGURA"

    st.markdown("---")
    if es_fraude_calc == 1:
        st.error(f"🚨 **{estado_eval}** | Nivel de Riesgo: **{score_riesgo}%**")
    else:
        st.success(f"✅ **{estado_eval}** | Nivel de Riesgo: **{score_riesgo}%**")

    # Guardar permanentemente en Supabase
    if st.button("📌 Guardar en Base de Datos Supabase"):
        nueva_tx = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "monto": float(monto_input),
            "tipo": str(tipo_input),
            "ubicacion": str(ubicacion_input),
            "origen": str(origen_input),
            "evaluacion": str(estado_eval),
            "es_fraude": int(es_fraude_calc)
        }
        
        try:
            supabase.table("transacciones").insert(nueva_tx).execute()
            st.toast("¡Guardado permanentemente en la base de datos!", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar en la BD: {e}")

# --- TAB 3: HISTORIAL ---
with tab3:
    st.subheader("Historial Completo (PostgreSQL)")
    st.dataframe(df, use_container_width=True)
