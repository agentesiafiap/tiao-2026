-- HeliOS — Schema do banco de dados PostgreSQL
-- Fase 4 | Global Solution 2026.1 — FIAP
-- Aplicar com: python src/database/setup_db.py

-- ─── Histórico de índice Kp ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS kp_history (
    id            SERIAL PRIMARY KEY,
    observed_time TIMESTAMPTZ NOT NULL,
    kp_index      DECIMAL(4, 2),
    source        VARCHAR(20) DEFAULT 'NOAA_SWPC',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kp_history_time
    ON kp_history (observed_time DESC);

-- ─── Eventos solares (DONKI) ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS solar_events (
    id             SERIAL PRIMARY KEY,
    event_id       VARCHAR(100) UNIQUE,
    event_type     VARCHAR(50),           -- solar_flare, cme, geomagnetic_storm, sep
    start_time     TIMESTAMPTZ,
    peak_time      TIMESTAMPTZ,
    end_time       TIMESTAMPTZ,
    class_type     VARCHAR(20),           -- ex: X1.5, M3.2 (para flares)
    source_location VARCHAR(50),          -- ex: N15W30
    raw_data       JSONB,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_solar_events_type
    ON solar_events (event_type, start_time DESC);

CREATE INDEX IF NOT EXISTS idx_solar_events_start
    ON solar_events (start_time DESC);

-- ─── Previsões LSTM ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS kp_predictions (
    id             SERIAL PRIMARY KEY,
    predicted_at   TIMESTAMPTZ NOT NULL,  -- momento em que a previsão foi gerada
    target_time    TIMESTAMPTZ NOT NULL,  -- hora alvo da previsão
    kp_predicted   DECIMAL(4, 2),
    alert_level    VARCHAR(20),           -- QUIET, ACTIVE, STORM_G1_G2, STORM_G3_PLUS
    model_version  VARCHAR(20) DEFAULT 'lstm-v1',
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kp_predictions_target
    ON kp_predictions (target_time DESC);

-- ─── Leituras do sensor IoT (ESP32 magnetômetro) ─────────────────────────────
CREATE TABLE IF NOT EXISTS iot_readings (
    id           SERIAL PRIMARY KEY,
    device_id    VARCHAR(50),
    observed_at  TIMESTAMPTZ NOT NULL,
    bx_nt        DECIMAL(10, 3),          -- componente X do campo magnético (nT)
    by_nt        DECIMAL(10, 3),          -- componente Y
    bz_nt        DECIMAL(10, 3),          -- componente Z
    bt_nt        DECIMAL(10, 3),          -- magnitude total
    latitude     DECIMAL(9, 6),
    longitude    DECIMAL(9, 6),
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_iot_readings_time
    ON iot_readings (observed_at DESC);
