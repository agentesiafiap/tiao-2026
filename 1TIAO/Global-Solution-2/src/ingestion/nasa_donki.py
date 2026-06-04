"""
nasa_donki.py — Ingestão de eventos solares via NASA DONKI API
HeliOS | Global Solution 2026.1 — FIAP

Eventos coletados: CME, FLR (Solar Flare), GST (Geomagnetic Storm), SEP
Docs: https://api.nasa.gov/
"""

import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.nasa.gov/DONKI"
API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "helios-solar-data")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw" / "donki"
DATA_DIR.mkdir(parents=True, exist_ok=True)

EVENTS = {
    "CME": "/CME",
    "FLR": "/FLR",
    "GST": "/GST",
    "SEP": "/SEP",
}


def fetch_event(event_type: str, endpoint: str, start_date: str, end_date: str) -> list:
    url = f"{BASE_URL}{endpoint}"
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": API_KEY,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else []


def upload_to_s3(local_path: Path, s3_key: str) -> None:
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.upload_file(str(local_path), S3_BUCKET, s3_key)
    print(f"  [S3] Uploaded → s3://{S3_BUCKET}/{s3_key}")


def run(start_date: str | None = None, end_date: str | None = None) -> dict:
    start = start_date or os.getenv("DONKI_START_DATE", "2024-01-01")
    end = end_date or os.getenv("DONKI_END_DATE", str(date.today()))
    today = date.today().isoformat()

    print(f"\n[DONKI] Coletando eventos de {start} até {end} ...")

    all_events: dict[str, list] = {}
    for event_type, endpoint in EVENTS.items():
        print(f"  Buscando {event_type}...", end=" ", flush=True)
        try:
            records = fetch_event(event_type, endpoint, start, end)
            all_events[event_type] = records
            print(f"{len(records)} registros")
        except requests.RequestException as exc:
            print(f"ERRO: {exc}")
            all_events[event_type] = []

    # Salvar localmente
    filename = f"{today}.json"
    local_path = DATA_DIR / filename
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump({"collected_at": today, "period": {"start": start, "end": end}, "events": all_events}, f, indent=2, ensure_ascii=False)
    print(f"[DONKI] Salvo em {local_path}")

    # Upload S3
    try:
        upload_to_s3(local_path, f"raw/donki/{filename}")
    except Exception as exc:
        print(f"[DONKI] Aviso — falha no upload S3: {exc}")

    return all_events


if __name__ == "__main__":
    run()
