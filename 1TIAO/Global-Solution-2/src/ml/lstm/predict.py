"""
predict.py — Inferência com o modelo LSTM treinado
HeliOS | Global Solution 2026.1 — FIAP

═══════════════════════════════════════════════════════════════════
CONCEITO: COMO USAR O MODELO EM PRODUÇÃO
═══════════════════════════════════════════════════════════════════

O modelo foi treinado com dados mensais históricos.
Para fazer uma previsão, precisamos:
  1. Pegar os últimos WINDOW_SIZE meses de SSN
  2. Normalizar com o MESMO scaler usado no treino
     (se usarmos outro scaler, os valores serão incompatíveis)
  3. Passar pela rede e desnormalizar a saída
  4. Classificar cada mês previsto em nível de risco

Retorno: JSON com previsão mensal + nível de risco para cada mês

Uso:
    python src/ml/lstm/predict.py
    python src/ml/lstm/predict.py --months 12   # prever 12 meses
    python src/ml/lstm/predict.py --output json  # saída em JSON
"""

import argparse
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf

# ─── Caminhos ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = ROOT / "data" / "processed" / "solar_cycle_historical.csv"
MODEL_DIR = Path(__file__).parent / "model"


def load_artifacts():
    """Carrega modelo e scaler do disco."""
    model = tf.keras.models.load_model(str(MODEL_DIR / "helios_lstm.keras"))
    with open(MODEL_DIR / "scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open(MODEL_DIR / "model_meta.json") as f:
        meta = json.load(f)
    return model, scaler, meta


def classify_risk(ssn: float) -> dict:
    """
    Classifica SSN em nível de risco geomagnético.
    Retorna dict com label, descrição e score numérico (0–3).
    """
    if ssn < 50:
        return {"level": "QUIET", "description": "Atividade solar baixa — sem risco", "score": 0}
    elif ssn < 80:
        return {"level": "ACTIVE", "description": "Atividade moderada — monitoramento contínuo", "score": 1}
    elif ssn < 120:
        return {"level": "ELEVATED", "description": "Atividade elevada — alerta para infraestrutura", "score": 2}
    else:
        return {"level": "STORM", "description": "TEMPESTADE SOLAR — risco crítico para infraestrutura", "score": 3}


def predict(n_months_ahead: int | None = None) -> dict:
    """
    Faz previsão de atividade solar para os próximos meses.

    Parâmetro:
        n_months_ahead: quantos meses prever. Se None, usa o HORIZON do modelo.

    Retorna dict com:
        - generated_at: timestamp da previsão
        - input_window: período usado como entrada
        - predictions: lista com SSN previsto e classificação por mês
        - peak_risk: maior nível de risco no horizonte previsto
    """
    model, scaler, meta = load_artifacts()
    window = meta["window_size"]
    horizon = meta["horizon"]
    n_months = n_months_ahead or horizon

    # Carregar série histórica e pegar a janela mais recente
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["time-tag"], format="%Y-%m")
    df = df.sort_values("date").reset_index(drop=True)
    df["ssn"] = df["ssn"].fillna(0).clip(lower=0).astype(float)

    recent = df.tail(window)
    input_series = recent["ssn"].values.astype(float)
    input_dates = recent["date"].dt.strftime("%Y-%m").tolist()

    # Normalizar e fazer previsão
    input_norm = scaler.transform(input_series.reshape(-1, 1)).flatten()
    X = input_norm.reshape(1, window, 1)  # batch size = 1

    pred_norm = model.predict(X, verbose=0)[0]  # shape: (horizon,)
    pred_ssn = scaler.inverse_transform(pred_norm.reshape(-1, 1)).flatten()

    # Gerar datas futuras
    last_date = df["date"].iloc[-1]
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=n_months,
        freq="MS",
    )

    # Construir resultado
    predictions = []
    for i in range(min(n_months, len(pred_ssn))):
        ssn_val = max(0.0, float(pred_ssn[i]))
        risk = classify_risk(ssn_val)
        predictions.append({
            "month": future_dates[i].strftime("%Y-%m"),
            "ssn_predicted": round(ssn_val, 1),
            "risk": risk,
        })

    peak_score = max(p["risk"]["score"] for p in predictions)
    peak_risk = next(p["risk"] for p in predictions if p["risk"]["score"] == peak_score)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_mae_ssn": meta["mae_test"],
        "input_window": {
            "from": input_dates[0],
            "to": input_dates[-1],
            "months": window,
        },
        "predictions": predictions,
        "peak_risk": peak_risk,
        "summary": (
            f"Previsão para os próximos {len(predictions)} meses: "
            f"pico de atividade '{peak_risk['level']}' "
            f"(SSN máximo previsto: {max(p['ssn_predicted'] for p in predictions):.1f})"
        ),
    }
    return result


def run(n_months: int = None, output: str = "human"):
    result = predict(n_months)

    if output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # Saída legível
    print("\n" + "=" * 60)
    print("  HeliOS LSTM — Previsão de Atividade Solar")
    print("=" * 60)
    print(f"  Gerado em: {result['generated_at']}")
    print(f"  Janela de entrada: {result['input_window']['from']} → {result['input_window']['to']}")
    print(f"  Margem de erro do modelo: ±{result['model_mae_ssn']:.1f} SSN")
    print(f"\n  {'Mês':<10} {'SSN Previsto':>14}  {'Nível de Risco'}")
    print(f"  {'─'*10} {'─'*14}  {'─'*30}")
    for p in result["predictions"]:
        icon = {"QUIET": "🟢", "ACTIVE": "🟡", "ELEVATED": "🟠", "STORM": "🔴"}.get(p["risk"]["level"], "⚪")
        print(f"  {p['month']:<10} {p['ssn_predicted']:>12.1f}  {icon} {p['risk']['level']}")
    print(f"\n  PICO: {result['peak_risk']['level']} — {result['peak_risk']['description']}")
    print(f"\n  {result['summary']}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HeliOS LSTM — Previsão")
    parser.add_argument("--months", type=int, default=None, help="Quantos meses prever")
    parser.add_argument("--output", choices=["human", "json"], default="human")
    args = parser.parse_args()
    run(n_months=args.months, output=args.output)
