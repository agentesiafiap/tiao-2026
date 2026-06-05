"""
data_loader.py — Funções de carregamento de dados para o dashboard HeliOS
HeliOS | Global Solution 2026.1 — FIAP

Centraliza todas as leituras de dados:
  - DynamoDB: leituras em tempo real do ESP32 (helios-kp-realtime)
  - S3: boletins cognitivos gerados pela API
  - LSTM: previsão de SSN via predict.py
  - YOLO: detecções solares via inference.py
  - NASA DONKI: eventos solares recentes (CME, flares)

Todas as funções usam @st.cache_data(ttl=300) para reduzir
chamadas às APIs e bancos de dados durante a navegação.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

import boto3
import pandas as pd
import streamlit as st
from boto3.dynamodb.conditions import Key, Attr

# ─── Caminhos ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.parent
SRC_ML_LSTM = ROOT / "src" / "ml" / "lstm"
SRC_ML_YOLO = ROOT / "src" / "ml" / "yolo"

# ─── Configurações ─────────────────────────────────────────────────────────────
DYNAMO_TABLE   = "helios-kp-realtime"
S3_BUCKET      = "helios-solar-data"
DEVICE_ID      = "helios-station-BR-001"
NASA_DONKI_URL = (
    "https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/CME?"
    "startDate={start}&endDate={end}&speed=500&halfAngle=30"
)


# ═══════════════════════════════════════════════════════════════════════════════
# DynamoDB — Leituras ESP32
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60)   # cache de 1 min para dados em tempo real
def load_esp32_readings(hours: int = 2) -> pd.DataFrame:
    """
    Retorna DataFrame com leituras do DynamoDB das últimas `hours` horas.

    Colunas: timestamp, b_total_nT, kp_proxy, geo_status, source

    A tabela helios-kp-realtime usa timestamp (string ISO) como hash key
    e armazena dados do NOAA Kp com campos: kp_index, alert_level, source.
    """
    try:
        dynamo = boto3.resource("dynamodb", region_name="us-east-1")
        table  = dynamo.Table(DYNAMO_TABLE)

        cutoff_iso = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")

        response = table.scan(
            FilterExpression=Attr("timestamp").gte(cutoff_iso),
            Limit=500,
        )
        items = response.get("Items", [])

        if not items:
            return _mock_esp32_readings(hours)

        rows = []
        for it in items:
            kp = float(it.get("kp_index", 0))
            # Converte Kp em campo B sintético: B_base - kp*400 nT (aproximação didática)
            b_total = max(18000.0, 23000.0 - kp * 400)
            rows.append({
                "timestamp": datetime.fromisoformat(it["timestamp"]).replace(tzinfo=timezone.utc),
                "b_total_nT": b_total,
                "kp_proxy":   kp,
                "geo_status": it.get("alert_level", "QUIET"),
                "source":     it.get("source", "unknown"),
            })

        df = pd.DataFrame(rows).sort_values("timestamp")
        return df

    except Exception as e:
        st.warning(f"DynamoDB indisponível ({e}) — usando dados simulados")
        return _mock_esp32_readings(hours)


def _mock_esp32_readings(hours: int = 2) -> pd.DataFrame:
    """Dados simulados para quando o DynamoDB estiver inacessível."""
    import numpy as np
    now  = datetime.now(timezone.utc)
    times = [now - timedelta(minutes=i * 15) for i in range(hours * 4)]
    times.reverse()
    base_b = 23000
    rows = []
    for t in times:
        noise = float(np.random.normal(0, 200))
        rows.append({
            "timestamp":  t,
            "b_total_nT": base_b + noise,
            "kp_proxy":   float(np.random.uniform(0, 2)),
            "geo_status": "QUIET",
            "source":     "mock_data",
        })
    return pd.DataFrame(rows)


def get_latest_kp(df: pd.DataFrame) -> dict:
    """Extrai a leitura mais recente do DataFrame ESP32."""
    if df.empty:
        return {"kp_proxy": 0.0, "geo_status": "QUIET", "b_total_nT": 23000.0}
    row = df.iloc[-1]
    return row.to_dict()


# ═══════════════════════════════════════════════════════════════════════════════
# S3 — Boletins Cognitivos
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def load_recent_bulletins(n: int = 3) -> list[dict]:
    """
    Retorna os últimos `n` boletins do S3 (bulletins/YYYY/MM/DD/HH-MM.json).
    """
    try:
        s3     = boto3.client("s3", region_name="us-east-1")
        prefix = "bulletins/"

        response = s3.list_objects_v2(
            Bucket=S3_BUCKET, Prefix=prefix, MaxKeys=200
        )
        keys = sorted(
            [obj["Key"] for obj in response.get("Contents", [])],
            reverse=True,
        )[:n]

        bulletins = []
        for key in keys:
            obj  = s3.get_object(Bucket=S3_BUCKET, Key=key)
            data = json.loads(obj["Body"].read())
            bulletins.append(data)

        return bulletins if bulletins else _mock_bulletins()

    except Exception as e:
        st.warning(f"S3 indisponível ({e}) — usando boletim simulado")
        return _mock_bulletins()


def _mock_bulletins() -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    return [{
        "generated_at": now,
        "kp_max": 0.0,
        "risk_level": "QUIET",
        "bulletin": (
            "## NÍVEL DE RISCO ATUAL\n"
            "BAIXO — Atividade solar dentro dos parâmetros normais.\n\n"
            "## INFRAESTRUTURAS EM RISCO\n"
            "Sem impactos previstos nas próximas 24 horas.\n\n"
            "## RECOMENDAÇÕES\n"
            "Monitoramento de rotina."
        ),
        "source": "mock_data",
    }]


# ═══════════════════════════════════════════════════════════════════════════════
# LSTM — Previsão SSN
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)   # cache 1h — modelo não muda
def load_lstm_forecast(months: int = 6) -> dict:
    """
    Importa predict.py diretamente e retorna o JSON de previsão.
    A função predict() em predict.py lê os dados e artefatos internamente.
    """
    try:
        if str(ROOT / "src" / "ml" / "lstm") not in sys.path:
            sys.path.insert(0, str(ROOT / "src" / "ml" / "lstm"))
        from predict import predict   # noqa: E402
        return predict(n_months_ahead=months)
    except Exception as e:
        return _mock_lstm_forecast(months)


def _mock_lstm_forecast(months: int = 6) -> dict:
    """Previsão simulada quando o modelo não está disponível."""
    import numpy as np
    now = datetime.now(timezone.utc)
    predictions = []
    base_ssn = 95.0
    for i in range(months):
        month_dt = now + timedelta(days=30 * (i + 1))
        ssn = max(0, base_ssn + float(np.random.normal(0, 10)) - i * 3)
        predictions.append({
            "month": month_dt.strftime("%Y-%m"),
            "ssn_predicted": round(ssn, 1),
            "risk": classify_ssn(ssn),
        })
    return {
        "predictions": predictions,
        "model_meta": {"mae_test": 12.3, "rmse_test": 15.8},
        "source": "mock_data",
    }


def classify_ssn(ssn: float) -> dict:
    """Classifica SSN em nível de risco — réplica de predict.py."""
    if ssn < 50:
        return {"level": "QUIET", "score": 0, "color": "#2ecc71"}
    elif ssn < 80:
        return {"level": "ACTIVE", "score": 1, "color": "#f39c12"}
    elif ssn < 120:
        return {"level": "ELEVATED", "score": 2, "color": "#e67e22"}
    else:
        return {"level": "STORM", "score": 3, "color": "#e74c3c"}


# ═══════════════════════════════════════════════════════════════════════════════
# YOLO — Última detecção solar
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)   # cache 10 min — imagem SDO atualiza a cada hora
def load_yolo_detection() -> dict:
    """
    Baixa imagem SDO e executa detecção YOLO.
    Retorna dict com detections, risk_score, risk_level, image_path.
    """
    try:
        if str(ROOT / "src" / "ml" / "yolo") not in sys.path:
            sys.path.insert(0, str(ROOT / "src" / "ml" / "yolo"))
        from inference import run_inference, download_latest_sdo   # noqa: E402

        sdo_path = ROOT / "data" / "solar_images" / "sdo_latest_0193.jpg"
        download_latest_sdo(sdo_path)
        result = run_inference(str(sdo_path))
        return result
    except Exception as e:
        return {
            "detections": [],
            "risk_score": 0.0,
            "risk_level": "QUIET",
            "annotated_image": None,
            "source": f"error: {e}",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# NASA DONKI — Eventos Solares Recentes
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=1800)   # cache 30 min
def load_recent_cme_events(days: int = 30) -> pd.DataFrame:
    """
    Consulta NASA DONKI API para CMEs das últimas `days` dias.
    """
    try:
        end   = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        url   = NASA_DONKI_URL.format(
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
        )
        req = urllib.request.Request(url, headers={"User-Agent": "HeliOS/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            events = json.loads(resp.read())

        rows = []
        for ev in events:
            rows.append({
                "activity_id":  ev.get("activityID", ""),
                "start_time":   ev.get("startTime", ""),
                "note":         ev.get("note", "")[:120],
                "cme_analysis": len(ev.get("cmeAnalyses", [])),
            })

        return pd.DataFrame(rows) if rows else _mock_cme_events()

    except Exception:
        return _mock_cme_events()


def _mock_cme_events() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "activity_id": "2026-06-01T12:00:00-CME-001",
            "start_time":  "2026-06-01T12:00Z",
            "note":        "C2.1 flare associated CME — Earth-directed component possible",
            "cme_analysis": 1,
        },
        {
            "activity_id": "2026-05-28T06:00:00-CME-001",
            "start_time":  "2026-05-28T06:00Z",
            "note":        "M1.4 flare — partial halo CME detected",
            "cme_analysis": 2,
        },
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

RISK_COLORS = {
    "QUIET":     "#2ecc71",
    "ACTIVE":    "#f39c12",
    "WATCH":     "#f39c12",
    "ELEVATED":  "#e67e22",
    "WARNING":   "#e67e22",
    "STORM":     "#e74c3c",
    "ALERT":     "#e74c3c",
    "STORM_MAJOR": "#9b59b6",
    "EXTREMO":   "#9b59b6",
}

KP_LABELS = {
    (0.0, 2.0):  ("QUIET",    "Atividade mínima"),
    (2.0, 4.0):  ("ACTIVE",   "Atividade moderada"),
    (4.0, 5.0):  ("ELEVATED", "Atenção — monitoramento reforçado"),
    (5.0, 6.0):  ("STORM",    "Tempestade G1"),
    (6.0, 99.0): ("STORM_MAJOR", "Tempestade G3+ — emergência"),
}


def classify_kp(kp: float) -> tuple[str, str]:
    for (lo, hi), (label, desc) in KP_LABELS.items():
        if lo <= kp < hi:
            return label, desc
    return "STORM_MAJOR", "Tempestade extrema"


def risk_badge_html(level: str) -> str:
    color = RISK_COLORS.get(level, "#95a5a6")
    return (
        f'<span style="background:{color};color:white;padding:4px 12px;'
        f'border-radius:4px;font-weight:bold;font-size:1.1em;">{level}</span>'
    )
