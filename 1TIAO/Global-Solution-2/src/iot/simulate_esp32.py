"""
simulate_esp32.py — Simulador Python do ESP32 HeliOS Magnetômetro
HeliOS | Global Solution 2026.1 — FIAP

═══════════════════════════════════════════════════════════════════
CONCEITO: O QUE ESTE MÓDULO SIMULA?
═══════════════════════════════════════════════════════════════════

Um ESP32 físico com sensor de campo magnético (ex: QMC5883L ou
HMC5883L) instalado em uma estação terrestre publicaria leituras
via MQTT para a nuvem. Este script Python reproduz exatamente
esse comportamento:

  1. Gera leituras sintéticas de campo magnético (nanoTeslas)
     com variação senoidal (ciclo solar ~11 anos) + ruído realista
  2. Publica via MQTT em formato JSON no tópico:
       helios/magnetometer
  3. Simultaneamente escreve no DynamoDB helios-kp-realtime
     (substitui o IoT Rule que precisaria do AWS IoT Core)

NOTA SOBRE AMBIENTE VOCAREUM/LAB:
  O AWS Vocareum não permite aws iot:CreateThing nem certificados
  mTLS. Por isso usamos o broker público HiveMQ (gratuito) para
  demonstrar o protocolo MQTT e escrevemos diretamente no DynamoDB.

LEITURAS SINTÉTICAS:
  Baseadas no campo magnético típico de São Paulo (~23.000 nT):
  - Campo quieto:    22.000 – 24.000 nT
  - Tempestade leve: 18.000 – 22.000 nT (SSC — Sudden Storm Commencement)
  - Tempestade forte: < 18.000 nT (Dst < -50 nT)

Uso:
    python src/iot/simulate_esp32.py              # 10 publicações (padrão)
    python src/iot/simulate_esp32.py --count 30   # 30 publicações
    python src/iot/simulate_esp32.py --interval 5 # a cada 5 segundos
    python src/iot/simulate_esp32.py --storm       # modo tempestade (campo deprimido)
"""

import argparse
import json
import math
import random
import time
import uuid
from datetime import datetime, timezone

import boto3

# ─── Configurações do simulador ───────────────────────────────────────────────
DEVICE_ID       = "helios-station-BR-001"
LATITUDE        = -23.5505   # São Paulo
LONGITUDE       = -46.6333
MQTT_TOPIC      = "helios/magnetometer"
DYNAMO_TABLE    = "helios-kp-realtime"
AWS_REGION      = "us-east-1"

# Campo magnético base de São Paulo (nanoTeslas)
B_BASELINE      = 23000.0
B_QUIET_NOISE   = 200.0      # ±200 nT em condições quietas
B_STORM_DROP    = 5000.0     # queda de até 5000 nT em tempestade forte

# ─── MQTT (broker público HiveMQ — sem autenticação) ─────────────────────────
MQTT_BROKER     = "broker.hivemq.com"
MQTT_PORT       = 1883

# ─── Funções de geração de dados sintéticos ───────────────────────────────────

def generate_magnetic_reading(t: float, storm_mode: bool = False) -> dict:
    """
    Gera leitura sintética de campo magnético com padrão realista.

    Modelo:
      B(t) = B_baseline
             + variação_diurna(t)    ← variação de ~100 nT ao longo do dia
             + variação_storm(t)     ← depressão durante tempestade
             + ruído_gaussiano()     ← ruído instrumental

    Args:
        t: tempo em segundos desde início da simulação
        storm_mode: se True, simula perturbação geomagnética

    Returns:
        dict com leituras dos eixos X, Y, Z e campo total
    """
    # Variação diurna (~100 nT, período 86400s)
    diurnal = 100.0 * math.sin(2 * math.pi * t / 86400)

    # Perturbação de tempestade (queda progressiva + recuperação)
    if storm_mode:
        storm_drop = B_STORM_DROP * (0.5 + 0.5 * math.sin(2 * math.pi * t / 3600))
    else:
        storm_drop = 0.0

    # Campo total
    b_total = B_BASELINE + diurnal - storm_drop + random.gauss(0, B_QUIET_NOISE)

    # Decomposição em componentes XYZ (inclinação magnética ~-37° para SP)
    inclination = math.radians(-37.0)
    declination  = math.radians(-21.0)  # declinação magnética de SP
    b_x = b_total * math.cos(inclination) * math.cos(declination) + random.gauss(0, 50)
    b_y = b_total * math.cos(inclination) * math.sin(declination) + random.gauss(0, 50)
    b_z = b_total * math.sin(inclination)                          + random.gauss(0, 80)

    # Classificação de distúrbio geomagnético (escala Dst simplificada)
    delta = b_total - B_BASELINE
    if delta > -100:    geo_status = "QUIET"
    elif delta > -500:  geo_status = "ACTIVE"
    elif delta > -2000: geo_status = "STORM_MINOR"
    else:               geo_status = "STORM_MAJOR"

    return {
        "b_total_nT": round(b_total, 2),
        "b_x_nT":     round(b_x, 2),
        "b_y_nT":     round(b_y, 2),
        "b_z_nT":     round(b_z, 2),
        "geo_status": geo_status,
    }


def build_payload(reading: dict, storm_mode: bool) -> dict:
    """Constrói o JSON publicado pelo ESP32 (formato idêntico ao hardware real)."""
    return {
        "device_id":      DEVICE_ID,
        "latitude":       LATITUDE,
        "longitude":      LONGITUDE,
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "storm_mode":     storm_mode,
        **reading,
    }


# ─── Publicação MQTT ──────────────────────────────────────────────────────────

def publish_mqtt(payload: dict) -> bool:
    """Publica payload no broker HiveMQ público via paho-mqtt."""
    try:
        import paho.mqtt.client as mqtt

        client = mqtt.Client(client_id=f"helios-sim-{uuid.uuid4().hex[:8]}")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=10)
        result = client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
        client.disconnect()
        return result.rc == 0
    except ImportError:
        print("  [MQTT] paho-mqtt não instalado. Execute: pip install paho-mqtt")
        return False
    except Exception as e:
        print(f"  [MQTT] Falha na conexão: {e}")
        return False


# ─── Escrita no DynamoDB ──────────────────────────────────────────────────────

def write_dynamodb(payload: dict) -> bool:
    """
    Escreve leitura no DynamoDB helios-kp-realtime.

    Substitui o IoT Rule do AWS IoT Core (bloqueado no Vocareum).
    Em produção real: IoT Core Rule → DynamoDB Action faria isso automaticamente.

    Estrutura do item:
        timestamp (PK)  — ISO 8601 UTC
        device_id       — ID da estação
        kp_proxy        — proxy do índice Kp derivado do campo magnético
        geo_status      — classificação do distúrbio
        b_total_nT      — campo magnético total
        source          — "esp32_simulator"
        ttl             — 7 dias (para auto-expiração)
    """
    try:
        dynamo = boto3.resource("dynamodb", region_name=AWS_REGION)
        table  = dynamo.Table(DYNAMO_TABLE)

        # Kp proxy: derivado da depressão do campo (simplificado)
        delta_b = payload["b_total_nT"] - B_BASELINE
        kp_proxy = max(0, min(9, round(abs(delta_b) / 500, 1)))

        ttl_unix = int(time.time()) + 7 * 24 * 3600

        item = {
            "timestamp":  payload["timestamp"],
            "device_id":  payload["device_id"],
            "kp_proxy":   str(kp_proxy),
            "geo_status": payload["geo_status"],
            "b_total_nT": str(round(payload["b_total_nT"], 2)),
            "b_x_nT":     str(round(payload["b_x_nT"], 2)),
            "b_y_nT":     str(round(payload["b_y_nT"], 2)),
            "b_z_nT":     str(round(payload["b_z_nT"], 2)),
            "latitude":   str(payload["latitude"]),
            "longitude":  str(payload["longitude"]),
            "source":     "esp32_simulator",
            "ttl":        ttl_unix,
        }
        table.put_item(Item=item)
        return True
    except Exception as e:
        print(f"  [DynamoDB] Erro: {e}")
        return False


# ─── Loop principal ───────────────────────────────────────────────────────────

def run(count: int = 10, interval: float = 2.0, storm_mode: bool = False):
    print("=" * 60)
    print("  HeliOS ESP32 Simulator — Estação Magnetômetro")
    print(f"  Dispositivo : {DEVICE_ID}")
    print(f"  Localização : {LATITUDE}°, {LONGITUDE}° (São Paulo, BR)")
    print(f"  Publicações : {count} × {interval}s")
    print(f"  Modo        : {'⚡ TEMPESTADE' if storm_mode else '☀ QUIETO'}")
    print(f"  MQTT topic  : {MQTT_TOPIC} → {MQTT_BROKER}")
    print(f"  DynamoDB    : {DYNAMO_TABLE}")
    print("=" * 60)

    t_start = time.time()
    success_mqtt  = 0
    success_dynamo = 0

    for i in range(1, count + 1):
        t_elapsed = time.time() - t_start
        reading  = generate_magnetic_reading(t_elapsed, storm_mode)
        payload  = build_payload(reading, storm_mode)

        print(f"\n[{i:02d}/{count}] {payload['timestamp']}")
        print(f"  B_total: {reading['b_total_nT']:>10.2f} nT  |  Status: {reading['geo_status']}")
        print(f"  X: {reading['b_x_nT']:>8.2f} nT  Y: {reading['b_y_nT']:>8.2f} nT  Z: {reading['b_z_nT']:>8.2f} nT")

        # Publicar MQTT
        ok_mqtt = publish_mqtt(payload)
        print(f"  MQTT    : {'✅ publicado' if ok_mqtt else '⚠️  falhou (sem impacto no demo)'}")
        if ok_mqtt:
            success_mqtt += 1

        # Escrever DynamoDB
        ok_dynamo = write_dynamodb(payload)
        print(f"  DynamoDB: {'✅ gravado' if ok_dynamo else '❌ erro'}")
        if ok_dynamo:
            success_dynamo += 1

        if i < count:
            time.sleep(interval)

    print("\n" + "=" * 60)
    print(f"  Resultado: {success_dynamo}/{count} gravações no DynamoDB")
    print(f"             {success_mqtt}/{count} publicações MQTT")
    print("=" * 60)

    return success_dynamo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HeliOS ESP32 Simulator")
    parser.add_argument("--count",    type=int,   default=10,  help="Número de publicações")
    parser.add_argument("--interval", type=float, default=2.0, help="Intervalo em segundos")
    parser.add_argument("--storm",    action="store_true",     help="Modo tempestade geomagnética")
    args = parser.parse_args()
    run(count=args.count, interval=args.interval, storm_mode=args.storm)
