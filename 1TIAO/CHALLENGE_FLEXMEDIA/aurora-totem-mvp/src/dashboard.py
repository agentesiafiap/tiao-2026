#!/usr/bin/env python3
"""
Aurora Totem - Streamlit Dashboard
Real-time monitoring dashboard for empathetic AI totem system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List
import logging

from config import API_CONFIG, DASHBOARD_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Aurora Totem Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for totem-style design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .sensor-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .emotion-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background: #e3f2fd;
        color: #1976d2;
        border-radius: 15px;
        margin: 0.2rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

class DashboardAPI:
    """API client for dashboard data"""
    
    def __init__(self):
        self.base_url = f"http://{API_CONFIG['host']}:{API_CONFIG['port']}"
        
    def get_sensor_data(self, limit: int = 100) -> Dict:
        """Fetch latest sensor data"""
        try:
            response = requests.get(f"{self.base_url}/api/sensors/data?limit={limit}")
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return {"success": False, "data": {"records": []}}
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return {"success": False, "data": {"records": []}}
    
    def get_sensor_stats(self) -> Dict:
        """Fetch sensor statistics"""
        try:
            response = requests.get(f"{self.base_url}/api/sensors/stats")
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "data": {}}
        except Exception as e:
            st.error(f"Stats error: {str(e)}")
            return {"success": False, "data": {}}
    
    def get_health_status(self) -> Dict:
        """Fetch system health status"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": "API Offline"}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}"}
    
    def get_ml_model_status(self) -> Dict:
        """Fetch ML model status"""
        try:
            response = requests.get(f"{self.base_url}/api/ml/model-status")
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "data": {}}
        except Exception as e:
            logger.error(f"ML status error: {str(e)}")
            return {"success": False, "data": {}}
    
    def predict_engagement(self, sensor_data: Dict) -> Dict:
        """Get engagement prediction from ML model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/ml/predict-engagement",
                json={"sensor_data": sensor_data}
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "data": {}}
        except Exception as e:
            logger.error(f"Engagement prediction error: {str(e)}")
            return {"success": False, "data": {}}
    
    def predict_emotion(self, sensor_data: Dict) -> Dict:
        """Get emotion prediction from ML model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/ml/predict-emotion",
                json={"sensor_data": sensor_data}
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "data": {}}
        except Exception as e:
            logger.error(f"Emotion prediction error: {str(e)}")
            return {"success": False, "data": {}}
    
    def train_ml_models(self) -> Dict:
        """Trigger ML model training"""
        try:
            response = requests.post(f"{self.base_url}/api/ml/train-models")
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": "Training failed"}
        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            return {"success": False, "message": str(e)}

def create_sensor_chart(df: pd.DataFrame, sensor_type: str, title: str, color: str) -> go.Figure:
    """Create time series chart for sensor data"""
    sensor_data = df[df['sensor_type'] == sensor_type].copy()
    
    if sensor_data.empty:
        fig = go.Figure()
        fig.add_annotation(text=f"No {sensor_type} data available", 
                          xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(title=title)
        return fig
    
    sensor_data['timestamp'] = pd.to_datetime(sensor_data['timestamp'])
    sensor_data = sensor_data.sort_values('timestamp')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sensor_data['timestamp'],
        y=sensor_data['sensor_value'],
        mode='lines+markers',
        name=sensor_type.title(),
        line=dict(color=color, width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Value",
        hovermode='x unified',
        template="plotly_white"
    )
    
    return fig

def create_emotion_distribution(df: pd.DataFrame) -> go.Figure:
    """Create emotion distribution chart"""
    camera_data = df[df['sensor_type'] == 'camera_emotion'].copy()
    
    if camera_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No emotion data available", 
                          xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    # Extract emotions from metadata
    emotions = []
    for _, row in camera_data.iterrows():
        try:
            metadata = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
            if 'dominant_emotion' in metadata:
                emotions.append(metadata['dominant_emotion'])
        except:
            continue
    
    if not emotions:
        fig = go.Figure()
        fig.add_annotation(text="No emotion metadata available", 
                          xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    emotion_counts = pd.Series(emotions).value_counts()
    
    fig = go.Figure(data=[
        go.Bar(x=emotion_counts.index, y=emotion_counts.values,
               marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'])
    ])
    
    fig.update_layout(
        title="Emotion Distribution",
        xaxis_title="Emotion",
        yaxis_title="Count",
        template="plotly_white"
    )
    
    return fig

def create_environmental_overview(df: pd.DataFrame) -> go.Figure:
    """Create environmental sensors overview"""
    env_sensors = ['temperature', 'humidity', 'light', 'sound']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature (°C)', 'Humidity (%)', 'Light (lux)', 'Sound (dB)'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    for i, sensor_type in enumerate(env_sensors):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
        sensor_data = df[df['sensor_type'] == sensor_type].copy()
        
        if not sensor_data.empty:
            sensor_data['timestamp'] = pd.to_datetime(sensor_data['timestamp'])
            sensor_data = sensor_data.sort_values('timestamp').tail(50)  # Last 50 points
            
            fig.add_trace(
                go.Scatter(
                    x=sensor_data['timestamp'],
                    y=sensor_data['sensor_value'],
                    mode='lines',
                    name=sensor_type.title(),
                    line=dict(color=colors[i], width=2)
                ),
                row=row, col=col
            )
    
    fig.update_layout(
        title="Environmental Sensors Overview",
        height=600,
        showlegend=False,
        template="plotly_white"
    )
    
    return fig

def create_engagement_gauge(engagement_level: str, confidence: float) -> go.Figure:
    """Create engagement level gauge chart"""
    
    # Map engagement levels to numeric values
    engagement_map = {"low": 33, "medium": 66, "high": 100}
    value = engagement_map.get(engagement_level.lower(), 50)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"User Engagement<br><span style='font-size:0.8em'>Level: {engagement_level.title()}</span>"},
        delta={'reference': 50, 'suffix': '%'},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "#ffcdd2"},
                {'range': [33, 66], 'color': "#fff9c4"},
                {'range': [66, 100], 'color': "#c8e6c9"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': confidence * 100
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_emotion_chart(emotion: str, probabilities: Dict) -> go.Figure:
    """Create emotion probability bar chart"""
    
    if not probabilities:
        fig = go.Figure()
        fig.add_annotation(text="No emotion data available", 
                          xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    emotions = list(probabilities.keys())
    probs = [probabilities[e] * 100 for e in emotions]
    
    # Color code based on current emotion
    colors = ['#667eea' if e == emotion else '#cccccc' for e in emotions]
    
    fig = go.Figure(go.Bar(
        x=emotions,
        y=probs,
        marker_color=colors,
        text=[f"{p:.1f}%" for p in probs],
        textposition='auto'
    ))
    
    fig.update_layout(
        title=f"Emotion Analysis<br><span style='font-size:0.8em'>Detected: {emotion.title()}</span>",
        xaxis_title="Emotion",
        yaxis_title="Confidence (%)",
        template="plotly_white",
        height=300,
        yaxis={'range': [0, 100]}
    )
    
    return fig

def create_ml_feature_importance(sensor_data: Dict) -> go.Figure:
    """Create feature importance visualization"""
    
    features = list(sensor_data.keys())
    values = list(sensor_data.values())
    
    # Normalize values to 0-100 scale for visualization
    max_val = max(values) if values else 1
    normalized = [(v / max_val) * 100 if max_val > 0 else 0 for v in values]
    
    fig = go.Figure(go.Bar(
        y=features,
        x=normalized,
        orientation='h',
        marker=dict(
            color=normalized,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Intensity")
        ),
        text=[f"{v:.2f}" for v in values],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Sensor Features (Current State)",
        xaxis_title="Normalized Value (%)",
        yaxis_title="Sensor",
        template="plotly_white",
        height=400
    )
    
    return fig

def display_system_metrics(api_client: DashboardAPI):
    """Display system health and metrics"""
    
    # System Health Status
    health = api_client.get_health_status()
    stats = api_client.get_sensor_stats()
    ml_status = api_client.get_ml_model_status()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if health.get('success', False):
            st.metric("System Status", "🟢 Online", "Connected")
        else:
            st.metric("System Status", "🔴 Offline", "Disconnected")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if stats.get('success', False):
            total_records = stats['data'].get('total_records', 0)
            st.metric("Total Records", f"{total_records:,}", "Database")
        else:
            st.metric("Total Records", "N/A", "No data")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if health.get('success', False) and 'data' in health:
            websockets_count = health['data'].get('active_websockets', 0)
            st.metric("Active Connections", websockets_count, "WebSockets")
        else:
            st.metric("Active Connections", "0", "No connections")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if stats.get('success', False):
            sensor_types = len(stats['data'].get('sensor_counts', {}))
            st.metric("Sensor Types", sensor_types, "Active")
        else:
            st.metric("Sensor Types", "0", "No sensors")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if ml_status.get('success', False):
            models_ready = ml_status['data'].get('models_ready', False)
            if models_ready:
                st.metric("ML Models", "🤖 Ready", "AI Active")
            else:
                st.metric("ML Models", "⏳ Training", "Not Ready")
        else:
            st.metric("ML Models", "❌ Offline", "No ML")
        st.markdown('</div>', unsafe_allow_html=True)

def display_ml_predictions(api_client: DashboardAPI, df: pd.DataFrame):
    """Display real-time ML predictions section"""
    
    st.markdown("### 🤖 Machine Learning Predictions")
    
    # Check if ML models are ready
    ml_status = api_client.get_ml_model_status()
    if not ml_status.get('success', False) or not ml_status['data'].get('models_ready', False):
        st.warning("⚠️ ML models not ready. Please train models first.")
        if st.button("🎯 Train ML Models"):
            with st.spinner("Training models... This may take a minute..."):
                result = api_client.train_ml_models()
                if result.get('success', False):
                    st.success("✅ Models trained successfully!")
                    st.json(result['data'])
                    st.rerun()
                else:
                    st.error("❌ Training failed")
        return
    
    # Prepare sensor data for prediction
    if df.empty:
        st.info("No sensor data available for predictions")
        return
    
    # Get latest sensor values for each type
    latest_data = {}
    for sensor_type in df['sensor_type'].unique():
        sensor_df = df[df['sensor_type'] == sensor_type]
        if not sensor_df.empty:
            latest_value = sensor_df.iloc[-1]['sensor_value']
            latest_data[sensor_type] = float(latest_value)
    
    # Add default values for missing sensors
    sensor_defaults = {
        'heart_rate': 70,
        'skin_conductance': 5.0,
        'eye_tracking': 0.5,
        'face_emotion': 0.5,
        'voice_emotion': 0.5,
        'proximity': 100,
        'interaction_duration': 30,
        'temperature': 22,
        'humidity': 60,
        'light': 300,
        'sound': 45
    }
    
    for key, default in sensor_defaults.items():
        if key not in latest_data:
            latest_data[key] = default
    
    # Create two columns for predictions
    col1, col2 = st.columns(2)
    
    with col1:
        # Engagement Prediction
        engagement_result = api_client.predict_engagement(latest_data)
        if engagement_result.get('success', False):
            prediction = engagement_result['data'].get('prediction', {})
            engagement_level = prediction.get('predicted_engagement', 'medium')
            confidence = prediction.get('confidence', 0.5)
            
            st.plotly_chart(
                create_engagement_gauge(engagement_level, confidence),
                width="stretch"
            )
            
            # Show probabilities
            if 'probabilities' in prediction:
                probs = prediction['probabilities']
                st.markdown("**Engagement Probabilities:**")
                for level, prob in probs.items():
                    st.progress(prob, text=f"{level.title()}: {prob:.1%}")
        else:
            st.error("Failed to get engagement prediction")
    
    with col2:
        # Emotion Prediction
        emotion_result = api_client.predict_emotion(latest_data)
        if emotion_result.get('success', False):
            prediction = emotion_result['data'].get('prediction', {})
            emotion = prediction.get('predicted_emotion', 'neutral')
            probabilities = prediction.get('probabilities', {})
            
            st.plotly_chart(
                create_emotion_chart(emotion, probabilities),
                width="stretch"
            )
        else:
            st.error("Failed to get emotion prediction")
    
    # Feature visualization
    st.markdown("#### 📊 Current Sensor State")
    st.plotly_chart(
        create_ml_feature_importance(latest_data),
        width="stretch"
    )

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('''
    <div class="main-header">
        <h1>🤖 Aurora Totem Dashboard</h1>
        <p>Real-time monitoring of empathetic AI totem system</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize API client
    api_client = DashboardAPI()
    
    # Sidebar controls
    st.sidebar.title("Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 30)
    
    # Data range selector
    data_limit = st.sidebar.selectbox(
        "Data Points to Display",
        [50, 100, 200, 500, 1000],
        index=1
    )
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    st.sidebar.divider()
    
    # ML Controls Section (NEW!)
    st.sidebar.title("🤖 ML Controls")
    
    ml_status = api_client.get_ml_model_status()
    if ml_status.get('success', False):
        models_ready = ml_status['data'].get('models_ready', False)
        if models_ready:
            st.sidebar.success("✅ ML Models Active")
        else:
            st.sidebar.warning("⏳ Models Not Trained")
            if st.sidebar.button("🎯 Train Models"):
                with st.spinner("Training ML models..."):
                    result = api_client.train_ml_models()
                    if result.get('success', False):
                        st.sidebar.success("Training complete!")
                        st.rerun()
    else:
        st.sidebar.error("❌ ML Service Offline")
    
    # System metrics
    st.subheader("📊 System Metrics")
    display_system_metrics(api_client)
    
    st.divider()
    
    # Fetch sensor data
    sensor_response = api_client.get_sensor_data(limit=data_limit)
    
    if sensor_response.get('success', False) and sensor_response['data']['records']:
        df = pd.DataFrame(sensor_response['data']['records'])
        
        # Main charts section
        st.subheader("🌡️ Environmental Monitoring")
        
        # Environmental overview
        env_chart = create_environmental_overview(df)
        st.plotly_chart(env_chart, width="stretch")
        
        # Individual sensor charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature chart
            temp_chart = create_sensor_chart(df, 'temperature', 'Temperature (°C)', '#FF6B6B')
            st.plotly_chart(temp_chart, width="stretch")
            
            # Light chart
            light_chart = create_sensor_chart(df, 'light', 'Light Level (lux)', '#45B7D1')
            st.plotly_chart(light_chart, width="stretch")
        
        with col2:
            # Humidity chart
            humidity_chart = create_sensor_chart(df, 'humidity', 'Humidity (%)', '#4ECDC4')
            st.plotly_chart(humidity_chart, width="stretch")
            
            # Sound chart
            sound_chart = create_sensor_chart(df, 'sound', 'Sound Level (dB)', '#96CEB4')
            st.plotly_chart(sound_chart, width="stretch")
        
        st.divider()
        
        # Emotion analysis section
        st.subheader("😊 Emotion Analysis")
        emotion_chart = create_emotion_distribution(df)
        st.plotly_chart(emotion_chart, width="stretch")
        
        # Recent emotions display
        camera_data = df[df['sensor_type'] == 'camera_emotion'].tail(10)
        if not camera_data.empty:
            st.write("**Recent Emotions Detected:**")
            emotions_html = ""
            for _, row in camera_data.iterrows():
                try:
                    metadata = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                    emotion = metadata.get('dominant_emotion', 'Unknown')
                    confidence = metadata.get('confidence', 0)
                    emotions_html += f'<span class="emotion-badge">{emotion} ({confidence:.1%})</span>'
                except:
                    continue
            
            if emotions_html:
                st.markdown(emotions_html, unsafe_allow_html=True)
        
        st.divider()
        
        # 🤖 ML PREDICTIONS SECTION (NEW!)
        display_ml_predictions(api_client, df)
        
        st.divider()
        
        # Data table
        st.subheader("📋 Recent Sensor Data")
        
        # Format data for display
        display_df = df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%H:%M:%S')
        display_df = display_df[['timestamp', 'sensor_type', 'sensor_value', 'device_id']].tail(20)
        
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )
        
    else:
        st.warning("⚠️ No sensor data available. Please check if the API server is running and sensors are active.")
        
        # Show connection help
        st.info(f"""
        **Connection Details:**
        - API Server: {api_client.base_url}
        - Expected endpoints: /api/sensors/data, /api/sensors/stats
        - Make sure the FastAPI server is running: `python main.py`
        """)
    
    # Footer with last update time
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()