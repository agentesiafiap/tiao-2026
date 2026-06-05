"""
train.py — Treinamento da rede LSTM para previsão de atividade solar
HeliOS | Global Solution 2026.1 — FIAP

═══════════════════════════════════════════════════════════════════
CONCEITO: O QUE É UMA LSTM E POR QUE USAMOS AQUI?
═══════════════════════════════════════════════════════════════════

Uma LSTM (Long Short-Term Memory) é um tipo especial de rede neural
recorrente (RNN) que resolve o problema do "gradiente que some" nas
RNNs tradicionais. Ela possui células de memória que aprendem:
  - O QUE guardar em memória de longo prazo
  - O QUE esquecer quando não é mais relevante
  - O QUE usar para fazer a previsão atual

Para séries temporais como a atividade solar, isso é ideal: o modelo
aprende que o ciclo solar tem ~11 anos e usa esse padrão na previsão.

═══════════════════════════════════════════════════════════════════
DADOS: O QUE ESTAMOS USANDO
═══════════════════════════════════════════════════════════════════

Fonte: NOAA Solar Cycle Indices (1749–2026)
Coluna principal: SSN (Sunspot Number — número de manchas solares)
  - Proxy da atividade solar: mais manchas = mais ativo = mais risco
  - Escala: 0 (sol quieto) a ~300 (máximo do ciclo solar 25 em 2024)
  - Correlacionado ao índice Kp geomagnético

═══════════════════════════════════════════════════════════════════
ARQUITETURA DA REDE
═══════════════════════════════════════════════════════════════════

  Entrada: janela de WINDOW_SIZE meses de SSN normalizado [0,1]
     ↓
  LSTM(64 unidades, return_sequences=True)
     - retorna sequência completa para a próxima camada LSTM
     ↓
  Dropout(0.2) — desliga 20% dos neurônios aleatoriamente no treino
     - previne overfitting (memorização em vez de aprendizado)
     ↓
  LSTM(32 unidades)
     - processa a sequência e comprime em estado interno
     ↓
  Dropout(0.2)
     ↓
  Dense(HORIZON) — camada de saída linear
     - prevê SSN para os próximos HORIZON meses

Uso:
    python src/ml/lstm/train.py
    python src/ml/lstm/train.py --epochs 100 --window 36 --horizon 12
"""

import argparse
import os
import os
# Desabilita XLA/JIT do TensorFlow — causa congelamento na Época 1
# em macOS ARM (Apple Silicon) com Python 3.13
os.environ["TF_XLA_FLAGS"] = "--tf_xla_auto_jit=0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # força CPU explícito

import pickle
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # sem display gráfico — salva em arquivo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import tensorflow as tf
tf.config.optimizer.set_jit(False)  # desabilita XLA globalmente
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# ─── Caminhos ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = ROOT / "data" / "processed" / "solar_cycle_historical.csv"
MODEL_DIR = Path(__file__).parent / "model"
MODEL_DIR.mkdir(exist_ok=True)
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

# ─── Hiperparâmetros padrão ────────────────────────────────────────────────────
WINDOW_SIZE = 24   # meses de histórico usados como entrada (2 anos)
HORIZON = 6        # meses a prever (6 meses à frente)
EPOCHS = 80
BATCH_SIZE = 32
RANDOM_SEED = 42

# ─── Modo rápido (--fast) ─────────────────────────────────────────────────────
# Usa últimos 600 meses (~5 ciclos solares), janela menor e batch maior.
# Reduz épocas de horas para ~3 minutos em CPU sem GPU.
FAST_LAST_N = 600   # meses mais recentes a usar
FAST_WINDOW = 12    # janela de 1 ano (suficiente para capturar sazonalidade solar)
FAST_HORIZON = 6    # mantém 6 meses de previsão
FAST_EPOCHS = 50    # menos épocas (EarlyStopping geralmente para antes)
FAST_BATCH = 64     # batch maior = menos atualizações por época = mais rápido

tf.random.set_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ─── 1. CARREGAMENTO E INSPEÇÃO DOS DADOS ─────────────────────────────────────
def load_data(fast: bool = False) -> pd.DataFrame:
    print("\n[1/6] Carregando dados históricos...")
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["time-tag"], format="%Y-%m")
    df = df.sort_values("date").reset_index(drop=True)

    # SSN pode ter valores negativos (meses de mínimo solar) — zeramos
    df["ssn"] = df["ssn"].fillna(0).clip(lower=0).astype(float)

    if fast:
        df = df.tail(FAST_LAST_N).reset_index(drop=True)
        print(f"  [MODO RÁPIDO] Usando últimos {FAST_LAST_N} meses ({FAST_LAST_N//12:.0f} anos)")

    print(f"  Período: {df['date'].iloc[0].strftime('%Y-%m')} → {df['date'].iloc[-1].strftime('%Y-%m')}")
    print(f"  Total de registros mensais: {len(df)}")
    print(f"  SSN médio: {df['ssn'].mean():.1f} | máximo: {df['ssn'].max():.1f}")
    return df


# ─── 2. NORMALIZAÇÃO ──────────────────────────────────────────────────────────
def normalize(series: np.ndarray) -> tuple[np.ndarray, MinMaxScaler]:
    """
    Normaliza para [0, 1] com MinMaxScaler.

    Por que normalizar? A LSTM usa funções de ativação (tanh, sigmoid)
    cujo domínio efetivo é [-1, 1]. Valores grandes (SSN ~ 300) fariam
    os gradientes saturar e o treino não convergir.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    normalized = scaler.fit_transform(series.reshape(-1, 1)).flatten()
    return normalized, scaler


# ─── 3. CRIAÇÃO DAS JANELAS DESLIZANTES ───────────────────────────────────────
def create_windows(series: np.ndarray, window: int, horizon: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Transforma uma série 1D em pares (X, y) para treino supervisionado.

    Exemplo com window=3, horizon=2 e série [1,2,3,4,5,6,7]:
      X[0] = [1,2,3]  →  y[0] = [4,5]
      X[1] = [2,3,4]  →  y[1] = [5,6]
      X[2] = [3,4,5]  →  y[2] = [6,7]

    Cada X terá shape (window, 1) — a dimensão 1 é o número de features.
    A LSTM espera entrada no formato: (amostras, timesteps, features)
    """
    X, y = [], []
    for i in range(len(series) - window - horizon + 1):
        X.append(series[i : i + window])
        y.append(series[i + window : i + window + horizon])
    X = np.array(X).reshape(-1, window, 1)
    y = np.array(y)
    return X, y


# ─── 4. SPLIT TEMPORAL ────────────────────────────────────────────────────────
def temporal_split(X: np.ndarray, y: np.ndarray) -> tuple:
    """
    Divisão TEMPORAL (nunca aleatória para séries temporais!).

    Por que não shuffle? Se misturarmos passado e futuro, o modelo
    "aprende" que 2025 prevê 1995 — o que é impossível na realidade.
    O split temporal garante que o modelo só vê o passado no treino.

    80% treino | 10% validação | 10% teste
    """
    n = len(X)
    train_end = int(n * 0.80)
    val_end = int(n * 0.90)

    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:val_end], y[train_end:val_end]
    X_test, y_test = X[val_end:], y[val_end:]

    print(f"\n[3/6] Split temporal:")
    print(f"  Treino:    {len(X_train):4d} amostras  (80%)")
    print(f"  Validação: {len(X_val):4d} amostras  (10%)")
    print(f"  Teste:     {len(X_test):4d} amostras  (10%)")
    return X_train, y_train, X_val, y_val, X_test, y_test


# ─── 5. CONSTRUÇÃO DO MODELO ──────────────────────────────────────────────────
def build_model(window: int, horizon: int) -> tf.keras.Model:
    """
    Arquitetura LSTM Bidirecional empilhada.

    Camada 1 — LSTM(64, return_sequences=True):
      Lê a sequência inteira e retorna estado a cada passo.
      É como um leitor que anota o que vê em cada mês.

    Camada 2 — LSTM(32):
      Recebe a sequência anotada e comprime em um vetor de estado.
      É como o leitor fazendo um resumo após ler tudo.

    Camada 3 — Dense(horizon):
      Mapeia o resumo para as previsões futuras.
      Uma saída por mês a prever.
    """
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(window, 1)),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(horizon),
    ], name="helios_lstm")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="mse",        # Mean Squared Error — penaliza erros grandes
        metrics=["mae"],   # Mean Absolute Error — mais interpretável
        jit_compile=False, # desabilita XLA para evitar congelamento em macOS ARM
    )

    print(f"\n[4/6] Arquitetura do modelo:")
    model.summary()
    return model


# ─── 6. TREINO ────────────────────────────────────────────────────────────────
def train_model(model, X_train, y_train, X_val, y_val, epochs: int, batch_size: int = BATCH_SIZE) -> tf.keras.callbacks.History:
    callbacks = [
        EarlyStopping(
            monitor="val_loss",
            patience=15,         # para se não melhorar em 15 épocas
            restore_best_weights=True,
            verbose=1,
        ),
        ModelCheckpoint(
            str(MODEL_DIR / "helios_lstm_best.keras"),
            monitor="val_loss",
            save_best_only=True,
            verbose=0,
        ),
    ]

    print(f"\n[5/6] Treinando por até {epochs} épocas (EarlyStopping patience=15)...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1,
    )
    return history


# ─── 7. AVALIAÇÃO E PERSISTÊNCIA ──────────────────────────────────────────────
def evaluate_and_save(model, scaler, history, X_test, y_test, window, horizon):
    print(f"\n[6/6] Avaliando no conjunto de teste...")

    # Previsão em escala normalizada → desnormaliza para SSN real
    y_pred_norm = model.predict(X_test, verbose=0)
    y_pred = scaler.inverse_transform(y_pred_norm)
    y_true = scaler.inverse_transform(y_test)

    mae = mean_absolute_error(y_true.flatten(), y_pred.flatten())
    rmse = np.sqrt(mean_squared_error(y_true.flatten(), y_pred.flatten()))

    print(f"  MAE  (Mean Absolute Error):  {mae:.2f} manchas solares")
    print(f"  RMSE (Root Mean Sq. Error):  {rmse:.2f} manchas solares")
    print(f"  (Para referência: SSN médio histórico ~ 80, máximo ~ 300)")

    # Salvar modelo final
    model_path = MODEL_DIR / "helios_lstm.keras"
    model.save(str(model_path))
    print(f"\n  Modelo salvo em: {model_path}")

    # Salvar scaler (necessário para desnormalizar previsões futuras)
    scaler_path = MODEL_DIR / "scaler.pkl"
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    print(f"  Scaler salvo em: {scaler_path}")

    # Salvar metadados do modelo
    meta = {
        "window_size": window,
        "horizon": horizon,
        "mae_test": float(mae),
        "rmse_test": float(rmse),
        "epochs_trained": len(history.history["loss"]),
        "feature": "ssn",
    }
    import json
    with open(MODEL_DIR / "model_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Gerar gráfico de curvas de loss
    _plot_training(history, mae, rmse)

    return mae, rmse


def _plot_training(history, mae, rmse):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Curvas de loss
    ax = axes[0]
    ax.plot(history.history["loss"], label="Train Loss (MSE)", color="steelblue")
    ax.plot(history.history["val_loss"], label="Val Loss (MSE)", color="orange")
    ax.set_title("Curvas de Treinamento — HeliOS LSTM")
    ax.set_xlabel("Época")
    ax.set_ylabel("MSE")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Curvas de MAE
    ax = axes[1]
    ax.plot(history.history["mae"], label="Train MAE", color="steelblue")
    ax.plot(history.history["val_mae"], label="Val MAE", color="orange")
    ax.set_title(f"MAE no Teste: {mae:.2f} SSN | RMSE: {rmse:.2f} SSN")
    ax.set_xlabel("Época")
    ax.set_ylabel("MAE (manchas solares)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = DOCS_DIR / "lstm_training_metrics.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Gráfico de treino salvo em: {out_path}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def run(epochs: int = EPOCHS, window: int = WINDOW_SIZE, horizon: int = HORIZON, fast: bool = False):
    if fast:
        window = FAST_WINDOW
        horizon = FAST_HORIZON
        epochs = FAST_EPOCHS

    print("=" * 60)
    print("  HeliOS LSTM — Treinamento")
    print(f"  Janela: {window} meses | Horizonte: {horizon} meses")
    if fast:
        print(f"  Modo: RÁPIDO (CPU-optimizado, ~3 min)")
    print("=" * 60)

    # 1. Dados
    df = load_data(fast=fast)
    series = df["ssn"].values.astype(float)

    # 2. Normalização
    print("\n[2/6] Normalizando série SSN para [0, 1]...")
    series_norm, scaler = normalize(series)

    # 3. Janelas + Split
    X, y = create_windows(series_norm, window, horizon)
    X_train, y_train, X_val, y_val, X_test, y_test = temporal_split(X, y)

    # 4. Modelo
    model = build_model(window, horizon)

    # 5. Treino — batch maior no modo rápido
    batch = FAST_BATCH if fast else BATCH_SIZE
    history = train_model(model, X_train, y_train, X_val, y_val, epochs, batch)

    # 6. Avaliação e salvamento
    mae, rmse = evaluate_and_save(model, scaler, history, X_test, y_test, window, horizon)

    print("\n" + "=" * 60)
    print("  Treinamento concluído!")
    print(f"  MAE final: {mae:.2f} | RMSE: {rmse:.2f}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HeliOS LSTM — Treinamento")
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--window", type=int, default=WINDOW_SIZE)
    parser.add_argument("--horizon", type=int, default=HORIZON)
    parser.add_argument("--fast", action="store_true",
                        help="Modo rápido: últimos 600 meses, janela=12, batch=64 (~3 min em CPU)")
    args = parser.parse_args()
    run(epochs=args.epochs, window=args.window, horizon=args.horizon, fast=args.fast)
