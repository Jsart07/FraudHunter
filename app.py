import streamlit as st
import pandas as pd
import mysql.connector
import datetime

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS MINIMALISTAS
# ---------------------------------------------------------
st.set_page_config(
    page_title="FraudHunter | Risk Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de CSS personalizado para la estética Minimalista / Modern Dark
st.markdown("""
    <style>
    /* Fondo principal y tipografía general */
    .stApp {
        background-color: #0E1117;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo de Tarjetas KPI */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Personalización de Botones */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.4);
        transform: scale(1.01);
    }
    
    /* Tarjetas de Contenedor */
    .css-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    /* Insignias de Riesgo */
    .badge-bajo {
        background-color: rgba(46, 213, 115, 0.15);
        color: #2ed573;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #2ed573;
        display: inline-block;
    }
    .badge-medio {
        background-color: rgba(255, 171, 0, 0.15);
        color: #ffab00;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #ffab00;
        display: inline-block;
    }
    .badge-alto {
        background-color: rgba(255, 71, 87, 0.15);
        color: #ff4757;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #ff4757;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CONEXIÓN A BASE DE DATOS MYSQL
# ---------------------------------------------------------
def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Momo07.",  # 👈 Cambia por tu contraseña de MySQL
        database="fraud_hunter"
    )

# ---------------------------------------------------------
# 3. LÓGICA DE EVALUACIÓN
# ---------------------------------------------------------
def evaluar_transaccion(monto, intentos, distancia, hora):
    score = 0.05
    factores = []
    
    if monto > 1000000:
        score += 0.35
        factores.append("Monto elevado (> $1.000.000 COP)")
    if intentos >= 2:
        score += 0.30
        factores.append(f"Múltiples reintentos fallidos ({intentos})")
    if distancia > 50:
        score += 0.20
        factores.append(f"Distancia atípica ({distancia} km)")
    if hora in [23, 0, 1, 2, 3, 4]:
        score += 0.15
        factores.append("Horario nocturno / atípico")
        
    probabilidad = min(score, 0.99)
    
    if probabilidad < 0.40:
        nivel = "BAJO"
        recom = "Aprobar operación normal."
    elif probabilidad < 0.70:
        nivel = "MEDIO"
        recom = "Solicitar doble factor de autenticación (OTP)."
    else:
        nivel = "ALTO"
        recom = "Bloquear transacción y contactar al titular."
        
    return probabilidad, nivel, factores, recom

def guardar_prediccion(monto, intentos, distancia, hora, prob, nivel, factores, recom):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        factores_str = ", ".join(factores) if factores else "Sin alertas"
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        query = """
            INSERT INTO transacciones_evaluadas 
            (monto, fecha_hora, intentos_rechazados, distancia_km, hora_dia, probabilidad, nivel_riesgo, factores, recomendacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (monto, fecha_actual, intentos, distancia, hora, prob * 100, nivel, factores_str, recom)
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Error MySQL: {e}")

# ---------------------------------------------------------
# 4. ENCABEZADO Y NAVEGACIÓN
# ---------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #FFFFFF; font-weight: 800; margin-bottom: 0px;'>🛡️ FraudHunter</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8B949E; font-size: 14px; margin-bottom: 30px;'>SISTEMA INTELIGENTE DE DETECCIÓN Y EVALUACIÓN DE RIESGO EN TIEMPO REAL</p>", unsafe_allow_html=True)

# Navegación mediante pestañas estilizadas
tab1, tab2, tab3 = st.tabs(["📊  Dashboard General", "⚡ Evaluador en Vivo", "🗄️ Historial de Operaciones"])

# --- TAB 1: DASHBOARD METRICAS ---
with tab1:
    try:
        conn = obtener_conexion()
        df = pd.read_sql_query("SELECT * FROM transacciones_evaluadas", conn)
        conn.close()
        
        total_ops = len(df)
        sospechosas = len(df[df['nivel_riesgo'].isin(['MEDIO', 'ALTO'])]) if total_ops > 0 else 0
        altas = len(df[df['nivel_riesgo'] == 'ALTO']) if total_ops > 0 else 0
        monto_riesgo = df[df['nivel_riesgo'] == 'ALTO']['monto'].sum() if total_ops > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Transacciones Totales", f"{total_ops:,}")
        c2.metric("Alertas Sospechosas", f"{sospechosas:,}")
        c3.metric("Riesgo Crítico (Alto)", f"{altas:,}")
        c4.metric("Capital en Riesgo", f"${monto_riesgo:,.0f} COP")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if total_ops > 0:
            st.subheader("Distribución de Transacciones por Nivel de Riesgo")
            conteo_riesgos = df['nivel_riesgo'].value_counts()
            st.bar_chart(conteo_riesgos)
        else:
            st.info("Sin registros en MySQL. Realiza una evaluación o importa un dataset.")
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")

# --- TAB 2: EVALUADOR EN VIVO ---
with tab2:
    st.markdown("<h3 style='color: #FFFFFF;'>Simulación de Transacción</h3>", unsafe_allow_html=True)
    
    with st.form("form_evaluacion"):
        c1, c2 = st.columns(2)
        with c1:
            monto = st.number_input("Monto de la Operación ($ COP)", min_value=1000, value=350000, step=25000)
            intentos = st.number_input("Intentos Fallidos Previos (24h)", min_value=0, max_value=10, value=0)
        with c2:
            distancia = st.number_input("Distancia a Ubicación Habitual (km)", min_value=0.0, value=3.0, step=1.0)
            hora = st.slider("Hora del Evento (0 - 23 h)", 0, 23, 14)
            
        btn_evaluar = st.form_submit_button("⚡ EVALUAR RIESGO EN TIEMPO REAL")
        
    if btn_evaluar:
        prob, nivel, factores, recom = evaluar_transaccion(monto, intentos, distancia, hora)
        guardar_prediccion(monto, intentos, distancia, hora, prob, nivel, factores, recom)
        
        st.markdown("---")
        res_col1, res_col2 = st.columns([1, 2])
        
        with res_col1:
            st.markdown("##### Probabilidad de Fraude")
            st.markdown(f"<h1 style='color: #00C6FF; font-size: 48px; margin: 0;'>{prob*100:.1f}%</h1>", unsafe_allow_html=True)
            
            if nivel == "BAJO":
                st.markdown('<span class="badge-bajo">RIESGO BAJO</span>', unsafe_allow_html=True)
            elif nivel == "MEDIO":
                st.markdown('<span class="badge-medio">RIESGO MEDIO</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-alto">RIESGO ALTO</span>', unsafe_allow_html=True)
                
        with res_col2:
            st.markdown("##### Acción Recomendada")
            st.info(f"👉 **{recom}**")
            
            st.markdown("##### Factores de Riesgo Detectados")
            if factores:
                for f in factores:
                    st.write(f"• ⚠️ {f}")
            else:
                st.write("• ✅ Operación dentro del comportamiento habitual.")

# --- TAB 3: HISTORIAL MYSQL ---
with tab3:
    st.markdown("<h3 style='color: #FFFFFF;'>Registros Evaluados en MySQL</h3>", unsafe_allow_html=True)
    try:
        conn = obtener_conexion()
        df_historial = pd.read_sql_query("SELECT id, fecha_hora, monto, intentos_rechazados, distancia_km, hora_dia, probabilidad, nivel_riesgo, recomendacion FROM transacciones_evaluadas ORDER BY id DESC", conn)
        conn.close()
        
        st.dataframe(
            df_historial,
            use_container_width=True,
            column_config={
                "monto": st.column_config.NumberColumn("Monto (COP)", format="$ %d"),
                "probabilidad": st.column_config.NumberColumn("Score %", format="%.1f%%"),
            }
        )
    except Exception as e:
        st.error(f"Error de lectura MySQL: {e}")