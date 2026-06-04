"""
solar_images.py — Download de imagens do SDO (Solar Dynamics Observatory / NASA)
HeliOS | Global Solution 2026.1 — FIAP

Fonte: https://sdo.gsfc.nasa.gov/assets/img/latest/
Imagens AIA (Atmospheric Imaging Assembly) em múltiplos comprimentos de onda.
Usadas no treinamento e inferência do modelo YOLO de manchas solares (Fase 6).
"""

import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET_NAME", "helios-solar-data")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

IMAGES_DIR = Path(__file__).parent.parent.parent / "data" / "solar_images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Imagens SDO disponíveis publicamente sem autenticação
# Comprimentos de onda AIA + magnetograma HMI
SDO_IMAGES = {
    "aia_0193": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_0193.jpg",
    "aia_0171": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_0171.jpg",
    "aia_0304": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_0304.jpg",
    "aia_0131": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_0131.jpg",
    "hmi_magnetogram": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_HMIB.jpg",
    "hmi_intensitygram": "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_HMIIC.jpg",
}


def download_image(name: str, url: str, timestamp: str) -> Path | None:
    try:
        resp = requests.get(url, timeout=30, stream=True)
        resp.raise_for_status()
        filename = f"{name}_{timestamp}.jpg"
        local_path = IMAGES_DIR / filename
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        size_kb = local_path.stat().st_size // 1024
        print(f"  [{name}] {size_kb} KB → {local_path.name}")
        return local_path
    except requests.RequestException as exc:
        print(f"  [{name}] ERRO: {exc}")
        return None


def upload_to_s3(local_path: Path, s3_key: str) -> None:
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.upload_file(str(local_path), S3_BUCKET, s3_key)
    print(f"    [S3] Uploaded → s3://{S3_BUCKET}/{s3_key}")


def run() -> list[Path]:
    print("\n[SDO] Baixando imagens solares do SDO/NASA ...")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    downloaded: list[Path] = []

    for name, url in SDO_IMAGES.items():
        path = download_image(name, url, timestamp)
        if path:
            downloaded.append(path)
            try:
                upload_to_s3(path, f"solar_images/{path.name}")
            except Exception as exc:
                print(f"    [S3] Aviso — falha no upload: {exc}")

    print(f"[SDO] {len(downloaded)}/{len(SDO_IMAGES)} imagens baixadas com sucesso")
    return downloaded


if __name__ == "__main__":
    run()
