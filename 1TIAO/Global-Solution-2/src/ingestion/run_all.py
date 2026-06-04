"""
run_all.py — Executa toda a pipeline de ingestão de dados do HeliOS
HeliOS | Global Solution 2026.1 — FIAP

Uso:
    python src/ingestion/run_all.py
    python src/ingestion/run_all.py --skip-images   # pula download de imagens
"""

import argparse
import sys
import time
from datetime import datetime, timezone

# Adiciona o diretório raiz ao path para imports relativos
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import nasa_donki
import noaa_kp
import noaa_historical
import solar_images


def print_header(title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def run(skip_images: bool = False) -> None:
    start_time = time.time()
    started_at = datetime.now(timezone.utc).isoformat()

    print_header(f"HeliOS — Pipeline de Ingestão")
    print(f"Iniciado em: {started_at}")

    results = {}

    # 1. Eventos solares NASA DONKI
    print_header("1/4 — NASA DONKI (eventos solares)")
    try:
        events = nasa_donki.run()
        total = sum(len(v) for v in events.values())
        results["donki"] = {"status": "ok", "records": total}
    except Exception as exc:
        print(f"ERRO em nasa_donki: {exc}")
        results["donki"] = {"status": "error", "error": str(exc)}

    # 2. Índice Kp em tempo real (NOAA)
    print_header("2/4 — NOAA Kp (tempo real)")
    try:
        kp_records = noaa_kp.run()
        results["kp_realtime"] = {"status": "ok", "records": len(kp_records)}
    except Exception as exc:
        print(f"ERRO em noaa_kp: {exc}")
        results["kp_realtime"] = {"status": "error", "error": str(exc)}

    # 3. Série histórica solar (NOAA)
    print_header("3/4 — NOAA Histórico (ciclos solares)")
    try:
        df = noaa_historical.run()
        results["historical"] = {"status": "ok", "records": len(df)}
    except Exception as exc:
        print(f"ERRO em noaa_historical: {exc}")
        results["historical"] = {"status": "error", "error": str(exc)}

    # 4. Imagens SDO
    if not skip_images:
        print_header("4/4 — Imagens SDO (Solar Dynamics Observatory)")
        try:
            images = solar_images.run()
            results["solar_images"] = {"status": "ok", "files": len(images)}
        except Exception as exc:
            print(f"ERRO em solar_images: {exc}")
            results["solar_images"] = {"status": "error", "error": str(exc)}
    else:
        print_header("4/4 — Imagens SDO [PULADO]")
        results["solar_images"] = {"status": "skipped"}

    # Resumo final
    elapsed = time.time() - start_time
    print_header("Resumo da Ingestão")
    all_ok = True
    for source, info in results.items():
        status = info["status"]
        if status == "ok":
            detail = info.get("records", info.get("files", ""))
            print(f"  ✓ {source:<20} {detail} registros/arquivos")
        elif status == "skipped":
            print(f"  - {source:<20} pulado")
        else:
            all_ok = False
            print(f"  ✗ {source:<20} ERRO: {info.get('error', '')}")

    print(f"\nTempo total: {elapsed:.1f}s")
    if not all_ok:
        print("AVISO: Um ou mais módulos falharam. Verifique os logs acima.")
        sys.exit(1)
    else:
        print("Ingestão concluída com sucesso!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HeliOS — Pipeline de ingestão")
    parser.add_argument("--skip-images", action="store_true", help="Pula o download de imagens SDO")
    args = parser.parse_args()
    run(skip_images=args.skip_images)
