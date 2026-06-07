# 📖 **Aurora Totem MVP - Technical Documentation**
**Complete System Architecture, API Reference & Deployment Guide**

---

## 🏗️ **System Architecture**

### **Overview**
Aurora Totem implements a modern **Edge-Cloud IoT architecture** with real-time AI processing, designed for scalable deployment in physical spaces like retail stores, museums, corporate lobbies, and cultural venues.

### **Architecture Diagram**
```
🌟 Aurora Totem - Production Architecture
┌─────────────────────────────────────────────────────────┐
│                 PHYSICAL SPACE                          │
│  📷 Cameras + 🌡️ Environmental Sensors + 👥 People    │
└─────────────────┬───────────────────────────────────────┘
                  │ 
          ┌───────▼───────┐
          │  📡 IoT Edge   │ ← sensor_simulator.py
          │ Data Collection │   (Simulates real sensors)
          │ • 5 Sensor Types│
          │ • Real-time Data│
          └───────┬───────┘
                  │ HTTP/WebSocket
     ┌────────────▼────────────┐
     │    🌐 API Gateway       │ ← main.py (FastAPI)
     │   • 15 REST Endpoints  │
     │   • 2 WebSocket Streams │
     │   • Data Validation    │
     │   • Rate Limiting      │
     └────┬─────────────┬─────┘
          │             │
    ┌─────▼─────┐ ┌─────▼─────┐
    │ 🤖 ML/AI  │ │ 🗄️ Oracle │ ← database.py
    │ Engine    │ │ FIAP DB   │   (Enterprise DB)
    │ • Emotion │ │ • Sensors │
    │ • Engage  │ │ • ML Data │
    │ • Predict │ │ • Analytics│
    └─────┬─────┘ └───────────┘
          │
    ┌─────▼─────┐
    │ 📊 Dashboard │ ← dashboard.py (Streamlit)
    │ • Real-time  │
    │ • Analytics  │
    │ • Monitoring │
    └─────────────┘
```

---

## 💻 **Technology Stack**

### **Backend Core**
- **FastAPI 0.122.0** - High-performance async web framework
- **Python 3.13** - Latest stable Python runtime
- **Uvicorn** - ASGI server for production deployment
- **Pydantic** - Data validation and settings management

### **Database & Persistence**
- **Oracle Database** - Enterprise-grade RDBMS via FIAP
- **cx_Oracle** - Python Oracle database connector
- **Connection pooling** - Efficient database resource management

### **Machine Learning**
- **scikit-learn 1.7.2** - ML algorithms and model training
- **NumPy/Pandas** - Data processing and numerical computation
- **Pickle** - Model serialization and deployment

### **Frontend & Visualization**  
- **Streamlit 1.51.0** - Interactive web dashboard
- **Plotly** - Interactive charts and graphs
- **Real-time updates** - WebSocket-powered live data

### **Development & Testing**
- **pytest** - Comprehensive testing framework
- **Requests** - HTTP client for API testing
- **WebSockets** - Real-time communication testing

---

## 🔌 **API Documentation**

### **Base URL**: `http://localhost:8000`

### **Core Endpoints**

#### **System Health**
```http
GET /
```
**Response:**
```json
{
  "success": true,
  "message": "Aurora Totem MVP API",
  "timestamp": "2025-11-25T21:00:00Z",
  "data": {
    "database_connected": true,
    "ml_models_loaded": true,
    "sensors_active": 5
  }
}
```

#### **Sensor Data**
```http
GET /api/sensors/data?limit=10&sensor_type=emotion
```
**Parameters:**
- `limit` (optional): Number of records (default: 100)
- `sensor_type` (optional): Filter by sensor type

**Response:**
```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "id": 1,
      "sensor_type": "emotion",
      "sensor_value": 0.85,
      "emotion_type": "joy",
      "confidence": 0.92,
      "timestamp": "2025-11-25T21:00:00Z",
      "location": "entrance"
    }
  ]
}
```

#### **Sensor Statistics**
```http
GET /api/sensors/stats
```
**Response:**
```json
{
  "success": true,
  "data": {
    "total_readings": 15420,
    "sensor_types": {
      "emotion": 3084,
      "temperature": 3084,
      "humidity": 3084,
      "motion": 3084,
      "light": 3084
    },
    "latest_reading": "2025-11-25T21:00:00Z",
    "average_values": {
      "temperature": 22.5,
      "humidity": 45.2,
      "motion": 0.67
    }
  }
}
```

#### **ML Predictions**
```http
GET /api/ml/predictions/current
```
**Response:**
```json
{
  "success": true,
  "data": {
    "engagement_score": 0.73,
    "dominant_emotion": "joy",
    "emotion_confidence": 0.88,
    "environmental_comfort": 0.82,
    "recommendation": "Optimal conditions for customer interaction"
  }
}
```

#### **ML Model Status**
```http
GET /api/ml/model-status
```
**Response:**
```json
{
  "success": true,
  "data": {
    "engagement_model": {
      "loaded": true,
      "accuracy": 0.87,
      "last_training": "2025-11-25T20:00:00Z"
    },
    "emotion_model": {
      "loaded": true,
      "accuracy": 0.91,
      "last_training": "2025-11-25T20:00:00Z"
    }
  }
}
```

### **WebSocket Endpoints**

#### **Real-time Sensor Data**
```
ws://localhost:8000/ws/sensors
```
**Message Format:**
```json
{
  "type": "sensor_update",
  "data": {
    "sensor_type": "emotion",
    "value": 0.85,
    "timestamp": "2025-11-25T21:00:00Z"
  }
}
```

#### **Real-time ML Predictions**
```
ws://localhost:8000/ws/predictions
```
**Message Format:**
```json
{
  "type": "prediction_update",
  "data": {
    "engagement_score": 0.73,
    "emotion": "joy",
    "timestamp": "2025-11-25T21:00:00Z"
  }
}
```

---

## 📊 **Database Schema**

### **Sensors Table**
```sql
CREATE TABLE sensors (
    id NUMBER PRIMARY KEY,
    sensor_type VARCHAR2(50) NOT NULL,
    sensor_value NUMBER(10,6) NOT NULL,
    emotion_type VARCHAR2(20),
    confidence NUMBER(5,4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR2(100)
);
```

### **ML Predictions Table**
```sql
CREATE TABLE ml_predictions (
    id NUMBER PRIMARY KEY,
    engagement_score NUMBER(5,4) NOT NULL,
    dominant_emotion VARCHAR2(20),
    emotion_confidence NUMBER(5,4),
    environmental_comfort NUMBER(5,4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR2(20)
);
```

---

## 🚀 **Deployment Guide**

### **Development Environment Setup**

#### **Prerequisites**
```bash
# System requirements
- Python 3.9+
- Oracle Instant Client
- Git
- 4GB+ RAM
- 2GB+ disk space
```

#### **Installation Steps**
```bash
# 1. Clone repository
git clone [repository-url]
cd aurora-totem-mvp

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup Oracle environment
./scripts/setup_oracle_env.sh

# 5. Configure environment variables
cp .env.example .env
# Edit .env with your Oracle FIAP credentials

# 6. Start system
./scripts/run_aurora.sh start
```

### **Production Deployment**

#### **Docker Containerization**
```dockerfile
FROM python:3.13-slim

# Install Oracle Instant Client
RUN apt-get update && apt-get install -y \
    libaio1 \
    wget \
    unzip

# Install Oracle Instant Client
WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip
RUN unzip instantclient-basiclite-linuxx64.zip

# Set Oracle environment
ENV LD_LIBRARY_PATH="/opt/oracle/instantclient_21_9:$LD_LIBRARY_PATH"

# Copy application
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose ports
EXPOSE 8000 8501

# Start application
CMD ["./scripts/run_aurora.sh", "start"]
```

#### **Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aurora-totem
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aurora-totem
  template:
    metadata:
      labels:
        app: aurora-totem
    spec:
      containers:
      - name: api
        image: aurora-totem:latest
        ports:
        - containerPort: 8000
        env:
        - name: ORACLE_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: aurora-secrets
              key: oracle-connection
---
apiVersion: v1
kind: Service
metadata:
  name: aurora-totem-service
spec:
  selector:
    app: aurora-totem
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### **Cloud Platform Deployment**

#### **AWS Deployment**
```bash
# Using AWS ECS with Fargate
aws ecs create-cluster --cluster-name aurora-totem
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cluster aurora-totem --service-name aurora-api --task-definition aurora-totem:1
```

#### **Azure Deployment**
```bash
# Using Azure Container Instances
az container create \
  --resource-group aurora-rg \
  --name aurora-totem \
  --image aurora-totem:latest \
  --ports 8000 8501 \
  --environment-variables ORACLE_CONNECTION_STRING=$ORACLE_CONN
```

#### **GCP Deployment**
```bash
# Using Google Cloud Run
gcloud run deploy aurora-totem \
  --image gcr.io/PROJECT-ID/aurora-totem \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database Configuration
ORACLE_HOST=oracle.fiap.com.br
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=ORCL
ORACLE_USERNAME=your_username
ORACLE_PASSWORD=your_password

# API Configuration  
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# ML Configuration
ML_MODEL_PATH=./models/
ENABLE_ML_TRAINING=True
MODEL_UPDATE_INTERVAL=3600

# Dashboard Configuration
DASHBOARD_PORT=8501
ENABLE_DASHBOARD=True
UPDATE_FREQUENCY=1000
```

### **Performance Tuning**
```python
# FastAPI settings
app = FastAPI(
    title="Aurora Totem API",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None
)

# Database connection pooling
POOL_SIZE = 10
MAX_OVERFLOW = 20
POOL_TIMEOUT = 30

# WebSocket settings
MAX_CONNECTIONS = 100
HEARTBEAT_INTERVAL = 30
```

---

## 🛡️ **Security Considerations**

### **Authentication & Authorization**
```python
# JWT token implementation
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.get("/api/secure-endpoint")
async def secure_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Token validation logic
    pass
```

### **Data Privacy**
- **Emotion data encryption** at rest and in transit
- **GDPR compliance** with data retention policies
- **Anonymization** of personal identifiers
- **Audit logging** for all data access

### **Network Security**
- **HTTPS only** in production
- **CORS configuration** for web dashboard
- **Rate limiting** on API endpoints
- **Input validation** and sanitization

---

## 📈 **Monitoring & Observability**

### **Application Metrics**
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')
SENSOR_READINGS = Gauge('sensor_readings_current', 'Current sensor readings')
```

### **Health Checks**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_database(),
        "models": await check_ml_models(),
        "sensors": await check_sensors()
    }
```

### **Logging Configuration**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aurora.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🧪 **Testing Strategy**

### **Unit Tests**
```python
# Model testing
def test_engagement_prediction():
    model = EngagementModel()
    result = model.predict(sample_features)
    assert 0 <= result <= 1
```

### **Integration Tests**
```python
# API testing
@pytest.mark.asyncio
async def test_sensor_endpoint():
    response = await client.get("/api/sensors/data")
    assert response.status_code == 200
    assert "data" in response.json()
```

### **Load Testing**
```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/sensors/data

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/
```

---

## 📋 **Maintenance & Operations**

### **Backup Procedures**
```sql
-- Database backup
EXPORT FULL=Y FILE=aurora_backup.dmp

-- Model backup
tar -czf models_backup.tar.gz models/
```

### **Update Procedures**
```bash
# Application updates
git pull origin main
pip install -r requirements.txt
./scripts/run_aurora.sh restart
```

### **Troubleshooting Guide**
```bash
# Check system status
./scripts/run_aurora.sh status

# View logs
tail -f logs/aurora.log

# Test connectivity
python3 tests/quick_system_test.py

# Database connection test
python3 -c "from src.database import DatabaseManager; print(DatabaseManager().test_connection())"
```

---

**This comprehensive technical documentation provides everything needed for successful deployment, operation, and maintenance of Aurora Totem MVP! 🌟**