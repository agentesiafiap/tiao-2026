"""
Configuration file for Aurora Totem MVP
Centralized settings and environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Oracle FIAP Database Configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "oracle.fiap.com.br"),
    "port": int(os.getenv("DB_PORT", "1521")),
    "sid": os.getenv("DB_SID", "ORCL"),
    "username": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD") 
}

# Connection string for Oracle
CONNECTION_STRING = f"oracle://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['sid']}"

# API Configuration
API_CONFIG = {
    "host": os.getenv("API_HOST", "localhost"),
    "port": int(os.getenv("API_PORT", "8000")),
    "debug": os.getenv("API_DEBUG", "True").lower() == "true"
}

# Sensor Simulator Configuration
SENSOR_CONFIG = {
    "device_id": os.getenv("DEVICE_ID", "totem_aurora_001"),
    "simulation_interval_min": float(os.getenv("SIM_INTERVAL_MIN", "1.0")),
    "simulation_interval_max": float(os.getenv("SIM_INTERVAL_MAX", "5.0")),
    "api_endpoint": f"http://{API_CONFIG['host']}:{API_CONFIG['port']}/api/sensor"
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "auto_refresh_seconds": int(os.getenv("DASHBOARD_REFRESH", "30")),
    "default_hours_range": int(os.getenv("DASHBOARD_HOURS", "1")),
    "max_records_display": int(os.getenv("MAX_RECORDS", "100"))
}

# ML Model Configuration
ML_CONFIG = {
    "model_path": os.getenv("MODEL_PATH", "interaction_model.pkl"),
    "synthetic_data_size": int(os.getenv("SYNTHETIC_DATA_SIZE", "1000")),
    "test_size": float(os.getenv("TEST_SIZE", "0.2")),
    "random_state": int(os.getenv("RANDOM_STATE", "42"))
}

# Sensor Value Ranges (for simulation)
SENSOR_RANGES = {
    "touch": {
        "quick_browse": (0.5, 2.0),
        "engaged_reading": (2.0, 8.0), 
        "deep_interaction": (8.0, 15.0)
    },
    "proximity": {
        "far": (100, 200),
        "medium": (50, 100),
        "close": (10, 50)
    },
    "emotion": {
        "negative": (0.0, 0.3),
        "neutral": (0.3, 0.7),
        "positive": (0.7, 1.0)
    }
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "refresh_interval": int(os.getenv("DASHBOARD_REFRESH", "30")),
    "data_hours": int(os.getenv("DASHBOARD_HOURS", "1")),
    "max_records": int(os.getenv("MAX_RECORDS", "100")),
    "auto_refresh": os.getenv("AUTO_REFRESH", "True").lower() == "true"
}

# Machine Learning Configuration
ML_CONFIG = {
    "model_dir": os.getenv("MODEL_DIR", "models"),
    "model_prefix": os.getenv("MODEL_PREFIX", "aurora_totem_model"),
    "synthetic_data_size": int(os.getenv("SYNTHETIC_DATA_SIZE", "1000")),
    "test_size": float(os.getenv("TEST_SIZE", "0.2")),
    "random_state": int(os.getenv("RANDOM_STATE", "42")),
    "cv_folds": int(os.getenv("CV_FOLDS", "5")),
    "n_clusters": int(os.getenv("N_CLUSTERS", "4")),
    "retrain_interval_hours": int(os.getenv("RETRAIN_INTERVAL", "24"))
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("LOG_FILE", "aurora_totem.log")
}

# Development/Production Settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

print(f"🔧 Aurora Totem Configuration Loaded")
print(f"   Environment: {ENVIRONMENT}")
print(f"   Database: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}")
print(f"   API: {API_CONFIG['host']}:{API_CONFIG['port']}")
print(f"   Device ID: {SENSOR_CONFIG['device_id']}")