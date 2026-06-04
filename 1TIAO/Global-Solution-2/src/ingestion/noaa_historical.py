"""
noaa_historical.py — Download da série histórica de índice Kp (NOAA SWPC)
HeliOS | Global Solution 2026.1 — FIAP

Fonte: https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json
Contém manchas solares mensais e fluxo F10.7 desde ~1932.

Para Kp diário histórico (desde 1932), usamos o FTP da GFZ Potsdam via NOAA:
https://www.ngdc.noaa.gov/stp/GEOMAG/kp_ap.html
"""

import io
import os
from pathlib import Path

import boto3
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

SOLAR_CYCLE_URL = "https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json"
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "helios-solar-data")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def fetch_solar_cycle_indices() -> pd.DataFrame:
    """Baixa o histórico de ciclos solares (manchas + F10.7 + Kp médio mensal)."""
    resp = requests.get(SOLAR_CYCLE_URL, timeout=60)
    resp.raise_for_status()
    records = resp.json()
    df = pd.DataFrame(records)
    return df


def upload_to_s3(local_path: Path, s3_key: str) -> None:
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.upload_file(str(local_path), S3_BUCKET, s3_key)
    print(f"  [S3] Uploaded → s3://{S3_BUCKET}/{s3_key}")


def run() -> pd.DataFrame:
    print("\n[HISTÓRICO] Baixando série histórica de ciclos solares ...")

    df = fetch_solar_cycle_indices()
    print(f"  {len(df)} registros mensais recebidos")
    print(f"  Colunas: {list(df.columns)}")
    print(f"  Período: {df.iloc[0, 0]} → {df.iloc[-1, 0]}")

    local_path = PROCESSED_DIR / "solar_cycle_historical.csv"
    df.to_csv(local_path, index=False)
    print(f"[HISTÓRICO] Salvo em {local_path}")

    # Também salvar em Parquet para eficiência nas consultas do LSTM
    parquet_path = PROCESSED_DIR / "solar_cycle_historical.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"[HISTÓRICO] Parquet salvo em {parquet_path}")

    # Upload S3
    try:
        upload_to_s3(local_path, "processed/solar_cycle_historical.csv")
        upload_to_s3(parquet_path, "processed/solar_cycle_historical.parquet")
    except Exception as exc:
        print(f"[HISTÓRICO] Aviso — falha no upload S3: {exc}")

    return df


if __name__ == "__main__":
    run()
