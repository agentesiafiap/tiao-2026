"""
noaa_kp.py — Ingestão do índice Kp em tempo real (NOAA SWPC)
HeliOS | Global Solution 2026.1 — FIAP

Fonte: https://services.swpc.noaa.gov/json/planetary_k_index_1m.json
Atualizado pela NOAA a cada minuto.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

KP_REALTIME_URL = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "helios-solar-data")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw" / "kp"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_kp() -> list:
    resp = requests.get(KP_REALTIME_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()


def upload_to_s3(local_path: Path, s3_key: str) -> None:
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.upload_file(str(local_path), S3_BUCKET, s3_key)
    print(f"  [S3] Uploaded → s3://{S3_BUCKET}/{s3_key}")


def run() -> list:
    print("\n[KP] Coletando índice Kp em tempo real ...")

    records = fetch_kp()
    print(f"  {len(records)} leituras recebidas")

    if records:
        latest = records[-1]
        print(f"  Última leitura: {latest.get('time_tag', 'N/A')} | Kp = {latest.get('kp_index', 'N/A')}")

    collected_at = datetime.now(timezone.utc).isoformat()
    payload = {"collected_at": collected_at, "records": records}

    local_path = DATA_DIR / "kp_realtime.json"
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[KP] Salvo em {local_path}")

    # Upload S3 com timestamp no nome para não sobrescrever histórico
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    s3_key = f"raw/kp/kp_realtime_{date_str}.json"
    try:
        upload_to_s3(local_path, s3_key)
    except Exception as exc:
        print(f"[KP] Aviso — falha no upload S3: {exc}")

    return records


if __name__ == "__main__":
    run()
