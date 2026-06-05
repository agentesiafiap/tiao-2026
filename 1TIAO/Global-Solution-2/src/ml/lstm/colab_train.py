# ============================================================
#  HeliOS LSTM — Treinamento no Google Colab (com GPU)
#  HeliOS | Global Solution 2026.1 — FIAP
# ============================================================
#
#  INSTRUÇÕES:
#  1. Abra https://colab.research.google.com
#  2. Menu: Runtime > Change runtime type > T4 GPU
#  3. Cole este arquivo inteiro em uma única célula e execute
#  4. Quando terminar, baixe os 3 arquivos da pasta /content/model/:
#       - helios_lstm.keras
#       - scaler.pkl
#       - model_meta.json
#  5. Coloque os 3 arquivos em: src/ml/lstm/model/
#
#  ARQUIVO DE DADOS NECESSÁRIO:
#  Faça upload do arquivo abaixo antes de executar:
#       data/processed/solar_cycle_historical.csv
#  Use o painel de arquivos do Colab (ícone de pasta à esquerda)
#  e arraste o CSV para /content/
# ============================================================

# ── Célula 1: Instalar dependências ──────────────────────────
# (execute separadamente se quiser ver o progresso)
# !pip install -q tensorflow scikit-learn matplotlib

# ── Célula 2: Código completo de treinamento ─────────────────

import os
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

import tensorflow as tf
print(f"TensorFlow: {tf.__version__}")
print(f"GPU disponível: {tf.config.list_physical_devices('GPU')}")

# ─── Caminhos ────────────────────────────────────────────────
DATA_PATH = "/content/solar_cycle_historical.csv"   # arquivo que você fez upload
MODEL_DIR = Path("/content/model")
MODEL_DIR.mkdir(exist_ok=True)

# ─── Hiperparâmetros (modo rápido, mesmos do --fast local) ───
WINDOW_SIZE = 12
HORIZON = 6
EPOCHS = 50
BATCH_SIZE = 64
RANDOM_SEED = 42

tf.random.set_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ─── 1. Carregar dados ───────────────────────────────────────
print("\n[1/6] Carregando dados históricos...")
df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["time-tag"], format="%Y-%m")
df = df.sort_values("date").reset_index(drop=True)
df["ssn"] = df["ssn"].fillna(0).clip(lower=0).astype(float)

# Usar últimos 600 meses (~50 anos = 5 ciclos solares)
df = df.tail(600).reset_index(drop=True)
print(f"  Período: {df['date'].iloc[0].strftime('%Y-%m')} → {df['date'].iloc[-1].strftime('%Y-%m')}")
print(f"  Registros: {len(df)} | SSN médio: {df['ssn'].mean():.1f} | máximo: {df['ssn'].max():.1f}")

# ─── 2. Normalizar ───────────────────────────────────────────
print("\n[2/6] Normalizando SSN para [0, 1]...")
scaler = MinMaxScaler(feature_range=(0, 1))
series_norm = scaler.fit_transform(df["ssn"].values.reshape(-1, 1)).flatten()

# ─── 3. Janelas deslizantes ──────────────────────────────────
print("\n[3/6] Criando janelas deslizantes...")
X, y = [], []
for i in range(len(series_norm) - WINDOW_SIZE - HORIZON + 1):
    X.append(series_norm[i : i + WINDOW_SIZE])
    y.append(series_norm[i + WINDOW_SIZE : i + WINDOW_SIZE + HORIZON])
X = np.array(X).reshape(-1, WINDOW_SIZE, 1)
y = np.array(y)

# ─── 4. Split temporal ───────────────────────────────────────
n = len(X)
train_end = int(n * 0.80)
val_end   = int(n * 0.90)

X_train, y_train = X[:train_end], y[:train_end]
X_val,   y_val   = X[train_end:val_end], y[train_end:val_end]
X_test,  y_test  = X[val_end:], y[val_end:]

print(f"  Treino: {len(X_train)} | Validação: {len(X_val)} | Teste: {len(X_test)}")

# ─── 5. Modelo ───────────────────────────────────────────────
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(WINDOW_SIZE, 1)),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(HORIZON),
], name="helios_lstm")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="mse",
    metrics=["mae"],
)
model.summary()

# ─── 6. Treino ───────────────────────────────────────────────
callbacks = [
    EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True, verbose=1),
    ModelCheckpoint(str(MODEL_DIR / "helios_lstm_best.keras"), monitor="val_loss",
                    save_best_only=True, verbose=0),
]

print(f"\n[5/6] Treinando ({EPOCHS} épocas, EarlyStopping patience=15)...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1,
)

# ─── 7. Avaliação ────────────────────────────────────────────
print("\n[6/6] Avaliando no conjunto de teste...")
y_pred_norm = model.predict(X_test, verbose=0)
y_pred = scaler.inverse_transform(y_pred_norm)
y_true = scaler.inverse_transform(y_test)

mae  = mean_absolute_error(y_true.flatten(), y_pred.flatten())
rmse = np.sqrt(mean_squared_error(y_true.flatten(), y_pred.flatten()))
print(f"  MAE:  {mae:.2f} manchas solares")
print(f"  RMSE: {rmse:.2f} manchas solares")

# ─── 8. Salvar modelo ────────────────────────────────────────
model.save(str(MODEL_DIR / "helios_lstm.keras"))
print(f"  Modelo salvo em: {MODEL_DIR / 'helios_lstm.keras'}")

with open(MODEL_DIR / "scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
print(f"  Scaler salvo em: {MODEL_DIR / 'scaler.pkl'}")

meta = {
    "window_size": WINDOW_SIZE,
    "horizon": HORIZON,
    "mae_test": float(mae),
    "rmse_test": float(rmse),
    "epochs_trained": len(history.history["loss"]),
    "feature": "ssn",
    "trained_on": "Google Colab (GPU)",
    "last_n_months": 600,
}
with open(MODEL_DIR / "model_meta.json", "w") as f:
    json.dump(meta, f, indent=2)
print(f"  Metadados salvos em: {MODEL_DIR / 'model_meta.json'}")

# ─── 9. Gráfico de treinamento ───────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(history.history["loss"], label="Train Loss (MSE)", color="steelblue")
ax.plot(history.history["val_loss"], label="Val Loss (MSE)", color="orange")
ax.set_title("Curvas de Treinamento — HeliOS LSTM")
ax.set_xlabel("Época"); ax.set_ylabel("MSE"); ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(history.history["mae"], label="Train MAE", color="steelblue")
ax.plot(history.history["val_mae"], label="Val MAE", color="orange")
ax.set_title(f"MAE no Teste: {mae:.2f} SSN | RMSE: {rmse:.2f} SSN")
ax.set_xlabel("Época"); ax.set_ylabel("MAE"); ax.legend(); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("/content/model/lstm_training_metrics.png", dpi=150)
plt.show()
print("\n  Gráfico salvo em: /content/model/lstm_training_metrics.png")

print("\n" + "=" * 60)
print("  TREINAMENTO CONCLUÍDO!")
print(f"  MAE: {mae:.2f} | RMSE: {rmse:.2f} | Épocas: {len(history.history['loss'])}")
print("=" * 60)
print("\n  PRÓXIMOS PASSOS:")
print("  1. Baixe os arquivos da pasta /content/model/ (painel de arquivos)")
print("  2. Coloque em: src/ml/lstm/model/")
print("  3. Copie lstm_training_metrics.png para: docs/")

# ─── 10. Download automático (descomente se quiser) ──────────
from google.colab import files
for fname in ["helios_lstm.keras", "scaler.pkl", "model_meta.json", "lstm_training_metrics.png"]:
    files.download(f"/content/model/{fname}")
