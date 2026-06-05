"""
app.py — Dashboard HeliOS: Monitoramento de Tempestades Solares
HeliOS | Global Solution 2026.1 — FIAP

Dashboard Streamlit com 7 seções:
  1. Cabeçalho + status atual (Kp, nível de alerta)
  2. Série temporal ESP32 (campo magnético B nas últimas 2h)
  3. Previsão LSTM — SSN para os próximos 6 meses
  4. Detecção YOLO — imagem SDO + manchas detectadas
  5. Mapa de risco auroral global (Folium/Leaflet)
  6. Últimos boletins cognitivos (S3)
  7. Histórico de eventos solares (NASA DONKI API)

Execução:
    streamlit run src/dashboard/app.py
"""

from pathlib import Path
import sys

# Garante que os módulos do projeto sejam encontráveis
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src" / "ml" / "lstm"))
sys.path.insert(0, str(ROOT / "src" / "ml" / "yolo"))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
from PIL import Image
from datetime import datetime, timezone
import pandas as pd

# Importa funções de dados do módulo local
sys.path.insert(0, str(Path(__file__).parent))
from data_loader import (
    load_esp32_readings,
    load_lstm_forecast,
    load_yolo_detection,
    load_recent_bulletins,
    load_recent_cme_events,
    get_latest_kp,
    classify_kp,
    risk_badge_html,
    RISK_COLORS,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Configuração da página
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="HeliOS — Monitoramento Solar",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Auto-refresh a cada 5 minutos (300 000 ms)
st_autorefresh(interval=300_000, key="helios_refresh")

# CSS leve para cards e badges
st.markdown("""
<style>
.metric-card {
    background: #1e1e2e;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    border-left: 4px solid #666;
}
.section-title {
    font-size: 1.2em;
    font-weight: bold;
    color: #f0f0f0;
    border-bottom: 2px solid #333;
    padding-bottom: 6px;
    margin-bottom: 12px;
}
.bulletin-box {
    background: #1a1a2e;
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 10px;
    border-left: 3px solid #e74c3c;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — Cabeçalho
# ═══════════════════════════════════════════════════════════════════════════════

col_logo, col_title, col_time = st.columns([1, 5, 2])
with col_logo:
    st.markdown("## ☀️")
with col_title:
    st.title("HeliOS — Sistema de Previsão de Tempestades Solares")
    st.caption("FIAP Global Solution 2026.1 | AWS + ML + IoT + Cognitive AI")
with col_time:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    st.metric("Última atualização", now_str)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — Painel de Risco Atual (ESP32 + Kp)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="section-title">📡 Status Geomagnético em Tempo Real</p>',
            unsafe_allow_html=True)

esp32_df   = load_esp32_readings(hours=2)
latest_kp  = get_latest_kp(esp32_df)
kp_val     = float(latest_kp.get("kp_proxy", 0))
kp_level, kp_desc = classify_kp(kp_val)
kp_color   = RISK_COLORS.get(kp_level, "#95a5a6")
b_total    = float(latest_kp.get("b_total_nT", 23000))
geo_status = latest_kp.get("geo_status", "QUIET")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🌡️ Índice Kp", f"{kp_val:.1f}", help="Proxy Kp medido pelo ESP32")
with col2:
    st.markdown(
        f"**Nível de Alerta**<br>{risk_badge_html(kp_level)}",
        unsafe_allow_html=True,
    )
with col3:
    st.metric("🧲 Campo B (nT)", f"{b_total:,.0f}", help="Campo magnético total em nanoteslas")
with col4:
    st.metric("📍 Estação", "BR-001 | São Paulo", help="helios-station-BR-001")

# Descrição do nível
st.info(f"**{kp_level}** — {kp_desc}")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 — Série Temporal ESP32 (Campo B)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="section-title">📊 Campo Magnético — Últimas 2 Horas (ESP32)</p>',
            unsafe_allow_html=True)

if not esp32_df.empty:
    fig_b = go.Figure()
    fig_b.add_trace(go.Scatter(
        x=esp32_df["timestamp"],
        y=esp32_df["b_total_nT"],
        mode="lines+markers",
        name="B total (nT)",
        line=dict(color="#3498db", width=2),
        marker=dict(size=4),
    ))

    # Linha de referência — campo base da Terra (~25 000 nT em latitudes médias)
    fig_b.add_hline(
        y=23000, line_dash="dash", line_color="#95a5a6",
        annotation_text="Campo de referência (23 000 nT)",
        annotation_position="top right",
    )

    # Colorir fundo se for tempestade
    if kp_val >= 5:
        fig_b.update_layout(
            paper_bgcolor="rgba(231,76,60,0.05)",
            plot_bgcolor="rgba(231,76,60,0.05)",
        )

    fig_b.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_title="Horário (UTC)",
        yaxis_title="Campo B (nT)",
        showlegend=True,
        template="plotly_dark",
    )
    st.plotly_chart(fig_b, use_container_width=True)

    # Mini-tabela das últimas 5 leituras
    with st.expander("Ver últimas 5 leituras ESP32"):
        display_df = esp32_df.tail(5).copy()
        display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M UTC")
        st.dataframe(
            display_df[["timestamp", "b_total_nT", "kp_proxy", "geo_status"]],
            use_container_width=True,
            hide_index=True,
        )
else:
    st.warning("Sem leituras ESP32 disponíveis")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — Previsão LSTM
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="section-title">🔮 Previsão de Atividade Solar — LSTM (6 meses)</p>',
            unsafe_allow_html=True)

lstm_result = load_lstm_forecast(months=6)
predictions = lstm_result.get("predictions", [])

if predictions:
    months_labels = [p["month"] for p in predictions]
    ssn_values    = [p["ssn_predicted"] for p in predictions]
    risk_levels   = [p["risk"]["level"] for p in predictions]
    bar_colors    = [RISK_COLORS.get(r, "#95a5a6") for r in risk_levels]

    # Garante 10% de margem de erro para banda de confiança
    mae = lstm_result.get("model_mae_ssn", 12.0)

    fig_lstm = go.Figure()

    # Banda de confiança (±MAE)
    fig_lstm.add_trace(go.Scatter(
        x=months_labels + months_labels[::-1],
        y=[v + mae for v in ssn_values] + [max(0, v - mae) for v in ssn_values[::-1]],
        fill="toself",
        fillcolor="rgba(52,152,219,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name=f"±{mae:.0f} SSN (confiança)",
        showlegend=True,
    ))

    # Linha de previsão
    fig_lstm.add_trace(go.Scatter(
        x=months_labels,
        y=ssn_values,
        mode="lines+markers",
        name="SSN previsto",
        line=dict(color="#3498db", width=3),
        marker=dict(
            size=10,
            color=bar_colors,
            line=dict(width=2, color="white"),
        ),
    ))

    # Limiares de risco
    for threshold, label, color in [
        (50,  "QUIET/ACTIVE",    "#f39c12"),
        (80,  "ACTIVE/ELEVATED", "#e67e22"),
        (120, "ELEVATED/STORM",  "#e74c3c"),
    ]:
        fig_lstm.add_hline(
            y=threshold, line_dash="dot", line_color=color, opacity=0.6,
            annotation_text=label, annotation_position="top right",
        )

    fig_lstm.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_title="Mês",
        yaxis_title="Número de Manchas Solares (SSN)",
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_lstm, use_container_width=True)

    # Tabela resumo
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        peak = max(predictions, key=lambda p: p["ssn_predicted"])
        st.metric("📈 Pico previsto", f"SSN {peak['ssn_predicted']:.0f}", peak["month"])
    with col_t2:
        mae_val = lstm_result.get("model_mae_ssn", None)
        try:
            mae_fmt = f"{float(mae_val):.1f} SSN"
            mae_delta = "menor = melhor"
        except (TypeError, ValueError):
            mae_fmt, mae_delta = "N/A", ""
        st.metric("📉 Erro do modelo (MAE)", mae_fmt, mae_delta)
else:
    st.warning("Previsão LSTM indisponível — modelo não encontrado")
    st.info("Execute `python src/ml/lstm/predict.py` para verificar o modelo")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5 — Imagem Solar (YOLO)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="section-title">🌞 Imagem Solar SDO + Detecções YOLOv8</p>',
            unsafe_allow_html=True)

yolo_result = load_yolo_detection()
col_img, col_det = st.columns([3, 2])

with col_img:
    # Usa imagem anotada se existir; fallback para imagem original
    img_path = yolo_result.get("annotated_image") or \
               str(ROOT / "data" / "solar_images" / "sdo_latest_0193.jpg")

    if Path(img_path).exists():
        img = Image.open(img_path)
        st.image(img, caption="SDO/AIA 0193 Å — última imagem disponível", use_container_width=True)
    else:
        st.info("Imagem SDO não disponível — execute a detecção localmente")

with col_det:
    yolo_level = yolo_result.get("risk_level", "QUIET")
    yolo_score = yolo_result.get("risk_score", 0.0)

    st.markdown(f"**Risco detectado:** {risk_badge_html(yolo_level)}", unsafe_allow_html=True)
    st.metric("Risk Score", f"{yolo_score:.2f}", help="Score de risco YOLO (0=QUIET → 1=ALERT)")

    detections = yolo_result.get("detections", [])
    st.metric("Objetos detectados", len(detections))

    if detections:
        det_df = pd.DataFrame(detections)[["class", "confidence"]]
        det_df["confidence"] = det_df["confidence"].map(lambda x: f"{x:.1%}")
        st.dataframe(det_df, use_container_width=True, hide_index=True)
    else:
        st.caption("Nenhuma anomalia detectada na imagem solar atual")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6 — Mapa de Risco Auroral
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="section-title">🗺️ Mapa de Risco Auroral Global</p>',
            unsafe_allow_html=True)

# O risco auroral/geomagnético é maior em latitudes altas (>55°)
# e em regiões com infraestrutura crítica (petróleo no Ártico, GPS, etc.)

RISK_ZONES = [
    # (nome, lat, lon, raio_km, cor, descrição)
    ("Ártico — Redes Elétricas", 70, -50,  600_000, "red",    "Correntes induzidas em linhas de transmissão"),
    ("Alasca — Oleodutos",       65, -148, 400_000, "orange", "Corrosão acelerada em oleodutos"),
    ("Escandinávia — GPS",       63, 15,   500_000, "orange", "Degradação GPS em rotas polares"),
    ("Sibéria — Comunicações",   65, 100,  550_000, "yellow", "Rádio HF afetado"),
    ("Brasil — Ionosfera",       -15, -52, 700_000, "green",  "Impacto moderado em GNSS/satélites"),
    ("Brasil — Estação HeliOS",  -23.5, -46.6, 50_000, "blue", "helios-station-BR-001 | São Paulo"),
]

m = folium.Map(
    location=[20, 0],
    zoom_start=2,
    tiles="CartoDB dark_matter",
)

for name, lat, lon, radius, color, desc in RISK_ZONES:
    alpha = 0.4 if kp_val >= 5 else 0.2  # destaca quando há tempestade
    folium.Circle(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=alpha,
        tooltip=f"<b>{name}</b><br>{desc}",
    ).add_to(m)
    folium.Marker(
        location=[lat, lon],
        tooltip=name,
        icon=folium.Icon(color=color if color != "red" else "red", icon="info-sign"),
    ).add_to(m)

st_folium(m, width=None, height=420, returned_objects=[])

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 7 — Boletins Cognitivos
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="section-title">📋 Últimos Boletins Cognitivos (HeliOS AI)</p>',
            unsafe_allow_html=True)

bulletins = load_recent_bulletins(n=3)

if bulletins:
    tabs = st.tabs([
        f"Boletim {i+1} — {b.get('generated_at', '')[:16].replace('T',' ')} UTC"
        for i, b in enumerate(bulletins)
    ])
    for tab, bulletin in zip(tabs, bulletins):
        with tab:
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                bl_kp = bulletin.get("kp_max", 0)
                st.metric("Kp máx.", f"{bl_kp:.1f}")
            with col_b2:
                bl_level = bulletin.get("risk_level", "QUIET")
                st.markdown(
                    f"**Nível:** {risk_badge_html(bl_level)}",
                    unsafe_allow_html=True,
                )
            with col_b3:
                src = bulletin.get("source", "N/A")
                st.metric("Fonte LLM", src)

            st.markdown("---")
            bl_text = bulletin.get("bulletin", "Boletim não disponível")
            st.markdown(bl_text)
else:
    st.info("Nenhum boletim disponível. Execute `python src/cognitive/bulletin_generator.py` para gerar.")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 8 — Histórico de Eventos Solares (NASA DONKI)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="section-title">☄️ Histórico de CMEs — NASA DONKI (30 dias)</p>',
            unsafe_allow_html=True)

cme_df = load_recent_cme_events(days=30)
if not cme_df.empty:
    st.dataframe(
        cme_df.rename(columns={
            "activity_id":  "ID do Evento",
            "start_time":   "Data/Hora Início",
            "note":         "Nota",
            "cme_analysis": "Análises CME",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"Total de {len(cme_df)} CMEs relevantes nos últimos 30 dias | Fonte: NASA DONKI API")
else:
    st.info("Nenhum CME relevante detectado nos últimos 30 dias")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# Rodapé
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style='text-align:center; color:#666; font-size:0.85em; margin-top:20px;'>
  HeliOS v1.0 | FIAP Global Solution 2026.1 | AWS Lambda + DynamoDB + S3 + SNS + EventBridge<br>
  LSTM (MAE ~12 SSN) + YOLOv8 (mAP50=0.866) + IoT ESP32 + Cognitive AI<br>
  Atualização automática a cada 5 minutos
</div>
""", unsafe_allow_html=True)
