"""
evaluate.py — Avaliação do modelo LSTM treinado
HeliOS | Global Solution 2026.1 — FIAP

═══════════════════════════════════════════════════════════════════
CONCEITO: O QUE ESTAMOS MEDINDO
═══════════════════════════════════════════════════════════════════

Após o treino, precisamos responder: "o modelo aprendeu algo útil
ou apenas memorizou os dados de treino?"

Métricas utilizadas:
  - MAE  (Mean Absolute Error): erro médio em unidades reais de SSN
    "Em média o modelo erra X manchas solares"
  - RMSE (Root Mean Squared Error): penaliza erros grandes mais que
    o MAE. Útil para detectar previsões muito erradas.
  - Acurácia por faixa de risco: o que importa para o HeliOS não é
    prever o SSN exato, mas classificar corretamente o NÍVEL de risco.
    Um erro de 10 SSN no nível "quieto" é inofensivo. O mesmo erro
    na fronteira "tempestade" pode custar alertas perdidos.

Faixas de risco (baseadas em SSN proxy do Kp):
  QUIET:  SSN < 50
  ACTIVE: 50 ≤ SSN < 120
  STORM:  SSN ≥ 120

Uso:
    python src/ml/lstm/evaluate.py
"""

import json
import pickle
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    ConfusionMatrixDisplay,
)
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf

# ─── Caminhos ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = ROOT / "data" / "processed" / "solar_cycle_historical.csv"
MODEL_DIR = Path(__file__).parent / "model"
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

WINDOW_SIZE = 24
HORIZON = 6


def classify_risk(ssn: float) -> str:
    """Converte SSN em categoria de risco geomagnético."""
    if ssn < 50:
        return "QUIET"
    elif ssn < 120:
        return "ACTIVE"
    else:
        return "STORM"


def run():
    print("=" * 60)
    print("  HeliOS LSTM — Avaliação do Modelo")
    print("=" * 60)

    # Carregar metadados do treino
    meta_path = MODEL_DIR / "model_meta.json"
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
        window = meta["window_size"]
        horizon = meta["horizon"]
        print(f"\n  Janela: {window} meses | Horizonte: {horizon} meses")
        print(f"  MAE de treino reportado: {meta['mae_test']:.2f}")
        print(f"  Épocas treinadas: {meta['epochs_trained']}")
    else:
        window, horizon = WINDOW_SIZE, HORIZON

    # Carregar modelo e scaler
    model = tf.keras.models.load_model(str(MODEL_DIR / "helios_lstm.keras"))
    with open(MODEL_DIR / "scaler.pkl", "rb") as f:
        scaler: MinMaxScaler = pickle.load(f)

    # Carregar e preparar dados
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["time-tag"], format="%Y-%m")
    df = df.sort_values("date").reset_index(drop=True)
    df["ssn"] = df["ssn"].fillna(0).clip(lower=0).astype(float)

    series = df["ssn"].values.astype(float)
    series_norm = scaler.transform(series.reshape(-1, 1)).flatten()

    # Reconstruir conjunto de teste (últimos 10%)
    X_all, y_all, dates_all = [], [], []
    for i in range(len(series_norm) - window - horizon + 1):
        X_all.append(series_norm[i:i + window])
        y_all.append(series_norm[i + window:i + window + horizon])
        dates_all.append(df["date"].iloc[i + window])

    X_all = np.array(X_all).reshape(-1, window, 1)
    y_all = np.array(y_all)

    n = len(X_all)
    test_start = int(n * 0.90)
    X_test = X_all[test_start:]
    y_test = y_all[test_start:]
    dates_test = dates_all[test_start:]

    # Previsão
    y_pred_norm = model.predict(X_test, verbose=0)
    y_pred = scaler.inverse_transform(y_pred_norm)
    y_true = scaler.inverse_transform(y_test)

    # ─── Métricas numéricas ────────────────────────────────────────
    mae = mean_absolute_error(y_true.flatten(), y_pred.flatten())
    rmse = np.sqrt(mean_squared_error(y_true.flatten(), y_pred.flatten()))

    print(f"\n{'─'*40}")
    print("  Métricas no conjunto de teste:")
    print(f"  MAE:  {mae:.2f} manchas solares")
    print(f"  RMSE: {rmse:.2f} manchas solares")

    # ─── Acurácia por classe de risco ──────────────────────────────
    # Usamos apenas o primeiro mês previsto para a classificação
    y_true_class = [classify_risk(v) for v in y_true[:, 0]]
    y_pred_class = [classify_risk(v) for v in y_pred[:, 0]]

    print(f"\n{'─'*40}")
    print("  Acurácia por classe de risco (1º mês previsto):")
    print(classification_report(y_true_class, y_pred_class,
                                 labels=["QUIET", "ACTIVE", "STORM"],
                                 zero_division=0))

    # ─── Gráficos ──────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # 1. Previsão vs Real (primeiro mês do horizonte)
    ax = axes[0]
    ax.plot(dates_test, y_true[:, 0], label="Real (SSN)", color="steelblue", linewidth=1.5)
    ax.plot(dates_test, y_pred[:, 0], label="Previsto (LSTM)", color="orange",
            linestyle="--", linewidth=1.5)
    ax.axhline(50, color="green", linestyle=":", alpha=0.5, label="Limiar ACTIVE (50)")
    ax.axhline(120, color="red", linestyle=":", alpha=0.5, label="Limiar STORM (120)")
    ax.set_title(f"HeliOS LSTM — Previsão vs Real | MAE={mae:.1f} SSN, RMSE={rmse:.1f} SSN")
    ax.set_xlabel("Data")
    ax.set_ylabel("Sunspot Number (SSN)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. Matriz de confusão
    ax = axes[1]
    labels = ["QUIET", "ACTIVE", "STORM"]
    cm = confusion_matrix(y_true_class, y_pred_class, labels=labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title("Matriz de Confusão — Classificação de Risco")

    plt.tight_layout()
    out_path = DOCS_DIR / "lstm_evaluation.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"\n  Gráfico de avaliação salvo em: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    run()
