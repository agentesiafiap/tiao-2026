# src/ingest_db.py
import sqlite3
import pandas as pd
import os

DB_PATH = "data/farmtech.db"
CSV_PATH = "data/simulated_sensor_data.csv"

def create_and_ingest(csv_path=CSV_PATH, db_path=DB_PATH):
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    df.to_sql("sensors", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Ingested {len(df)} rows into {db_path}")

if __name__ == "__main__":
    create_and_ingest()
