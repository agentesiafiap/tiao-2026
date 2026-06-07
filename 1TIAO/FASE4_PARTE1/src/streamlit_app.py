# src/streamlit_app.py
import streamlit as st
import pandas as pd
import sqlite3
import joblib
import altair as alt
import numpy as np
from recommend import recommend_from_point
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os

MODEL_PATH = "models/regression_model.joblib"
DB_PATH = "data/farmtech.db"
CSV_PATH = "data/simulated_sensor_data.csv"

st.set_page_config(page_title="FarmTech - Assistente Agrícola", layout="wide")

st.title("FarmTech Solutions — Assistente Agrícola Inteligente")

# Sidebar: data source
st.sidebar.header("Dados")
source = st.sidebar.selectbox("Fonte de dados", ["CSV (simulado)", "SQLite DB"])
if source == "CSV (simulado)":
    df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
else:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM sensors", conn, parse_dates=["timestamp"])
    conn.close()

st.sidebar.markdown(f"Linhas: {len(df)}")

# Mostrar primeiras linhas
if st.checkbox("Mostrar amostra dos dados"):
    st.dataframe(df.head(200))

# Métricas do modelo (se existir)
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    st.sidebar.success("Modelo carregado")
else:
    model = None
    st.sidebar.warning("Modelo não encontrado. Rode train_model.py antes.")

# Estatísticas descritivas
st.subheader("Estatísticas descritivas")
st.write(df[["soil_moisture","soil_ph","air_temp","humidity","irrigation_ml","fertilizer_kg","yield_ton_per_ha"]].describe())

# Gráfico de correlação
st.subheader("Mapa de correlação (Pearson)")
corr = df[["soil_moisture","soil_ph","air_temp","humidity","irrigation_ml","fertilizer_kg","yield_ton_per_ha"]].corr()
st.dataframe(corr.style.background_gradient(axis=None))

# Scatter interativo: umidade x yield
st.subheader("Umidade do solo vs Rendimento")
chart = alt.Chart(df.sample(min(1000,len(df)))).mark_circle(size=60).encode(
    x='soil_moisture',
    y='yield_ton_per_ha',
    color='soil_ph',
    tooltip=['sensor_id','timestamp','soil_moisture','soil_ph','yield_ton_per_ha']
).interactive()
st.altair_chart(chart, use_container_width=True)

# Metrics: evaluate model on recent data if model exists
st.subheader("Avaliação do modelo")
if model is not None:
    X = df[["soil_moisture","soil_ph","air_temp","humidity","irrigation_ml","fertilizer_kg"]]
    y = df["yield_ton_per_ha"]
    preds = model.predict(X)
    mae = mean_absolute_error(y, preds)
    mse = mean_squared_error(y, preds)
    rmse = np.sqrt(mse)
    r2 = r2_score(y, preds)
    st.metric("MAE", f"{mae:.4f}")
    st.metric("RMSE", f"{rmse:.4f}")
    st.metric("R²", f"{r2:.4f}")
    st.write("Exemplo: previsões x observado (últimas 50 linhas)")
    comp = pd.DataFrame({"obs": y.tail(50).values, "pred": preds[-50:]})
    st.line_chart(comp.reset_index(drop=True))
else:
    st.info("Treine o modelo para ver métricas (execute src/train_model.py)")

# Painel de previsão e recomendação
st.subheader("Fazer previsão e obter recomendações")
with st.form("predict_form"):
    sm = st.number_input("Soil moisture (%)", min_value=0.0, max_value=100.0, value=25.0)
    ph = st.number_input("Soil pH", min_value=3.0, max_value=9.0, value=6.2)
    at = st.number_input("Air temp (°C)", min_value=-10.0, max_value=60.0, value=24.0)
    hum = st.number_input("Air humidity (%)", min_value=0.0, max_value=100.0, value=60.0)
    irr_ml = st.number_input("Irrigation applied (mL)", min_value=0.0, max_value=5000.0, value=0.0)
    fert = st.number_input("Fertilizer applied (kg)", min_value=0.0, max_value=10.0, value=0.0)
    submitted = st.form_submit_button("Prever & Recomendar")
    if submitted:
        if model is None:
            st.error("Modelo não encontrado. Rode src/train_model.py primeiro.")
        else:
            Xp = np.array([[sm, ph, at, hum, irr_ml, fert]])
            py = model.predict(Xp)[0]
            st.metric("Rendimento previsto (ton/ha)", f"{py:.4f}")
            rec = recommend_from_point(sm, ph, {"air_temp":at, "humidity":hum, "irrigation_ml":irr_ml, "fertilizer_kg":fert})
            st.write("**Recomendações**")
            st.write({
                "predicted_yield": rec["predicted_yield"],
                "irrigation_ml_suggested": rec["irrigation_ml_suggested"],
                "irrigation_reason": rec["irrigation_reason"],
                "fertilizer_kg_suggested": rec["fertilizer_kg_suggested"],
                "fertilizer_reason": rec["fertilizer_reason"]
            })
st.markdown("---")
st.caption("Protótipo: ajustar regras e thresholds para aplicação real. Consulte um engenheiro agrônomo para decisões finais.")
