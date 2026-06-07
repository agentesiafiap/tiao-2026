#!/usr/bin/env python3
"""
Aurora Totem - FastAPI Backend
REST API server with real-time WebSocket connections for empathetic AI totem
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
import asyncio
import json
import logging
from datetime import datetime, timedelta
import uvicorn
from contextlib import asynccontextmanager

from .config import API_CONFIG, SENSOR_CONFIG, DATABASE_CONFIG, ML_CONFIG
from .database import DatabaseManager
from .sensor_simulator import SensorSimulator
from .ml_model import EmotionPatternAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class SensorData(BaseModel):
    """Sensor data input model"""
    device_id: str = Field(..., description="Device identifier")
    sensor_type: str = Field(..., description="Type of sensor (temperature, humidity, etc.)")
    sensor_value: float = Field(..., description="Sensor reading value")
    metadata: Optional[Dict] = Field(default={}, description="Additional sensor metadata")

class SensorResponse(BaseModel):
    """Sensor data response model"""
    device_id: str
    sensor_type: str
    sensor_value: float
    timestamp: str
    metadata: Dict

class UserSession(BaseModel):
    """User session model"""
    session_id: str = Field(..., description="Unique session identifier")
    device_id: str = Field(..., description="Totem device identifier")
    user_age: Optional[int] = Field(None, description="Estimated user age")
    user_gender: Optional[str] = Field(None, description="Estimated user gender")
    interaction_duration: Optional[float] = Field(None, description="Session duration in seconds")
    emotions_detected: Optional[List[str]] = Field(default=[], description="List of emotions detected")
    engagement_score: Optional[float] = Field(None, description="User engagement score (0-1)")
    metadata: Optional[Dict] = Field(default={}, description="Additional session metadata")

class ApiResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[Union[Dict, List]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class MLPredictionRequest(BaseModel):
    """ML prediction request model"""
    sensor_data: Dict[str, Union[float, int, str]] = Field(..., description="Sensor data dictionary")

class MLPredictionResponse(BaseModel):
    """ML prediction response model"""
    predicted_value: str
    probabilities: Dict[str, float]
    confidence: float
    model_used: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.sensor_subscribers: List[WebSocket] = []
        self.dashboard_subscribers: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, connection_type: str = "general"):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if connection_type == "sensors":
            self.sensor_subscribers.append(websocket)
        elif connection_type == "dashboard":
            self.dashboard_subscribers.append(websocket)
            
        logger.info(f"🔌 Nova conexão WebSocket ({connection_type}): {len(self.active_connections)} ativas")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.sensor_subscribers:
            self.sensor_subscribers.remove(websocket)
        if websocket in self.dashboard_subscribers:
            self.dashboard_subscribers.remove(websocket)
            
        logger.info(f"🔌 Conexão WebSocket desconectada: {len(self.active_connections)} ativas")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {str(e)}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str, connection_type: str = "all"):
        """Broadcast message to all connections of specified type"""
        if connection_type == "all":
            connections = self.active_connections
        elif connection_type == "sensors":
            connections = self.sensor_subscribers
        elif connection_type == "dashboard":
            connections = self.dashboard_subscribers
        else:
            connections = []
        
        disconnected = []
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"❌ Erro no broadcast: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

# Global instances
manager = ConnectionManager()
db_manager = DatabaseManager()
ml_analyzer = None
simulator = None

def get_ml_analyzer():
    """Get ML analyzer instance with automatic model loading/training"""
    global ml_analyzer
    if ml_analyzer is None:
        ml_analyzer = EmotionPatternAnalyzer()
        # Try to load existing models
        try:
            ml_analyzer.load_models()
            logger.info("✅ ML models loaded from disk")
        except Exception as e:
            logger.warning(f"⚠️ Could not load ML models: {str(e)}")
            logger.info("🤖 Auto-training ML models...")
            # Auto-train if no models exist
            try:
                synthetic_data = ml_analyzer.generate_synthetic_data()
                ml_analyzer.train_engagement_predictor(synthetic_data)
                ml_analyzer.train_emotion_classifier(synthetic_data)
                ml_analyzer.save_models()
                logger.info("✅ ML models trained and saved automatically")
            except Exception as train_error:
                logger.error(f"❌ Auto-training failed: {str(train_error)}")
    return ml_analyzer

# Background task for sensor simulation
async def run_sensor_simulation():
    """Background task to run sensor simulation and broadcast data"""
    global simulator
    
    logger.info("🚀 Iniciando simulação de sensores em background...")
    
    while True:
        try:
            if simulator is None:
                simulator = SensorSimulator()
            
            # Generate sensor readings
            readings = simulator.generate_sensor_cycle()
            
            # Save to database
            if db_manager.is_connected or db_manager.connect():
                simulator.save_readings_to_db(readings)
            
            # Broadcast to WebSocket clients
            sensor_data = []
            for reading in readings:
                data = {
                    "device_id": reading.device_id,
                    "sensor_type": reading.sensor_type,
                    "sensor_value": reading.value,
                    "timestamp": reading.timestamp.isoformat() if reading.timestamp else datetime.now().isoformat(),
                    "metadata": reading.metadata
                }
                sensor_data.append(data)
            
            # Send to sensor subscribers
            await manager.broadcast(
                json.dumps({
                    "type": "sensor_update",
                    "data": sensor_data,
                    "timestamp": datetime.now().isoformat()
                }),
                connection_type="sensors"
            )
            
            # Send dashboard summary
            await manager.broadcast(
                json.dumps({
                    "type": "dashboard_update",
                    "summary": {
                        "active_sensors": len(sensor_data),
                        "latest_readings": sensor_data,
                        "timestamp": datetime.now().isoformat()
                    }
                }),
                connection_type="dashboard"
            )
            
            # Wait for next cycle (default 5 seconds)
            await asyncio.sleep(SENSOR_CONFIG.get('simulation_interval_max', 5.0))
            
        except Exception as e:
            logger.error(f"❌ Erro na simulação de sensores: {str(e)}")
            await asyncio.sleep(10)  # Wait longer on error

# Lifespan manager for startup/shutdown tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("🚀 Iniciando Aurora Totem API...")
    
    # Initialize database connection
    if db_manager.connect():
        logger.info("✅ Conexão com Oracle FIAP estabelecida")
    else:
        logger.warning("⚠️ Oracle indisponível - sistema funcionará com dados simulados")
        # Ensure fallback mode is properly enabled
        db_manager.is_connected = True  # Allow API to continue with fallback data
    
    # Start background sensor simulation
    sensor_task = asyncio.create_task(run_sensor_simulation())
    
    yield
    
    # Shutdown
    logger.info("🔄 Encerrando Aurora Totem API...")
    sensor_task.cancel()
    
    if db_manager.is_connected:
        db_manager.disconnect()
        logger.info("✅ Conexão com banco de dados fechada")

# Create FastAPI app
app = FastAPI(
    title="Aurora Totem API",
    description="REST API for Aurora Totem - Empathetic AI Interaction System",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/", response_model=ApiResponse)
async def root():
    """Root endpoint - API health check"""
    return ApiResponse(
        success=True,
        message="Aurora Totem API is running",
        data={
            "version": "1.0.0",
            "status": "healthy",
            "database_connected": db_manager.is_connected,
            "active_websockets": len(manager.active_connections)
        }
    )

# Database dependency
def get_db():
    """Database dependency for endpoints"""
    if not db_manager.is_connected:
        if not db_manager.connect():
            raise HTTPException(status_code=503, detail="Database connection failed")
    return db_manager

# === SENSOR DATA ENDPOINTS ===

@app.post("/api/sensors/data", response_model=ApiResponse)
async def create_sensor_data(sensor_data: SensorData, db: DatabaseManager = Depends(get_db)):
    """Create new sensor data entry"""
    try:
        success = db.insert_sensor_data(
            device_id=sensor_data.device_id,
            sensor_type=sensor_data.sensor_type,
            sensor_value=sensor_data.sensor_value,
            metadata=sensor_data.metadata
        )
        
        if success:
            # Broadcast to WebSocket clients
            await manager.broadcast(
                json.dumps({
                    "type": "new_sensor_data",
                    "data": sensor_data.dict(),
                    "timestamp": datetime.now().isoformat()
                }),
                connection_type="sensors"
            )
            
            return ApiResponse(
                success=True,
                message="Sensor data saved successfully",
                data=sensor_data.dict()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save sensor data")
            
    except Exception as e:
        logger.error(f"❌ Erro ao salvar dados do sensor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sensors/data", response_model=ApiResponse)
async def get_sensor_data(
    limit: int = 50,
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    hours: Optional[int] = None,
    db: DatabaseManager = Depends(get_db)
):
    """Get sensor data with optional filtering"""
    try:
        if hours:
            # Get data from specific timeframe
            data = db.get_data_by_timeframe(hours=hours, device_id=device_id)
        else:
            # Get latest data
            data = db.get_latest_data(limit=limit)
        
        # Filter by sensor type if specified
        if sensor_type:
            data = [item for item in data if item.get('sensor_type') == sensor_type]
        
        # Filter by device ID if specified and not already filtered by timeframe
        if device_id and not hours:
            data = [item for item in data if item.get('device_id') == device_id]
        
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(data)} sensor records",
            data={
                "records": data,
                "count": len(data),
                "filters": {
                    "limit": limit,
                    "device_id": device_id,
                    "sensor_type": sensor_type,
                    "hours": hours
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao consultar dados dos sensores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sensors/latest/{sensor_type}", response_model=ApiResponse)
async def get_latest_sensor_reading(sensor_type: str, db: DatabaseManager = Depends(get_db)):
    """Get the latest reading for a specific sensor type"""
    try:
        data = db.get_latest_data(limit=100)  # Get more data to find the sensor type
        
        # Find latest reading for the specified sensor type
        sensor_reading = None
        for item in data:
            if item.get('sensor_type') == sensor_type:
                sensor_reading = item
                break
        
        if sensor_reading:
            return ApiResponse(
                success=True,
                message=f"Latest {sensor_type} reading retrieved",
                data=sensor_reading
            )
        else:
            raise HTTPException(status_code=404, detail=f"No data found for sensor type: {sensor_type}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao consultar último dado do sensor {sensor_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sensors/stats", response_model=ApiResponse)
async def get_sensor_statistics(db: DatabaseManager = Depends(get_db)):
    """Get sensor statistics and summary"""
    try:
        stats = db.get_database_stats()
        
        return ApiResponse(
            success=True,
            message="Sensor statistics retrieved",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao consultar estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === USER SESSION ENDPOINTS ===

@app.post("/api/sessions", response_model=ApiResponse)
async def create_user_session(session: UserSession, db: DatabaseManager = Depends(get_db)):
    """Create new user interaction session"""
    try:
        success = db.insert_user_session(
            session_id=session.session_id,
            device_id=session.device_id,
            user_age=session.user_age,
            user_gender=session.user_gender,
            interaction_duration=session.interaction_duration,
            emotions_detected=session.emotions_detected,
            engagement_score=session.engagement_score,
            metadata=session.metadata
        )
        
        if success:
            return ApiResponse(
                success=True,
                message="User session created successfully",
                data=session.dict()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create user session")
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar sessão de usuário: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions", response_model=ApiResponse)
async def get_user_sessions(
    limit: int = 20,
    device_id: Optional[str] = None,
    hours: Optional[int] = None,
    db: DatabaseManager = Depends(get_db)
):
    """Get user sessions with optional filtering"""
    try:
        # This would require implementing get_user_sessions in DatabaseManager
        # For now, return a placeholder
        return ApiResponse(
            success=True,
            message="User sessions endpoint (placeholder)",
            data={
                "message": "User sessions functionality to be implemented",
                "filters": {"limit": limit, "device_id": device_id, "hours": hours}
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao consultar sessões: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === WEBSOCKET ENDPOINTS ===

@app.websocket("/ws/sensors")
async def websocket_sensors(websocket: WebSocket):
    """WebSocket endpoint for real-time sensor data"""
    await manager.connect(websocket, "sensors")
    
    try:
        # Send initial data
        if db_manager.is_connected or db_manager.connect():
            latest_data = db_manager.get_latest_data(limit=10)
            await manager.send_personal_message(
                json.dumps({
                    "type": "initial_data",
                    "data": latest_data,
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
        
        # Keep connection alive
        while True:
            # Wait for client messages (optional)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                # Handle client messages
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                        websocket
                    )
                    
            except asyncio.TimeoutError:
                # Send heartbeat if no messages received
                await manager.send_personal_message(
                    json.dumps({"type": "heartbeat", "timestamp": datetime.now().isoformat()}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("🔌 Cliente WebSocket desconectado (sensores)")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket de sensores: {str(e)}")
        manager.disconnect(websocket)

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for dashboard real-time updates"""
    await manager.connect(websocket, "dashboard")
    
    try:
        # Send initial dashboard data
        if db_manager.is_connected or db_manager.connect():
            stats = db_manager.get_database_stats()
            latest_data = db_manager.get_latest_data(limit=5)
            
            await manager.send_personal_message(
                json.dumps({
                    "type": "dashboard_init",
                    "stats": stats,
                    "latest_data": latest_data,
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
        
        # Keep connection alive
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                if message.get("type") == "request_update":
                    # Send current stats
                    stats = db_manager.get_database_stats()
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "stats_update",
                            "data": stats,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await manager.send_personal_message(
                    json.dumps({"type": "heartbeat", "timestamp": datetime.now().isoformat()}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("🔌 Cliente WebSocket desconectado (dashboard)")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket do dashboard: {str(e)}")
        manager.disconnect(websocket)

# === CONTROL ENDPOINTS ===

@app.post("/api/simulator/control", response_model=ApiResponse)
async def control_simulator(action: str):
    """Control sensor simulator (start/stop/status)"""
    try:
        global simulator
        
        if action == "status":
            status = "running" if simulator and hasattr(simulator, 'running') and simulator.running else "stopped"
            return ApiResponse(
                success=True,
                message=f"Simulator status: {status}",
                data={"status": status, "active_connections": len(manager.active_connections)}
            )
        
        elif action == "start":
            if simulator is None:
                simulator = SensorSimulator()
            return ApiResponse(
                success=True,
                message="Simulator started (background task running)",
                data={"status": "started"}
            )
            
        elif action == "stop":
            # The background task will continue, but this endpoint acknowledges the request
            return ApiResponse(
                success=True,
                message="Simulator stop requested",
                data={"status": "stop_requested"}
            )
            
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
            
    except Exception as e:
        logger.error(f"❌ Erro no controle do simulador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === MACHINE LEARNING ENDPOINTS ===

@app.post("/api/ml/predict-engagement", response_model=ApiResponse)
async def predict_engagement(request: MLPredictionRequest):
    """Predict user engagement level based on sensor data"""
    try:
        ml_analyzer = get_ml_analyzer()
        
        # Prepare sensor data for ML prediction
        sensor_data = {
            "heart_rate": request.sensor_data.get("heart_rate", 70),
            "skin_conductance": request.sensor_data.get("skin_conductance", 5.0),
            "eye_tracking": request.sensor_data.get("eye_tracking", 0.5),
            "face_emotion": request.sensor_data.get("face_emotion", 0.5),
            "voice_emotion": request.sensor_data.get("voice_emotion", 0.5),
            "proximity": request.sensor_data.get("proximity", 100),
            "interaction_duration": request.sensor_data.get("interaction_duration", 30)
        }
        
        prediction = ml_analyzer.predict_engagement(sensor_data)
        
        return ApiResponse(
            success=True,
            message="Engagement prediction completed",
            data={
                "prediction": prediction,
                "confidence": float(prediction.get("confidence", 0.5)),
                "engagement_level": prediction.get("engagement_level", "medium"),
                "sensor_data": sensor_data
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Erro na predição de engajamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/predict-emotion", response_model=ApiResponse)
async def predict_emotion(request: MLPredictionRequest):
    """Predict user emotion patterns based on sensor data"""
    try:
        ml_analyzer = get_ml_analyzer()
        
        # Prepare sensor data for emotion prediction
        sensor_data = {
            "heart_rate": request.sensor_data.get("heart_rate", 70),
            "skin_conductance": request.sensor_data.get("skin_conductance", 5.0),
            "eye_tracking": request.sensor_data.get("eye_tracking", 0.5),
            "face_emotion": request.sensor_data.get("face_emotion", 0.5),
            "voice_emotion": request.sensor_data.get("voice_emotion", 0.5),
            "proximity": request.sensor_data.get("proximity", 100),
            "interaction_duration": request.sensor_data.get("interaction_duration", 30)
        }
        
        prediction = ml_analyzer.predict_emotion(sensor_data)
        
        return ApiResponse(
            success=True,
            message="Emotion prediction completed",
            data={
                "prediction": prediction,
                "emotion": prediction.get("emotion", "neutral"),
                "confidence": float(prediction.get("confidence", 0.5)),
                "emotion_scores": prediction.get("emotion_scores", {}),
                "sensor_data": sensor_data
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Erro na predição de emoção: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/train-models", response_model=ApiResponse)
async def train_ml_models():
    """Train or retrain the ML models with synthetic data"""
    try:
        ml_analyzer = get_ml_analyzer()
        
        # Generate synthetic data for training
        logger.info("🤖 Generating synthetic data for ML training...")
        synthetic_data = ml_analyzer.generate_synthetic_data()
        
        # Train the models with synthetic data
        logger.info("🤖 Starting ML model training...")
        engagement_result = ml_analyzer.train_engagement_predictor(synthetic_data)
        emotion_result = ml_analyzer.train_emotion_classifier(synthetic_data)
        
        # Save models to disk for persistence
        try:
            ml_analyzer.save_models()
            logger.info("✅ ML models saved to disk for persistence")
        except Exception as save_error:
            logger.warning(f"⚠️ Could not save models: {str(save_error)}")
        
        return ApiResponse(
            success=True,
            message="ML models trained successfully",
            data={
                "training_completed": True,
                "models_trained": ["engagement_predictor", "emotion_classifier"],
                "engagement_accuracy": engagement_result.get("accuracy", 0.0),
                "emotion_accuracy": emotion_result.get("accuracy", 0.0),
                "data_size": len(synthetic_data),
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Erro no treinamento dos modelos ML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/model-status", response_model=ApiResponse)
async def get_ml_model_status():
    """Get status of ML models (trained/not trained)"""
    try:
        ml_analyzer = get_ml_analyzer()
        
        # Check if models are trained/loaded
        engagement_trained = hasattr(ml_analyzer, 'models') and 'engagement_predictor' in ml_analyzer.models and ml_analyzer.models['engagement_predictor'] is not None
        emotion_trained = hasattr(ml_analyzer, 'models') and 'emotion_classifier' in ml_analyzer.models and ml_analyzer.models['emotion_classifier'] is not None
        
        return ApiResponse(
            success=True,
            message="ML model status retrieved",
            data={
                "engagement_model_trained": engagement_trained,
                "emotion_model_trained": emotion_trained,
                "models_ready": engagement_trained and emotion_trained,
                "analyzer_initialized": ml_analyzer is not None
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status dos modelos ML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === DEVELOPMENT ENDPOINTS ===

@app.get("/api/dev/test-sensor")
async def test_sensor_generation():
    """Development endpoint to test sensor data generation"""
    try:
        global simulator
        if simulator is None:
            simulator = SensorSimulator()
            
        readings = simulator.run_single_cycle()
        
        # Convert to JSON serializable format
        data = []
        for reading in readings:
            data.append({
                "device_id": reading.device_id,
                "sensor_type": reading.sensor_type,
                "sensor_value": reading.value,
                "metadata": reading.metadata,
                "timestamp": reading.timestamp.isoformat() if reading.timestamp else datetime.now().isoformat()
            })
        
        return ApiResponse(
            success=True,
            message="Test sensor data generated",
            data=data
        )
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de sensores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server
    print("🚀 Starting Aurora Totem API Server...")
    print(f"📡 Server: http://{API_CONFIG['host']}:{API_CONFIG['port']}")
    print(f"📊 WebSocket Sensors: ws://{API_CONFIG['host']}:{API_CONFIG['port']}/ws/sensors")
    print(f"📈 WebSocket Dashboard: ws://{API_CONFIG['host']}:{API_CONFIG['port']}/ws/dashboard")
    print(f"📝 API Docs: http://{API_CONFIG['host']}:{API_CONFIG['port']}/docs")
    
    uvicorn.run(
        "main:app",
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        log_level="info"
    )