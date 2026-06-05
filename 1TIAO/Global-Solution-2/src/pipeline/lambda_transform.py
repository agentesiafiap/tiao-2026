"""
lambda_transform.py — Lambda handler para transformação e roteamento de dados
HeliOS | Global Solution 2026.1 — FIAP

Acionada por S3 Event Notification (ou manualmente) após ingestão.
Lê dados brutos do S3, normaliza e grava em:
  - DynamoDB: leituras Kp em tempo real
  - S3 processed/: dados normalizados para uso pelo LSTM

Handler: lambda_transform.lambda_handler
Runtime: python3.12
"""

import json
import os
import traceback
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import boto3
import requests

S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "helios-solar-data")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DYNAMO_TABLE_KP = os.environ.get("DYNAMODB_TABLE_NAME", "helios-kp-realtime")
KP_ALERT_THRESHOLD = float(os.environ.get("KP_ALERT_THRESHOLD", "5"))

s3 = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

TMP = Path("/tmp")


# ─── Transformação Kp ──────────────────────────────────────────────────────────

def transform_kp(s3_key: str) -> dict:
    """
    Lê arquivo Kp bruto do S3, normaliza e grava cada leitura no DynamoDB.
    Classifica o nível de alerta por faixa de Kp:
      0-2: Quieto | 3-4: Ativo | 5-6: Tempestade G1-G2 | 7+: Tempestade G3+
    """
    tmp_path = TMP / "kp_raw.json"
    s3.download_file(S3_BUCKET, s3_key, str(tmp_path))
    raw = json.loads(tmp_path.read_text())
    records = raw.get("records", [])

    table = dynamodb.Table(DYNAMO_TABLE_KP)
    written = 0
    alerts = []

    with table.batch_writer() as batch:
        for rec in records:
            time_tag = rec.get("time_tag", "")
            kp_raw = rec.get("kp_index")
            if not time_tag or kp_raw is None:
                continue

            try:
                kp = float(kp_raw)
            except (TypeError, ValueError):
                continue

            # Classificação de nível de alerta
            if kp < 3:
                alert_level = "QUIET"
            elif kp < 5:
                alert_level = "ACTIVE"
            elif kp < 7:
                alert_level = "STORM_G1_G2"
            else:
                alert_level = "STORM_G3_PLUS"

            item = {
                "timestamp": time_tag,
                "kp_index": Decimal(str(round(kp, 2))),
                "alert_level": alert_level,
                "source": "NOAA_SWPC",
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "ttl": int((datetime.now(timezone.utc).timestamp()) + 7 * 24 * 3600),  # TTL 7 dias
            }
            batch.put_item(Item=item)
            written += 1

            if kp >= KP_ALERT_THRESHOLD:
                alerts.append({"time": time_tag, "kp": kp, "level": alert_level})

    print(f"[TRANSFORM/KP] {written} leituras gravadas no DynamoDB '{DYNAMO_TABLE_KP}'")
    if alerts:
        print(f"[TRANSFORM/KP] ⚠ {len(alerts)} leituras acima do limiar Kp≥{KP_ALERT_THRESHOLD}")

    return {"written": written, "alerts": len(alerts)}


# ─── Transformação DONKI ───────────────────────────────────────────────────────

def transform_donki(s3_key: str) -> dict:
    """
    Normaliza eventos DONKI e salva em S3 processed/ como JSON estruturado.
    (Carga no RDS PostgreSQL será feita na Fase 4 via seed.py)
    """
    tmp_path = TMP / "donki_raw.json"
    s3.download_file(S3_BUCKET, s3_key, str(tmp_path))
    raw = json.loads(tmp_path.read_text())

    events = raw.get("events", {})
    normalized = []

    event_type_map = {"FLR": "solar_flare", "CME": "cme", "GST": "geomagnetic_storm", "SEP": "sep"}

    for event_type, records in events.items():
        mapped_type = event_type_map.get(event_type, event_type.lower())
        for rec in (records or []):
            normalized.append({
                "event_type": mapped_type,
                "event_id": rec.get("flrID") or rec.get("activityID") or rec.get("gstID") or rec.get("sepID", ""),
                "start_time": rec.get("beginTime") or rec.get("startTime", ""),
                "peak_time": rec.get("peakTime", ""),
                "end_time": rec.get("endTime", ""),
                "class_type": rec.get("classType", ""),
                "source_location": rec.get("sourceLocation", ""),
                "raw": rec,
            })

    date_str = raw.get("period", {}).get("end", "unknown")
    out_key = f"processed/donki/normalized_{date_str}.json"
    tmp_out = TMP / "donki_normalized.json"
    tmp_out.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    s3.upload_file(str(tmp_out), S3_BUCKET, out_key)

    print(f"[TRANSFORM/DONKI] {len(normalized)} eventos normalizados → s3://{S3_BUCKET}/{out_key}")
    return {"normalized": len(normalized)}


# ─── Handler ───────────────────────────────────────────────────────────────────

def lambda_handler(event: dict, context) -> dict:
    """
    Ponto de entrada da Lambda de transformação.
    Pode ser invocada:
      - Manualmente (event com 'transform_kp_key' e/ou 'transform_donki_key')
      - Via S3 Event Notification (Records[].s3.object.key)
    """
    print(f"[HeliOS-Transform] Iniciando — {datetime.now(timezone.utc).isoformat()}")
    print(f"Event: {json.dumps(event)}")

    results = {}
    errors = []

    # Detectar invocação via S3 Event
    s3_records = event.get("Records", [])
    kp_keys = []
    donki_keys = []

    for rec in s3_records:
        key = rec.get("s3", {}).get("object", {}).get("key", "")
        if "raw/kp/" in key:
            kp_keys.append(key)
        elif "raw/donki/" in key:
            donki_keys.append(key)

    # Invocação manual com chaves explícitas
    if not s3_records:
        if kp_key := event.get("transform_kp_key"):
            kp_keys.append(kp_key)
        if donki_key := event.get("transform_donki_key"):
            donki_keys.append(donki_key)

    # Processar Kp
    for key in kp_keys:
        try:
            results[f"kp:{key}"] = transform_kp(key)
        except Exception as exc:
            print(f"[ERROR] transform_kp({key}): {traceback.format_exc()}")
            results[f"kp:{key}"] = {"error": str(exc)}
            errors.append(key)

    # Processar DONKI
    for key in donki_keys:
        try:
            results[f"donki:{key}"] = transform_donki(key)
        except Exception as exc:
            print(f"[ERROR] transform_donki({key}): {traceback.format_exc()}")
            results[f"donki:{key}"] = {"error": str(exc)}
            errors.append(key)

    if not kp_keys and not donki_keys:
        print("[WARN] Nenhuma chave S3 identificada para transformar.")
        results["warning"] = "no_keys_found"

    status_code = 200 if not errors else 207
    body = {
        "transform_time": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "errors": errors,
    }

    return {"statusCode": status_code, "body": json.dumps(body)}
