"""
setup_db.py — Aplica o schema SQL no RDS PostgreSQL do HeliOS
HeliOS | Global Solution 2026.1 — FIAP

Uso:
    python src/database/setup_db.py

Pré-requisito: instância helios-db em status 'available'.
Credenciais lidas de .env (RDS_HOST, RDS_USER, RDS_PASSWORD, RDS_DB_NAME).
"""

import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


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


def apply_schema() -> None:
    print("[setup_db] Conectando ao RDS PostgreSQL ...")
    sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as conn:
        with conn.cursor() as cur:
            print("[setup_db] Aplicando schema.sql ...")
            cur.execute(sql)
        conn.commit()

    print("[setup_db] Schema aplicado com sucesso.")
    print("  Tabelas criadas/verificadas:")
    print("    - kp_history")
    print("    - solar_events")
    print("    - kp_predictions")
    print("    - iot_readings")


if __name__ == "__main__":
    try:
        apply_schema()
    except psycopg2.OperationalError as exc:
        print(f"[ERRO] Não foi possível conectar ao RDS: {exc}")
        print("Verifique RDS_HOST no .env e se a instância está em status 'available'.")
        sys.exit(1)
