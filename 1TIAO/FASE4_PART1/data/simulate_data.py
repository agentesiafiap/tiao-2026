# src/simulate_data.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

def generate_sensor_data(n_days=180, sensors=5, seed=42, out_path="data/simulated_sensor_data.csv"):
    np.random.seed(seed)
    rows = []
    start = datetime.now() - timedelta(days=n_days)
    for s in range(sensors):
        sensor_id = f"sensor_{s+1}"
        for day in range(n_days):
            ts = start + timedelta(days=day)
            soil_moisture = np.clip(20 + 40*np.sin(day/30 + s) + np.random.normal(0,5), 5, 60) # %
            soil_ph = np.clip(5.5 + 0.5*np.cos(day/50 + s/2) + np.random.normal(0,0.15), 4.5, 7.5)
            air_temp = np.clip(18 + 8*np.sin(day/20) + np.random.normal(0,2), 5, 40)
            humidity = np.clip(40 + 30*np.cos(day/25) + np.random.normal(0,5), 10, 100)
            irrigation_ml = max(0, np.random.normal(200 if soil_moisture<30 else 50, 40))
            fertilizer_kg = max(0, np.random.normal(2 if day%30==0 else 0.2, 0.3))
            # yield as a function of moisture, pH, irrigation, fertilizer + noise
            yield_ton = (0.05*soil_moisture) + (0.8 * (1 - abs(6.5 - soil_ph))) + 0.001*irrigation_ml + 0.2*fertilizer_kg
            yield_ton = yield_ton/10 + np.random.normal(0,0.05)  # scale and noise
            rows.append({
                "sensor_id": sensor_id,
                "timestamp": ts,
                "soil_moisture": round(soil_moisture,2),
                "soil_ph": round(soil_ph,2),
                "air_temp": round(air_temp,2),
                "humidity": round(humidity,2),
                "irrigation_ml": round(irrigation_ml,2),
                "fertilizer_kg": round(fertilizer_kg,3),
                "yield_ton_per_ha": round(yield_ton,4)
            })
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Simulated data saved to {out_path} ({len(df)} rows)")
    return df

if __name__ == "__main__":
    generate_sensor_data()
