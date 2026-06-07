#!/usr/bin/env python3
"""
Aurora Totem - IoT Sensor Data Simulator
Simulates realistic sensor data for the empathetic AI totem system
"""

import time
import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging
from dataclasses import dataclass

from .config import SENSOR_CONFIG, DATABASE_CONFIG
from .database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SensorReading:
    """Data structure for sensor readings"""
    device_id: str
    sensor_type: str
    value: float
    metadata: Dict
    timestamp: datetime = None

class SensorSimulator:
    """
    Realistic IoT sensor data simulator for Aurora Totem
    Generates environmental and biometric data with natural patterns
    """
    
    def __init__(self):
        self.device_id = SENSOR_CONFIG['device_id']
        self.db = DatabaseManager()
        
        # Simulation state
        self.running = False
        self.start_time = datetime.now()
        
        # Environmental base values (São Paulo averages)
        self.base_temperature = 25.0  # °C
        self.base_humidity = 65.0     # %
        self.base_light = 400         # lux
        self.base_sound = 45.0        # dB
        
        # Emotion simulation state
        self.crowd_emotions = ['neutral', 'happy', 'curious', 'engaged', 'surprised']
        self.current_crowd_mood = 'neutral'
        self.mood_change_probability = 0.15
        
        logger.info(f"🎯 Sensor Simulator iniciado para dispositivo: {self.device_id}")
    
    def get_time_factors(self) -> Dict[str, float]:
        """
        Calculate time-based factors for realistic daily/seasonal patterns
        """
        now = datetime.now()
        
        # Time of day factor (0-1, peak at noon)
        hour_angle = (now.hour - 6) * math.pi / 12  # 6am = 0, 6pm = π
        day_factor = max(0, math.sin(hour_angle))
        
        # Day of year factor for seasonal variation
        day_of_year = now.timetuple().tm_yday
        seasonal_factor = 0.5 + 0.3 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        
        # Weekend factor (slightly different patterns)
        weekend_factor = 1.2 if now.weekday() >= 5 else 1.0
        
        return {
            'day_factor': day_factor,
            'seasonal_factor': seasonal_factor,
            'weekend_factor': weekend_factor,
            'is_business_hours': 8 <= now.hour <= 18,
            'is_peak_hours': 11 <= now.hour <= 14 or 17 <= now.hour <= 19
        }
    
    def simulate_temperature(self) -> SensorReading:
        """
        Simulate temperature sensor (20-35°C range)
        Includes daily cycle, seasonal variation, and HVAC effects
        """
        time_factors = self.get_time_factors()
        
        # Base temperature with seasonal and daily variation
        seasonal_adj = (time_factors['seasonal_factor'] - 0.5) * 10  # ±5°C seasonal
        daily_adj = time_factors['day_factor'] * 5  # +5°C peak day heat
        
        # HVAC effects during business hours
        hvac_adj = -2 if time_factors['is_business_hours'] else 0
        
        # Random variation ±1.5°C
        noise = random.uniform(-1.5, 1.5)
        
        temperature = self.base_temperature + seasonal_adj + daily_adj + hvac_adj + noise
        temperature = max(20.0, min(35.0, temperature))  # Clamp to range
        
        metadata = {
            'unit': 'celsius',
            'location': 'totem_ambient',
            'seasonal_factor': round(time_factors['seasonal_factor'], 3),
            'hvac_active': time_factors['is_business_hours'],
            'comfort_zone': 20 <= temperature <= 26
        }
        
        return SensorReading(
            device_id=self.device_id,
            sensor_type='temperature',
            value=round(temperature, 1),
            metadata=metadata
        )
    
    def simulate_humidity(self) -> SensorReading:
        """
        Simulate humidity sensor (40-80% range)
        Inversely correlated with temperature, includes weather simulation
        """
        time_factors = self.get_time_factors()
        
        # Base humidity with inverse temperature correlation
        temp_effect = -0.8 * (self.base_temperature - 25)  # Higher temp = lower humidity
        
        # Weather pattern simulation
        weather_variation = random.uniform(-10, 15) if random.random() < 0.3 else 0
        
        # HVAC dehumidification effect
        hvac_effect = -5 if time_factors['is_business_hours'] else 0
        
        # Daily cycle (higher at night)
        daily_effect = -5 * time_factors['day_factor']
        
        humidity = self.base_humidity + temp_effect + weather_variation + hvac_effect + daily_effect
        humidity = max(40.0, min(80.0, humidity))
        
        # Determine comfort and air quality
        is_comfortable = 45 <= humidity <= 65
        air_quality = 'good' if is_comfortable else ('dry' if humidity < 45 else 'humid')
        
        metadata = {
            'unit': 'percent',
            'location': 'totem_ambient',
            'air_quality': air_quality,
            'comfortable': is_comfortable,
            'weather_event': weather_variation > 10
        }
        
        return SensorReading(
            device_id=self.device_id,
            sensor_type='humidity',
            value=round(humidity, 1),
            metadata=metadata
        )
    
    def simulate_light(self) -> SensorReading:
        """
        Simulate light sensor (100-1000 lux range)
        Includes natural light cycle, artificial lighting, and cloud effects
        """
        time_factors = self.get_time_factors()
        
        # Natural light cycle (much stronger effect)
        natural_light = time_factors['day_factor'] * 600  # 0-600 lux from sun
        
        # Artificial lighting (always present indoors)
        artificial_light = 200 if time_factors['is_business_hours'] else 100
        
        # Cloud/weather effects
        cloud_factor = random.uniform(0.6, 1.0) if time_factors['day_factor'] > 0.3 else 1.0
        
        # Random variations
        noise = random.uniform(-30, 30)
        
        total_light = (natural_light * cloud_factor) + artificial_light + noise
        total_light = max(100, min(1000, total_light))
        
        # Classify lighting conditions
        if total_light < 200:
            lighting_quality = 'dim'
        elif total_light < 500:
            lighting_quality = 'moderate'
        else:
            lighting_quality = 'bright'
        
        metadata = {
            'unit': 'lux',
            'location': 'totem_display_area',
            'natural_component': round(natural_light * cloud_factor),
            'artificial_component': artificial_light,
            'lighting_quality': lighting_quality,
            'optimal_for_display': 300 <= total_light <= 800
        }
        
        return SensorReading(
            device_id=self.device_id,
            sensor_type='light',
            value=round(total_light),
            metadata=metadata
        )
    
    def simulate_sound(self) -> SensorReading:
        """
        Simulate sound/noise sensor (30-80 dB range)
        Includes crowd dynamics, peak hours, and ambient noise
        """
        time_factors = self.get_time_factors()
        
        # Base ambient noise
        base_noise = 35  # Quiet indoor baseline
        
        # Crowd effect during business/peak hours
        if time_factors['is_peak_hours']:
            crowd_noise = random.uniform(15, 25)  # Busy periods
        elif time_factors['is_business_hours']:
            crowd_noise = random.uniform(5, 15)   # Normal activity
        else:
            crowd_noise = random.uniform(0, 5)    # Quiet periods
        
        # Weekend factor (slightly busier)
        weekend_bonus = 5 * time_factors['weekend_factor'] if time_factors['weekend_factor'] > 1 else 0
        
        # Random events (conversations, announcements, etc.)
        event_noise = 0
        if random.random() < 0.2:  # 20% chance of noise event
            event_noise = random.uniform(10, 20)
        
        total_sound = base_noise + crowd_noise + weekend_bonus + event_noise
        total_sound = max(30, min(80, total_sound))
        
        # Classify noise level
        if total_sound < 40:
            noise_level = 'quiet'
        elif total_sound < 55:
            noise_level = 'moderate'
        elif total_sound < 70:
            noise_level = 'noisy'
        else:
            noise_level = 'loud'
        
        metadata = {
            'unit': 'decibels',
            'location': 'totem_microphone',
            'crowd_activity': round(crowd_noise),
            'noise_level': noise_level,
            'event_detected': event_noise > 0,
            'comfortable_level': total_sound < 60
        }
        
        return SensorReading(
            device_id=self.device_id,
            sensor_type='sound',
            value=round(total_sound, 1),
            metadata=metadata
        )
    
    def simulate_camera_emotion(self) -> SensorReading:
        """
        Simulate camera-based emotion detection
        Includes crowd mood dynamics and confidence scoring
        """
        time_factors = self.get_time_factors()
        
        # Update crowd mood with some probability
        if random.random() < self.mood_change_probability:
            self.current_crowd_mood = random.choice(self.crowd_emotions)
        
        # Emotion probabilities based on current mood and time factors
        emotion_weights = {
            'neutral': 0.4,
            'happy': 0.25,
            'curious': 0.15,
            'engaged': 0.1,
            'surprised': 0.05,
            'confused': 0.03,
            'frustrated': 0.02
        }
        
        # Adjust probabilities based on crowd mood
        if self.current_crowd_mood in emotion_weights:
            emotion_weights[self.current_crowd_mood] += 0.3
            # Normalize
            total = sum(emotion_weights.values())
            emotion_weights = {k: v/total for k, v in emotion_weights.items()}
        
        # Peak hours = more engagement/curiosity
        if time_factors['is_peak_hours']:
            emotion_weights['engaged'] *= 1.5
            emotion_weights['curious'] *= 1.3
            emotion_weights['neutral'] *= 0.8
        
        # Select emotion based on weights
        emotions = list(emotion_weights.keys())
        weights = list(emotion_weights.values())
        detected_emotion = random.choices(emotions, weights=weights)[0]
        
        # Confidence score (higher for common emotions)
        base_confidence = emotion_weights[detected_emotion]
        confidence = min(0.95, max(0.6, base_confidence + random.uniform(-0.1, 0.2)))
        
        # Face detection simulation
        face_detected = random.random() < 0.85  # 85% face detection rate
        
        # Age/gender estimation (optional)
        estimated_age = random.randint(18, 65) if face_detected else None
        estimated_gender = random.choice(['male', 'female', 'unknown']) if face_detected else None
        
        metadata = {
            'emotion': detected_emotion,
            'dominant_emotion': detected_emotion,  # Add this field for dashboard compatibility
            'confidence': round(confidence, 3),
            'face_detected': face_detected,
            'crowd_mood': self.current_crowd_mood,
            'estimated_age': estimated_age,
            'estimated_gender': estimated_gender,
            'engagement_level': 'high' if detected_emotion in ['engaged', 'curious', 'happy'] else 'low'
        }
        
        return SensorReading(
            device_id=self.device_id,
            sensor_type='camera_emotion',
            value=confidence,  # Use confidence as the numeric value
            metadata=metadata
        )
    
    def generate_sensor_cycle(self) -> List[SensorReading]:
        """
        Generate a complete set of sensor readings for one cycle
        """
        readings = []
        
        # Generate all sensor types
        sensors = [
            self.simulate_temperature(),
            self.simulate_humidity(),
            self.simulate_light(),
            self.simulate_sound(),
            self.simulate_camera_emotion()
        ]
        
        # Add timestamp to all readings
        now = datetime.now()
        for sensor in sensors:
            sensor.timestamp = now
            readings.append(sensor)
        
        return readings
    
    def save_readings_to_db(self, readings: List[SensorReading]) -> bool:
        """
        Save sensor readings to Oracle database
        """
        try:
            if not self.db.is_connected:
                if not self.db.connect():
                    logger.warning("⚠️ Oracle indisponível - usando armazenamento em memória")
                    # Enable fallback mode for sensor simulator
                    self.db.is_connected = True
            
            success_count = 0
            for reading in readings:
                success = self.db.insert_sensor_data(
                    device_id=reading.device_id,
                    sensor_type=reading.sensor_type,
                    sensor_value=reading.value,
                    metadata=reading.metadata
                )
                if success:
                    success_count += 1
            
            logger.info(f"✅ {success_count}/{len(readings)} leituras salvas no banco")
            return success_count == len(readings)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar no banco: {str(e)}")
            return False
    
    def run_simulation(self, duration_minutes: int = 10, interval_seconds: int = 5):
        """
        Run the sensor simulation for specified duration
        """
        logger.info(f"🚀 Iniciando simulação por {duration_minutes} minutos...")
        logger.info(f"📊 Intervalo entre leituras: {interval_seconds} segundos")
        
        self.running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        cycle_count = 0
        
        try:
            while self.running and time.time() < end_time:
                cycle_start = time.time()
                
                # Generate sensor readings
                readings = self.generate_sensor_cycle()
                
                # Log current readings
                cycle_count += 1
                logger.info(f"\n📡 Ciclo {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                for reading in readings:
                    value_str = f"{reading.value:.1f}" if isinstance(reading.value, float) else str(reading.value)
                    unit = reading.metadata.get('unit', '')
                    logger.info(f"   {reading.sensor_type:15} {value_str:>6} {unit}")
                
                # Save to database
                if not self.save_readings_to_db(readings):
                    logger.warning("⚠️ Erro ao salvar dados - continuando simulação...")
                
                # Wait for next cycle
                elapsed = time.time() - cycle_start
                sleep_time = max(0, interval_seconds - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️ Simulação interrompida pelo usuário")
        except Exception as e:
            logger.error(f"\n❌ Erro na simulação: {str(e)}")
        finally:
            self.running = False
            if self.db.is_connected:
                self.db.disconnect()
            
            logger.info(f"\n✅ Simulação finalizada - {cycle_count} ciclos executados")
    
    def run_single_cycle(self) -> List[SensorReading]:
        """
        Execute a single sensor reading cycle (useful for testing)
        """
        logger.info("🔄 Executando ciclo único de sensores...")
        
        readings = self.generate_sensor_cycle()
        
        # Display readings
        logger.info(f"📊 Leituras geradas em {datetime.now().strftime('%H:%M:%S')}:")
        for reading in readings:
            value_str = f"{reading.value:.1f}" if isinstance(reading.value, float) else str(reading.value)
            unit = reading.metadata.get('unit', '')
            logger.info(f"   {reading.sensor_type:15} {value_str:>6} {unit}")
            logger.info(f"   └─ Metadata: {reading.metadata}")
        
        return readings

def main():
    """
    Main function for standalone execution
    """
    simulator = SensorSimulator()
    
    print("🎯 Aurora Totem - Sensor Simulator")
    print("=" * 50)
    print("1. Executar ciclo único (teste)")
    print("2. Simulação contínua (5 min)")
    print("3. Simulação longa (30 min)")
    print("4. Simulação personalizada")
    print("5. Sair")
    
    try:
        choice = input("\nEscolha uma opção (1-5): ").strip()
        
        if choice == "1":
            readings = simulator.run_single_cycle()
            
            save = input("\nSalvar no banco de dados? (s/n): ").strip().lower()
            if save == 's':
                simulator.save_readings_to_db(readings)
                
        elif choice == "2":
            simulator.run_simulation(duration_minutes=5, interval_seconds=5)
            
        elif choice == "3":
            simulator.run_simulation(duration_minutes=30, interval_seconds=10)
            
        elif choice == "4":
            duration = int(input("Duração em minutos: "))
            interval = int(input("Intervalo em segundos: "))
            simulator.run_simulation(duration_minutes=duration, interval_seconds=interval)
            
        elif choice == "5":
            print("👋 Até logo!")
            
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n👋 Simulação cancelada")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    main()