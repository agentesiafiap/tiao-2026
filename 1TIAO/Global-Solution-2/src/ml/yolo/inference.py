"""
inference.py — Detecção de manchas solares em imagem SDO com YOLOv8
HeliOS | Global Solution 2026.1 — FIAP

Recebe uma imagem solar (local ou URL) e retorna JSON com:
  - Lista de detecções: {class, confidence, bbox}
  - risk_score: pontuação de risco geomagnético baseado nas detecções
  - risk_level: QUIET / WATCH / WARNING / ALERT

Uso:
    python src/ml/yolo/inference.py --image data/solar_images/aia_0193_latest.jpg
    python src/ml/yolo/inference.py --image data/solar_images/aia_0193_latest.jpg --output json
    python src/ml/yolo/inference.py --latest   # baixa imagem SDO mais recente
"""

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MODEL_PATH   = Path(__file__).parent / "model" / "helios_yolo.pt"
ANNOTATED_DIR = Path(__file__).parent.parent.parent.parent / "data" / "solar_images" / "annotated"
ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

# SDO/AIA 0193 — canal mais sensível a regiões ativas
SDO_LATEST_URL = (
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"
)

# Pesos de risco por classe
RISK_WEIGHTS = {
    "quiet_sun":      0.0,
    "active_region":  0.5,
    "sunspot_group":  1.0,
}


def download_latest_sdo(dest: Path) -> Path:
    """Baixa a imagem SDO/AIA mais recente (1024px)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Baixando imagem SDO mais recente...")
    urllib.request.urlretrieve(SDO_LATEST_URL, dest)
    print(f"  Salvo em: {dest}")
    return dest


def compute_risk(detections: list[dict]) -> tuple[float, str]:
    """
    Calcula risk_score [0, 1] baseado no número e tipo de detecções.

    Lógica:
      - Cada detecção contribui: weight_classe × confidence
      - Score normalizado pelo máximo teórico (5 manchas com conf=1.0)
      - Thresholds: QUIET<0.2, WATCH<0.5, WARNING<0.75, ALERT≥0.75
    """
    if not detections:
        return 0.0, "QUIET"

    raw = sum(
        RISK_WEIGHTS.get(d["class"], 0.0) * d["confidence"]
        for d in detections
    )
    score = min(raw / 5.0, 1.0)  # normaliza para [0, 1]

    if score < 0.2:   level = "QUIET"
    elif score < 0.5: level = "WATCH"
    elif score < 0.75: level = "WARNING"
    else:             level = "ALERT"

    return round(score, 4), level


def run_inference(image_path: str, save_annotated: bool = True) -> dict:
    from ultralytics import YOLO

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado: {MODEL_PATH}\n"
            f"Execute o treinamento via src/ml/yolo/colab_yolo.ipynb e coloque "
            f"helios_yolo.pt em src/ml/yolo/model/"
        )

    model = YOLO(str(MODEL_PATH))
    results = model.predict(image_path, conf=0.25, verbose=False)
    result = results[0]

    detections = []
    for box in result.boxes:
        cls_id  = int(box.cls[0])
        cls_name = model.names[cls_id]
        conf    = float(box.conf[0])
        xyxy    = [round(float(v), 1) for v in box.xyxy[0].tolist()]
        detections.append({
            "class":      cls_name,
            "class_id":   cls_id,
            "confidence": round(conf, 4),
            "bbox_xyxy":  xyxy,
        })

    risk_score, risk_level = compute_risk(detections)

    # Salvar imagem anotada
    annotated_path = None
    if save_annotated and len(detections) > 0:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        annotated_path = str(ANNOTATED_DIR / f"solar_annotated_{ts}.jpg")
        result.save(annotated_path)

    return {
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "image":          str(image_path),
        "detections":     detections,
        "total_detected": len(detections),
        "risk_score":     risk_score,
        "risk_level":     risk_level,
        "annotated_image": annotated_path,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HeliOS YOLO — Inferência Solar")
    parser.add_argument("--image",   type=str, help="Caminho ou URL da imagem solar")
    parser.add_argument("--latest",  action="store_true", help="Baixa imagem SDO mais recente")
    parser.add_argument("--output",  choices=["json", "pretty"], default="pretty")
    args = parser.parse_args()

    if args.latest or not args.image:
        img_path = ANNOTATED_DIR.parent / "sdo_latest_0193.jpg"
        download_latest_sdo(img_path)
        image = str(img_path)
    else:
        image = args.image

    print(f"\n  Executando inferência em: {image}")
    output = run_inference(image)

    if args.output == "json":
        print(json.dumps(output))
    else:
        print(f"\n{'='*50}")
        print(f"  Detecções: {output['total_detected']}")
        for d in output["detections"]:
            print(f"    [{d['class_id']}] {d['class']:<16} conf={d['confidence']:.2f}  bbox={d['bbox_xyxy']}")
        print(f"\n  Risk Score : {output['risk_score']}")
        print(f"  Risk Level : {output['risk_level']}")
        if output["annotated_image"]:
            print(f"  Anotada em : {output['annotated_image']}")
        print(f"{'='*50}")
