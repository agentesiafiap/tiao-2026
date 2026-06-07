#!/usr/bin/env python3
"""
Aurora Totem - Machine Learning Model
User behavior classification and emotion pattern recognition system
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import joblib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import warnings
warnings.filterwarnings('ignore')

from .config import ML_CONFIG, DATABASE_CONFIG
from .database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionPatternAnalyzer:
    """
    Analyzes emotion patterns and user engagement for the Aurora Totem system
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.db = DatabaseManager()
        self.emotion_categories = [
            'happy', 'sad', 'angry', 'surprised', 'fear', 'disgust', 'neutral'
        ]
        self.engagement_levels = ['low', 'medium', 'high']
        
    def generate_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        Generate synthetic training data based on realistic patterns
        """
        logger.info(f"🧠 Generating {n_samples} synthetic training samples...")
        
        np.random.seed(42)  # For reproducible results
        
        data = []
        
        for _ in range(n_samples):
            # Environmental factors
            temperature = np.random.normal(25, 5)  # °C
            humidity = np.random.normal(60, 15)    # %
            light = np.random.normal(500, 200)     # lux
            sound = np.random.normal(50, 15)       # dB
            
            # Time features
            hour = np.random.randint(8, 22)  # Business hours
            day_of_week = np.random.randint(0, 7)
            
            # User demographics (synthetic)
            age_group = np.random.choice(['child', 'teen', 'adult', 'senior'])
            gender = np.random.choice(['male', 'female', 'other'])
            
            # Interaction duration (seconds)
            base_duration = np.random.exponential(30)
            
            # Environmental influence on engagement
            temp_comfort = 1 - abs(temperature - 24) / 10  # Optimal at 24°C
            light_comfort = min(light / 300, 1)  # Better lighting = more engagement
            sound_comfort = 1 - max(0, sound - 60) / 40  # Noise reduces engagement
            
            # Time influence
            time_factor = 1 - abs(hour - 14) / 8  # Peak at 2 PM
            weekend_factor = 1.2 if day_of_week >= 5 else 1.0
            
            # Calculate engagement score
            engagement_score = (
                temp_comfort * 0.2 + 
                light_comfort * 0.3 + 
                sound_comfort * 0.2 + 
                time_factor * 0.2 +
                np.random.normal(0, 0.1)  # Random factor
            ) * weekend_factor
            
            # Adjust duration based on engagement
            interaction_duration = base_duration * (1 + engagement_score)
            
            # Emotion based on engagement and environment
            if engagement_score > 0.7:
                emotion = np.random.choice(['happy', 'surprised'], p=[0.8, 0.2])
            elif engagement_score > 0.4:
                emotion = np.random.choice(['happy', 'neutral'], p=[0.6, 0.4])
            else:
                emotion = np.random.choice(['neutral', 'sad'], p=[0.7, 0.3])
            
            # Engagement level
            if interaction_duration > 60:
                engagement = 'high'
            elif interaction_duration > 20:
                engagement = 'medium'
            else:
                engagement = 'low'
            
            # User satisfaction (derived feature)
            satisfaction = min(1.0, engagement_score + np.random.normal(0, 0.1))
            
            data.append({
                'temperature': temperature,
                'humidity': humidity,
                'light': light,
                'sound': sound,
                'hour': hour,
                'day_of_week': day_of_week,
                'age_group': age_group,
                'gender': gender,
                'interaction_duration': interaction_duration,
                'emotion': emotion,
                'engagement_level': engagement,
                'satisfaction_score': satisfaction,
                'engagement_score': engagement_score
            })
        
        df = pd.DataFrame(data)
        logger.info(f"✅ Generated synthetic dataset: {df.shape}")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Prepare features for machine learning models
        """
        logger.info("🔧 Preparing features for ML models...")
        
        # Create a copy for processing
        data = df.copy()
        
        # Encode categorical variables
        if 'age_group' in data.columns:
            if 'age_group_encoder' not in self.encoders:
                self.encoders['age_group_encoder'] = LabelEncoder()
                data['age_group_encoded'] = self.encoders['age_group_encoder'].fit_transform(data['age_group'])
            else:
                data['age_group_encoded'] = self.encoders['age_group_encoder'].transform(data['age_group'])
        
        if 'gender' in data.columns:
            if 'gender_encoder' not in self.encoders:
                self.encoders['gender_encoder'] = LabelEncoder()
                data['gender_encoded'] = self.encoders['gender_encoder'].fit_transform(data['gender'])
            else:
                data['gender_encoded'] = self.encoders['gender_encoder'].transform(data['gender'])
        
        # Create time-based features
        if 'hour' in data.columns:
            data['is_morning'] = (data['hour'] >= 6) & (data['hour'] < 12)
            data['is_afternoon'] = (data['hour'] >= 12) & (data['hour'] < 18)
            data['is_evening'] = (data['hour'] >= 18) & (data['hour'] < 22)
            data['is_weekend'] = data['day_of_week'] >= 5
        
        # Environmental comfort indicators
        if all(col in data.columns for col in ['temperature', 'humidity', 'light', 'sound']):
            data['temp_comfort'] = 1 - np.abs(data['temperature'] - 24) / 10
            data['humidity_comfort'] = 1 - np.abs(data['humidity'] - 50) / 30
            data['light_adequacy'] = np.minimum(data['light'] / 400, 1)
            data['sound_comfort'] = 1 - np.maximum(0, data['sound'] - 55) / 30
        
        # Select feature columns
        feature_columns = [
            'temperature', 'humidity', 'light', 'sound',
            'hour', 'day_of_week', 'age_group_encoded', 'gender_encoded',
            'is_morning', 'is_afternoon', 'is_evening', 'is_weekend',
            'temp_comfort', 'humidity_comfort', 'light_adequacy', 'sound_comfort'
        ]
        
        # Filter existing columns
        feature_columns = [col for col in feature_columns if col in data.columns]
        
        X = data[feature_columns].values
        
        logger.info(f"✅ Prepared {X.shape[1]} features for {X.shape[0]} samples")
        return X, data
    
    def train_engagement_predictor(self, df: pd.DataFrame) -> Dict:
        """
        Train model to predict user engagement levels
        """
        logger.info("🎯 Training engagement prediction model...")
        
        X, processed_data = self.prepare_features(df)
        y = processed_data['engagement_level'].values
        
        # Encode engagement levels
        if 'engagement_encoder' not in self.encoders:
            self.encoders['engagement_encoder'] = LabelEncoder()
            y_encoded = self.encoders['engagement_encoder'].fit_transform(y)
        else:
            y_encoded = self.encoders['engagement_encoder'].transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=ML_CONFIG['test_size'], 
            random_state=ML_CONFIG['random_state']
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['engagement_scaler'] = scaler
        
        # Train multiple models
        models_to_try = {
            'random_forest': RandomForestClassifier(
                n_estimators=100, 
                random_state=ML_CONFIG['random_state'],
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100, 
                random_state=ML_CONFIG['random_state']
            ),
            'logistic_regression': LogisticRegression(
                random_state=ML_CONFIG['random_state'],
                max_iter=1000
            )
        }
        
        best_model = None
        best_score = 0
        best_name = ""
        
        for name, model in models_to_try.items():
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            mean_score = cv_scores.mean()
            
            logger.info(f"   {name}: CV Score = {mean_score:.4f} (+/- {cv_scores.std() * 2:.4f})")
            
            if mean_score > best_score:
                best_score = mean_score
                best_model = model
                best_name = name
        
        # Test best model
        y_pred = best_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"✅ Best engagement model: {best_name} (Accuracy: {accuracy:.4f})")
        
        # Store model
        self.models['engagement_predictor'] = best_model
        
        # Generate classification report
        target_names = self.encoders['engagement_encoder'].classes_
        report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
        
        return {
            'model_name': best_name,
            'accuracy': accuracy,
            'cv_score': best_score,
            'classification_report': report,
            'feature_count': X.shape[1]
        }
    
    def train_emotion_classifier(self, df: pd.DataFrame) -> Dict:
        """
        Train model to classify emotions from sensor data
        """
        logger.info("😊 Training emotion classification model...")
        
        X, processed_data = self.prepare_features(df)
        y = processed_data['emotion'].values
        
        # Encode emotions
        if 'emotion_encoder' not in self.encoders:
            self.encoders['emotion_encoder'] = LabelEncoder()
            y_encoded = self.encoders['emotion_encoder'].fit_transform(y)
        else:
            y_encoded = self.encoders['emotion_encoder'].transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=ML_CONFIG['test_size'], 
            random_state=ML_CONFIG['random_state'],
            stratify=y_encoded
        )
        
        # Scale features
        if 'emotion_scaler' not in self.scalers:
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            self.scalers['emotion_scaler'] = scaler
        else:
            scaler = self.scalers['emotion_scaler']
            X_train_scaled = scaler.transform(X_train)
        
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest (works well for multi-class classification)
        model = RandomForestClassifier(
            n_estimators=150,
            random_state=ML_CONFIG['random_state'],
            class_weight='balanced',  # Handle class imbalance
            n_jobs=-1
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        
        logger.info(f"✅ Emotion classifier accuracy: {accuracy:.4f}")
        logger.info(f"✅ Cross-validation score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Store model
        self.models['emotion_classifier'] = model
        
        # Generate classification report
        target_names = self.encoders['emotion_encoder'].classes_
        report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
        
        return {
            'accuracy': accuracy,
            'cv_score': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'classification_report': report,
            'emotion_classes': list(target_names)
        }
    
    def train_satisfaction_predictor(self, df: pd.DataFrame) -> Dict:
        """
        Train model to predict user satisfaction scores
        """
        logger.info("⭐ Training satisfaction prediction model...")
        
        X, processed_data = self.prepare_features(df)
        
        # Convert satisfaction to categories for classification
        satisfaction_bins = [0, 0.3, 0.7, 1.0]
        satisfaction_labels = ['low', 'medium', 'high']
        processed_data['satisfaction_category'] = pd.cut(
            processed_data['satisfaction_score'], 
            bins=satisfaction_bins, 
            labels=satisfaction_labels
        )
        
        y = processed_data['satisfaction_category'].values
        
        # Remove any NaN values
        mask = ~pd.isna(y)
        X = X[mask]
        y = y[mask]
        
        # Encode satisfaction categories
        if 'satisfaction_encoder' not in self.encoders:
            self.encoders['satisfaction_encoder'] = LabelEncoder()
            y_encoded = self.encoders['satisfaction_encoder'].fit_transform(y)
        else:
            y_encoded = self.encoders['satisfaction_encoder'].transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=ML_CONFIG['test_size'], 
            random_state=ML_CONFIG['random_state']
        )
        
        # Scale features
        if 'satisfaction_scaler' not in self.scalers:
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            self.scalers['satisfaction_scaler'] = scaler
        else:
            scaler = self.scalers['satisfaction_scaler']
            X_train_scaled = scaler.transform(X_train)
        
        X_test_scaled = scaler.transform(X_test)
        
        # Train Gradient Boosting model
        model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            random_state=ML_CONFIG['random_state']
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"✅ Satisfaction predictor accuracy: {accuracy:.4f}")
        
        # Store model
        self.models['satisfaction_predictor'] = model
        
        return {
            'accuracy': accuracy,
            'satisfaction_categories': satisfaction_labels
        }
    
    def perform_user_segmentation(self, df: pd.DataFrame) -> Dict:
        """
        Perform user behavior clustering/segmentation
        """
        logger.info("👥 Performing user behavior segmentation...")
        
        # Prepare features for clustering
        cluster_features = []
        
        if 'interaction_duration' in df.columns:
            cluster_features.append(df['interaction_duration'])
        if 'satisfaction_score' in df.columns:
            cluster_features.append(df['satisfaction_score'])
        if 'engagement_score' in df.columns:
            cluster_features.append(df['engagement_score'])
        
        # Add emotion distribution features
        emotion_dummies = pd.get_dummies(df['emotion'], prefix='emotion')
        for col in emotion_dummies.columns:
            cluster_features.append(emotion_dummies[col])
        
        # Create feature matrix
        X_cluster = np.column_stack(cluster_features)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_cluster)
        
        # Determine optimal number of clusters using elbow method
        inertias = []
        K_range = range(2, 8)
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=ML_CONFIG['random_state'])
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
        
        # Use 4 clusters as a reasonable default for user types
        optimal_k = 4
        
        # Final clustering
        kmeans = KMeans(n_clusters=optimal_k, random_state=ML_CONFIG['random_state'])
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # Store clustering model
        self.models['user_segmentation'] = kmeans
        self.scalers['segmentation_scaler'] = scaler
        
        # Analyze clusters
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = cluster_labels
        
        cluster_analysis = {}
        for i in range(optimal_k):
            cluster_data = df_with_clusters[df_with_clusters['cluster'] == i]
            
            cluster_analysis[f'cluster_{i}'] = {
                'size': len(cluster_data),
                'avg_duration': cluster_data['interaction_duration'].mean(),
                'avg_satisfaction': cluster_data['satisfaction_score'].mean(),
                'dominant_emotion': cluster_data['emotion'].mode().iloc[0],
                'engagement_distribution': cluster_data['engagement_level'].value_counts().to_dict()
            }
        
        logger.info(f"✅ Identified {optimal_k} user segments")
        
        return {
            'n_clusters': optimal_k,
            'cluster_analysis': cluster_analysis,
            'inertias': inertias
        }
    
    def predict_engagement(self, sensor_data: Dict) -> Dict:
        """
        Predict user engagement based on current sensor data
        """
        if 'engagement_predictor' not in self.models:
            return {'error': 'Engagement model not trained'}
        
        # Prepare features
        features = self._prepare_prediction_features(sensor_data)
        
        if features is None:
            return {'error': 'Invalid sensor data format'}
        
        # Scale features
        features_scaled = self.scalers['engagement_scaler'].transform([features])
        
        # Predict
        prediction = self.models['engagement_predictor'].predict(features_scaled)[0]
        probabilities = self.models['engagement_predictor'].predict_proba(features_scaled)[0]
        
        # Decode prediction
        engagement_level = self.encoders['engagement_encoder'].inverse_transform([prediction])[0]
        
        # Create probability dictionary
        prob_dict = {}
        classes = self.encoders['engagement_encoder'].classes_
        for i, cls in enumerate(classes):
            prob_dict[cls] = float(probabilities[i])
        
        return {
            'predicted_engagement': engagement_level,
            'probabilities': prob_dict,
            'confidence': float(max(probabilities))
        }
    
    def predict_emotion(self, sensor_data: Dict) -> Dict:
        """
        Predict emotion based on sensor data
        """
        if 'emotion_classifier' not in self.models:
            return {'error': 'Emotion model not trained'}
        
        # Prepare features
        features = self._prepare_prediction_features(sensor_data)
        
        if features is None:
            return {'error': 'Invalid sensor data format'}
        
        # Scale features
        features_scaled = self.scalers['emotion_scaler'].transform([features])
        
        # Predict
        prediction = self.models['emotion_classifier'].predict(features_scaled)[0]
        probabilities = self.models['emotion_classifier'].predict_proba(features_scaled)[0]
        
        # Decode prediction
        emotion = self.encoders['emotion_encoder'].inverse_transform([prediction])[0]
        
        # Create probability dictionary
        prob_dict = {}
        classes = self.encoders['emotion_encoder'].classes_
        for i, cls in enumerate(classes):
            prob_dict[cls] = float(probabilities[i])
        
        return {
            'predicted_emotion': emotion,
            'probabilities': prob_dict,
            'confidence': float(max(probabilities))
        }
    
    def _prepare_prediction_features(self, sensor_data: Dict) -> Optional[List]:
        """
        Prepare features for prediction from raw sensor data
        """
        try:
            # Extract basic sensor values
            temperature = sensor_data.get('temperature', 25)
            humidity = sensor_data.get('humidity', 50)
            light = sensor_data.get('light', 400)
            sound = sensor_data.get('sound', 50)
            
            # Time features (use current time if not provided)
            current_time = datetime.now()
            hour = sensor_data.get('hour', current_time.hour)
            day_of_week = sensor_data.get('day_of_week', current_time.weekday())
            
            # Demographics (default values)
            age_group = sensor_data.get('age_group', 'adult')
            gender = sensor_data.get('gender', 'other')
            
            # Encode categorical variables
            try:
                age_encoded = self.encoders['age_group_encoder'].transform([age_group])[0]
            except:
                age_encoded = 2  # Default to 'adult'
            
            try:
                gender_encoded = self.encoders['gender_encoder'].transform([gender])[0]
            except:
                gender_encoded = 2  # Default to 'other'
            
            # Time-based features
            is_morning = 6 <= hour < 12
            is_afternoon = 12 <= hour < 18
            is_evening = 18 <= hour < 22
            is_weekend = day_of_week >= 5
            
            # Comfort indicators
            temp_comfort = 1 - abs(temperature - 24) / 10
            humidity_comfort = 1 - abs(humidity - 50) / 30
            light_adequacy = min(light / 400, 1)
            sound_comfort = 1 - max(0, sound - 55) / 30
            
            features = [
                temperature, humidity, light, sound,
                hour, day_of_week, age_encoded, gender_encoded,
                is_morning, is_afternoon, is_evening, is_weekend,
                temp_comfort, humidity_comfort, light_adequacy, sound_comfort
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing prediction features: {str(e)}")
            return None
    
    def train_all_models(self, use_synthetic_data: bool = True) -> Dict:
        """
        Train all ML models with available data
        """
        logger.info("🚀 Starting complete ML model training...")
        
        results = {}
        
        try:
            # Get training data
            if use_synthetic_data:
                df = self.generate_synthetic_data(ML_CONFIG['synthetic_data_size'])
            else:
                # Try to get real data from database
                df = self._load_real_data()
                if df is None or len(df) < 100:
                    logger.warning("Insufficient real data, using synthetic data")
                    df = self.generate_synthetic_data(ML_CONFIG['synthetic_data_size'])
            
            # Train models
            logger.info("Training engagement prediction model...")
            results['engagement'] = self.train_engagement_predictor(df)
            
            logger.info("Training emotion classification model...")  
            results['emotion'] = self.train_emotion_classifier(df)
            
            logger.info("Training satisfaction prediction model...")
            results['satisfaction'] = self.train_satisfaction_predictor(df)
            
            logger.info("Performing user segmentation...")
            results['segmentation'] = self.perform_user_segmentation(df)
            
            # Save models
            self.save_models()
            
            logger.info("✅ All ML models trained successfully!")
            
            results['training_summary'] = {
                'models_trained': len(self.models),
                'training_samples': len(df),
                'timestamp': datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error during model training: {str(e)}")
            return {'error': str(e)}
    
    def _load_real_data(self) -> Optional[pd.DataFrame]:
        """
        Load real sensor data from database for training
        """
        try:
            if not self.db.connect():
                return None
            
            # Get recent sensor data
            sensor_data = self.db.get_latest_sensor_data(limit=1000)
            
            if not sensor_data:
                return None
            
            # Convert to DataFrame (would need more processing for real implementation)
            df = pd.DataFrame(sensor_data)
            
            # Close connection
            self.db.connection.close()
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading real data: {str(e)}")
            return None
    
    def save_models(self, model_dir: str = None) -> bool:
        """
        Save trained models and encoders to disk in organized directory structure
        """
        try:
            if model_dir is None:
                model_dir = ML_CONFIG['model_dir']
            
            # Create models directory if it doesn't exist
            os.makedirs(model_dir, exist_ok=True)
            
            model_prefix = ML_CONFIG['model_prefix']
            
            # Save models
            for name, model in self.models.items():
                file_path = os.path.join(model_dir, f"{model_prefix}_{name}.pkl")
                joblib.dump(model, file_path)
            
            # Save scalers
            for name, scaler in self.scalers.items():
                file_path = os.path.join(model_dir, f"{model_prefix}_{name}.pkl")
                joblib.dump(scaler, file_path)
            
            # Save encoders
            for name, encoder in self.encoders.items():
                file_path = os.path.join(model_dir, f"{model_prefix}_{name}.pkl")
                joblib.dump(encoder, file_path)
            
            logger.info(f"✅ Models saved to {model_dir}/{model_prefix}_*.pkl")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving models: {str(e)}")
            return False
    
    def load_models(self, model_dir: str = None) -> bool:
        """
        Load trained models from disk using organized directory structure
        """
        try:
            if model_dir is None:
                model_dir = ML_CONFIG['model_dir']
            
            model_prefix = ML_CONFIG['model_prefix']
            
            # Define expected model files
            model_files = {
                'engagement_predictor': os.path.join(model_dir, f"{model_prefix}_engagement_predictor.pkl"),
                'emotion_classifier': os.path.join(model_dir, f"{model_prefix}_emotion_classifier.pkl"), 
                'satisfaction_predictor': os.path.join(model_dir, f"{model_prefix}_satisfaction_predictor.pkl"),
                'user_segmentation': os.path.join(model_dir, f"{model_prefix}_user_segmentation.pkl")
            }
            
            scaler_files = {
                'engagement_scaler': os.path.join(model_dir, f"{model_prefix}_engagement_scaler.pkl"),
                'emotion_scaler': os.path.join(model_dir, f"{model_prefix}_emotion_scaler.pkl"),
                'satisfaction_scaler': os.path.join(model_dir, f"{model_prefix}_satisfaction_scaler.pkl"),
                'segmentation_scaler': os.path.join(model_dir, f"{model_prefix}_segmentation_scaler.pkl")
            }
            
            encoder_files = {
                'engagement_encoder': os.path.join(model_dir, f"{model_prefix}_engagement_encoder.pkl"),
                'emotion_encoder': os.path.join(model_dir, f"{model_prefix}_emotion_encoder.pkl"),
                'satisfaction_encoder': os.path.join(model_dir, f"{model_prefix}_satisfaction_encoder.pkl"),
                'age_group_encoder': os.path.join(model_dir, f"{model_prefix}_age_group_encoder.pkl"),
                'gender_encoder': os.path.join(model_dir, f"{model_prefix}_gender_encoder.pkl")
            }
            
            # Load models
            for name, path in model_files.items():
                try:
                    self.models[name] = joblib.load(path)
                    logger.info(f"✅ Loaded {name}")
                except:
                    logger.warning(f"⚠️ Could not load {name}")
            
            # Load scalers
            for name, path in scaler_files.items():
                try:
                    self.scalers[name] = joblib.load(path)
                except:
                    logger.warning(f"⚠️ Could not load {name}")
            
            # Load encoders
            for name, path in encoder_files.items():
                try:
                    self.encoders[name] = joblib.load(path)
                except:
                    logger.warning(f"⚠️ Could not load {name}")
            
            return len(self.models) > 0
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {str(e)}")
            return False

def main():
    """
    Main function for testing the ML model
    """
    print("🧠 Aurora Totem - Machine Learning Model Test")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = EmotionPatternAnalyzer()
    
    # Train models
    results = analyzer.train_all_models(use_synthetic_data=True)
    
    if 'error' in results:
        print(f"❌ Training failed: {results['error']}")
        return
    
    print("\n📊 Training Results:")
    print(f"✅ Engagement Model Accuracy: {results['engagement']['accuracy']:.4f}")
    print(f"✅ Emotion Model Accuracy: {results['emotion']['accuracy']:.4f}")  
    print(f"✅ Satisfaction Model Accuracy: {results['satisfaction']['accuracy']:.4f}")
    print(f"✅ User Segments Identified: {results['segmentation']['n_clusters']}")
    
    # Test predictions with sample data
    print("\n🧪 Testing Predictions:")
    
    sample_data = {
        'temperature': 26.5,
        'humidity': 65,
        'light': 450,
        'sound': 48,
        'hour': 14,
        'day_of_week': 2,
        'age_group': 'adult',
        'gender': 'other'
    }
    
    # Test engagement prediction
    engagement_pred = analyzer.predict_engagement(sample_data)
    print(f"🎯 Predicted Engagement: {engagement_pred.get('predicted_engagement', 'N/A')}")
    print(f"   Confidence: {engagement_pred.get('confidence', 0):.3f}")
    
    # Test emotion prediction
    emotion_pred = analyzer.predict_emotion(sample_data)
    print(f"😊 Predicted Emotion: {emotion_pred.get('predicted_emotion', 'N/A')}")
    print(f"   Confidence: {emotion_pred.get('confidence', 0):.3f}")
    
    print("\n✅ ML Model implementation complete!")
    print("🚀 Ready for integration with Aurora Totem system!")

if __name__ == "__main__":
    main()