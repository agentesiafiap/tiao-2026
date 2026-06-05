"""
lambda_ingestion.py — Lambda handler para ingestão de dados solares
HeliOS | Global Solution 2026.1 — FIAP

Executa automaticamente a cada hora via EventBridge.
Replica a lógica dos scripts da Fase 2, adaptada ao ambiente Lambda
(sem acesso a disco local — usa /tmp para arquivos temporários).

Handler: lambda_ingestion.lambda_handler
Runtime: python3.12
"""

import json
import os
import traceback
from datetime import datetime, date, timezone
from pathlib import Path

import boto3
import requests

# Diretório temporário disponível em Lambda
TMP = Path("/tmp")

S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "helios-solar-data")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
NASA_API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")
DONKI_START = os.environ.get("DONKI_START_DATE", str(date.today()))
DONKI_END = os.environ.get("DONKI_END_DATE", str(date.today()))

s3 = boto3.client("s3", region_name=AWS_REGION)


# ─── NASA DONKI ────────────────────────────────────────────────────────────────

def ingest_donki() -> dict:
    base_url = "https://api.nasa.gov/DONKI"
    events = {"CME": "/CME", "FLR": "/FLR", "GST": "/GST", "SEP": "/SEP"}
    all_events: dict[str, list] = {}

    for event_type, endpoint in events.items():
        try:
            resp = requests.get(
                f"{base_url}{endpoint}",
                params={"startDate": DONKI_START, "endDate": DONKI_END, "api_key": NASA_API_KEY},
                timeout=25,
            )
            resp.raise_for_status()
            data = resp.json()
            all_events[event_type] = data if isinstance(data, list) else []
        except Exception as exc:
            print(f"[DONKI] Erro em {event_type}: {exc}")
            all_events[event_type] = []

    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "period": {"start": DONKI_START, "end": DONKI_END},
        "events": all_events,
    }

    today = date.today().isoformat()
    tmp_path = TMP / f"donki_{today}.json"
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    s3.upload_file(str(tmp_path), S3_BUCKET, f"raw/donki/{today}.json")

    total = sum(len(v) for v in all_events.values())
    print(f"[DONKI] {total} eventos → s3://{S3_BUCKET}/raw/donki/{today}.json")
    return {"records": total}


# ─── NOAA Kp realtime ──────────────────────────────────────────────────────────

def ingest_kp() -> dict:
    url = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
    resp = requests.get(url, timeout=25)
    resp.raise_for_status()
    records = resp.json()

    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "records": records,
    }

    today = date.today().isoformat()
    tmp_path = TMP / f"kp_{today}.json"
    tmp_path.write_text(json.dumps(payload), encoding="utf-8")
    s3.upload_file(str(tmp_path), S3_BUCKET, f"raw/kp/kp_realtime_{today}.json")

    print(f"[KP] {len(records)} leituras → s3://{S3_BUCKET}/raw/kp/kp_realtime_{today}.json")
    return {"records": len(records)}


# ─── SDO Images ────────────────────────────────────────────────────────────────

SDO_IMAGES = {
    "aia_0193": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_0193.jpg",
    "hmi_magnetogram": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_HMIB.jpg",
}


def ingest_images() -> dict:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    count = 0

    for name, url in SDO_IMAGES.items():
        try:
            resp = requests.get(url, timeout=25, stream=True)
            resp.raise_for_status()
            tmp_path = TMP / f"{name}_{timestamp}.jpg"
            with open(tmp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            s3.upload_file(str(tmp_path), S3_BUCKET, f"solar_images/{tmp_path.name}")
            count += 1
        except Exception as exc:
            print(f"[SDO] Erro em {name}: {exc}")

    print(f"[SDO] {count}/{len(SDO_IMAGES)} imagens → s3://{S3_BUCKET}/solar_images/")
    return {"files": count}


# ─── Handler ───────────────────────────────────────────────────────────────────

def lambda_handler(event: dict, context) -> dict:
    """Ponto de entrada da Lambda de ingestão."""
    print(f"[HeliOS] Iniciando ingestão — {datetime.now(timezone.utc).isoformat()}")

    results = {}
    errors = []

    for name, fn in [("donki", ingest_donki), ("kp", ingest_kp), ("images", ingest_images)]:
        try:
            results[name] = fn()
        except Exception as exc:
            tb = traceback.format_exc()
            print(f"[ERROR] {name}: {tb}")
            results[name] = {"error": str(exc)}
            errors.append(name)

    status_code = 200 if not errors else 207  # 207 Multi-Status se houver falhas parciais
    body = {
        "ingestion_time": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "errors": errors,
    }
    print(f"[HeliOS] Ingestão concluída — status {status_code}")

    return {"statusCode": status_code, "body": json.dumps(body)}
