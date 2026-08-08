-- Schema simples para SQLite / Postgres
CREATE TABLE IF NOT EXISTS sensors (
    id SERIAL PRIMARY KEY,
    sensor_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    soil_moisture REAL,    -- umidade (%)
    soil_ph REAL,          -- pH
    air_temp REAL,         -- temperatura ambiente (°C)
    humidity REAL,         -- umidade relativa (%)
    irrigation_ml REAL,    -- volume de irrigação aplicado (mL)
    fertilizer_kg REAL,    -- fertilizante aplicado (kg/ha)
    yield_ton_per_ha REAL  -- rendimento observado (ton/ha) - target
);
