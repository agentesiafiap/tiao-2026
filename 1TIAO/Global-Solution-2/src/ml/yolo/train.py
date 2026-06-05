"""
train.py — Fine-tuning YOLOv8n para detecção de manchas solares
HeliOS | Global Solution 2026.1 — FIAP

═══════════════════════════════════════════════════════════════════
CONCEITO: O QUE É YOLO E POR QUE USAMOS AQUI?
═══════════════════════════════════════════════════════════════════

YOLO (You Only Look Once) é uma arquitetura de detecção de objetos
em tempo real. Diferente de abordagens de duas etapas (proposta de
região + classificação), o YOLO faz tudo em uma única passagem
pela rede — daí o nome.

Para o HeliOS, usamos YOLOv8n (nano — menor variante):
  - Detecta regiões ativas e manchas solares em imagens do SDO
  - Produz bounding boxes com classe e confiança
  - Inferência em <50ms por imagem (tempo real possível)

POR QUE FINE-TUNING E NÃO TREINO DO ZERO?
  O YOLOv8n pré-treinado no COCO já aprendeu features visuais
  genéricas (bordas, texturas, formas). Fine-tuning adapta esses
  pesos para o domínio solar em poucas épocas, sem precisar de
  milhares de imagens anotadas.

CLASSES DETECTADAS:
  0 — quiet_sun      : região solar quieta
  1 — active_region  : região ativa (AR) — potencial para flares
  2 — sunspot_group  : grupo de manchas solares visíveis

ATENÇÃO: Treinamento local pode ser lento. Use colab_yolo.ipynb
para treinar com GPU T4 no Google Colab (~10 min).

Uso:
    python src/ml/yolo/train.py
    python src/ml/yolo/train.py --epochs 50 --imgsz 416
"""

import argparse
from pathlib import Path
from ultralytics import YOLO

ROOT = Path(__file__).parent.parent.parent.parent
DATASET_YAML = Path(__file__).parent / "dataset.yaml"
MODEL_DIR = Path(__file__).parent / "model"
MODEL_DIR.mkdir(exist_ok=True)

EPOCHS   = 30
IMGSZ    = 640
BATCH    = 16
BASE_MODEL = "yolo11n.pt"   # nano — menor e mais rápido para POC


def run(epochs: int = EPOCHS, imgsz: int = IMGSZ, batch: int = BATCH):
    print("=" * 60)
    print("  HeliOS YOLO — Fine-tuning")
    print(f"  Modelo base: {BASE_MODEL} | Épocas: {epochs} | Imgsz: {imgsz}")
    print("=" * 60)

    print("\n[1/3] Carregando modelo pré-treinado YOLOv8n (COCO)...")
    model = YOLO(BASE_MODEL)

    print(f"\n[2/3] Iniciando fine-tuning...")
    print(f"  Dataset config : {DATASET_YAML}")
    results = model.train(
        data=str(DATASET_YAML),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=str(MODEL_DIR),
        name="helios_yolo",
        exist_ok=True,
        verbose=True,
    )

    print(f"\n[3/3] Salvando modelo final...")
    best_weights = MODEL_DIR / "helios_yolo" / "weights" / "best.pt"
    if best_weights.exists():
        import shutil
        shutil.copy(best_weights, MODEL_DIR / "helios_yolo.pt")
        print(f"  Modelo salvo em: {MODEL_DIR / 'helios_yolo.pt'}")

    metrics = results.results_dict if hasattr(results, "results_dict") else {}
    map50 = metrics.get("metrics/mAP50(B)", None)
    if map50 is not None:
        print(f"\n  mAP50: {map50:.4f}")
        print(f"  (Referência: mAP50 > 0.5 é considerado bom para este POC)")

    print("\n" + "=" * 60)
    print("  Fine-tuning concluído!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HeliOS YOLO — Fine-tuning")
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--imgsz",  type=int, default=IMGSZ)
    parser.add_argument("--batch",  type=int, default=BATCH)
    args = parser.parse_args()
    run(epochs=args.epochs, imgsz=args.imgsz, batch=args.batch)
