# 🛡️ FraudHunter - Sistema de Detección de Fraude en Tiempo Real

**FraudHunter** es una aplicación web analítica y predictiva diseñada para evaluar transacciones financieras en tiempo real, clasificar sus niveles de riesgo y registrar los eventos para auditoría cibersegura.

---

## 🚀 Tecnologías Utilizadas

- **Frontend / Dashboard:** Streamlit (Custom Dark/Minimalist UI)
- **Backend & Lógica:** Python 3.x
- **Base de Datos:** MySQL (`fraud_hunter`)
- **Procesamiento de Datos:** Pandas, NumPy

---

## 📌 Funcionalidades Principales

1. **Dashboard General:** Visualización de métricas clave (monto total en riesgo, alertas sospechosas y volumen de operaciones).
2. **Evaluador en Vivo:** Simulación interactiva de transacciones calculando probabilísticamente el score de riesgo (Bajo, Medio, Alto).
3. **Historial de Operaciones:** Conexión persistente a MySQL para consulta de registros analizados.

---

## 💻 Ejecución Local

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/Jsart07/FraudHunter.git](https://github.com/Jsart07/FraudHunter.git)
   cd FraudHunter
   
