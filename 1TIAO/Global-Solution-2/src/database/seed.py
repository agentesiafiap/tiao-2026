"""
seed.py — Carrega dados históricos no RDS PostgreSQL do HeliOS
HeliOS | Global Solution 2026.1 — FIAP

Fontes carregadas:
  1. data/processed/solar_cycle_historical.csv → kp_history (proxy via SSN/F10.7)
  2. data/raw/donki/<mais recente>.json         → solar_events

Uso:
    python src/database/seed.py
    python src/database/seed.py --only kp        # só kp_history
    python src/database/seed.py --only events    # só solar_events
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_DONKI_DIR = ROOT / "data" / "raw" / "donki"


def get_connection():
    return psycopg2.connect(
        host=os.environ["RDS_HOST"],
        port=int(os.environ.get("RDS_PORT", "5432")),
        dbname=os.environ.get("RDS_DB_NAME", "helios"),
        user=os.environ["RDS_USER"],
        password=os.environ["RDS_PASSWORD"],
        connect_timeout=10,
        sslmode="require",
    )


# ─── kp_history ───────────────────────────────────────────────────────────────

def seed_kp_history(conn) -> int:
    """
    Carrega o histórico de ciclos solares como proxy de atividade.
    A tabela kp_history aceita também F10.7 (correlacionado ao Kp).
    Registros com ssn (sunspot number) > 0 são inseridos com kp_index derivado.
    Fórmula aproximada: Kp ≈ ssn / 50 (simplificada para seed histórico).
    """
    csv_path = PROCESSED_DIR / "solar_cycle_historical.csv"
    if not csv_path.exists():
        print("[seed] AVISO: solar_cycle_historical.csv não encontrado. Pule e execute run_all.py primeiro.")
        return 0

    df = pd.read_csv(csv_path)
    # Coluna de data está em formato YYYY-MM
    df["observed_time"] = pd.to_datetime(df["time-tag"], format="%Y-%m", utc=True)
    df["kp_index"] = (df["ssn"].fillna(0) / 50).clip(0, 9).round(2)
    df = df[df["kp_index"] > 0]

    records = [
        (row["observed_time"], float(row["kp_index"]), "NOAA_HISTORICAL")
        for _, row in df.iterrows()
    ]

    with conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO kp_history (observed_time, kp_index, source)
            VALUES %s
            ON CONFLICT DO NOTHING
            """,
            records,
            page_size=500,
        )
    conn.commit()
    print(f"[seed] kp_history: {len(records)} registros inseridos")
    return len(records)


# ─── solar_events ─────────────────────────────────────────────────────────────

def seed_solar_events(conn) -> int:
    """Carrega eventos DONKI do arquivo JSON mais recente em data/raw/donki/."""
    json_files = sorted(RAW_DONKI_DIR.glob("*.json"))
    if not json_files:
        print("[seed] AVISO: Nenhum arquivo DONKI encontrado em data/raw/donki/")
        return 0

    latest = json_files[-1]
    print(f"[seed] Usando {latest.name} ...")
    raw = json.loads(latest.read_text(encoding="utf-8"))
    events_by_type = raw.get("events", {})

    type_map = {
        "FLR": "solar_flare",
        "CME": "cme",
        "GST": "geomagnetic_storm",
        "SEP": "sep",
    }

    records = []
    for event_type, items in events_by_type.items():
        mapped = type_map.get(event_type, event_type.lower())
        for item in (items or []):
            event_id = (
                item.get("flrID")
                or item.get("activityID")
                or item.get("gstID")
                or item.get("sepID")
                or ""
            )
            if not event_id:
                continue

            def parse_dt(val):
                if not val:
                    return None
                try:
                    return datetime.fromisoformat(val.replace("Z", "+00:00"))
                except Exception:
                    return None

            records.append((
                event_id,
                mapped,
                parse_dt(item.get("beginTime") or item.get("startTime")),
                parse_dt(item.get("peakTime")),
                parse_dt(item.get("endTime")),
                item.get("classType", ""),
                item.get("sourceLocation", ""),
                json.dumps(item),
            ))

    with conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO solar_events
              (event_id, event_type, start_time, peak_time, end_time,
               class_type, source_location, raw_data)
            VALUES %s
            ON CONFLICT (event_id) DO NOTHING
            """,
            records,
            template="(%s, %s, %s, %s, %s, %s, %s, %s::jsonb)",
            page_size=200,
        )
    conn.commit()
    print(f"[seed] solar_events: {len(records)} registros inseridos")
    return len(records)


# ─── Main ─────────────────────────────────────────────────────────────────────

def run(only: str | None = None) -> None:
    print("[seed] Conectando ao RDS PostgreSQL ...")
    try:
        conn = get_connection()
    except psycopg2.OperationalError as exc:
        print(f"[ERRO] Não foi possível conectar: {exc}")
        sys.exit(1)

    total = 0
    if only in (None, "kp"):
        total += seed_kp_history(conn)
    if only in (None, "events"):
        total += seed_solar_events(conn)

    conn.close()
    print(f"[seed] Concluído. Total: {total} registros inseridos.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["kp", "events"], help="Executar apenas uma das seeds")
    args = parser.parse_args()
    run(only=args.only)
