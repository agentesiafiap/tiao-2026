# 🚀 Aurora Totem MVP - Quick Start Guide

**Complete system startup in 3 minutes** | Sistema completo em 3 minutos

---

## 📋 **Prerequisites**

```bash
# Verify Python 3.8+
python3 --version

# Verify Oracle Instant Client (ARM64 macOS)
ls -la /opt/homebrew/lib/libclntsh.dylib
```

**If Oracle client missing:**
```bash
brew install instantclient-arm64-basic
```

### **🔧 Environment Configuration**

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your credentials
# Replace YOUR_RM_NUMBER with your FIAP RM (e.g., RM567686)
# Replace YOUR_PASSWORD with your Oracle FIAP password
nano .env  # or use your preferred editor
```

**⚠️ Important:** Never commit the `.env` file to version control - it contains your personal credentials!

---

## 🎯 **Quick Start (Recommended)**

### **Option 1: Automated Script**
```bash
# Clone and enter project directory
cd aurora-totem-mvp

# Set Oracle environment and start everything
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
export ORACLE_HOME=/opt/homebrew/lib
./run_aurora.sh start

# ✅ System will auto-start:
# • FastAPI at http://localhost:8000
# • Dashboard at http://localhost:8501
```

### **Option 2: Manual Background Startup**
```bash
# 1. Set Oracle environment
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
export ORACLE_HOME=/opt/homebrew/lib

# 2. Start FastAPI backend
nohup python3 main.py > fastapi.log 2>&1 &

# 3. Start Streamlit dashboard
nohup streamlit run dashboard.py --server.port 8501 > streamlit.log 2>&1 &

# 4. Wait for startup (30 seconds)
sleep 30
```

---

## 🌐 **Access System**

| Component | URL | Description |
|-----------|-----|-------------|
| **📊 Main Dashboard** | http://localhost:8501 | ML-integrated Streamlit interface |
| **🌐 API Server** | http://localhost:8000 | REST + WebSocket endpoints |
| **📚 API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |

---

## 🧪 **System Validation**

```bash
# Check API status
curl http://localhost:8000/

# Check database stats  
curl http://localhost:8000/api/sensors/stats

# Train ML models (if needed)
curl -X POST http://localhost:8000/api/ml/train-models

# Check ML model status
curl http://localhost:8000/api/ml/model-status
```

**Expected Response:**
```json
{
  "success": true,
  "database_connected": true,
  "ml_models_ready": true
}
```

---

## 📊 **System Components**

### **✅ What Starts Automatically:**
- **Oracle FIAP Database**: Real-time connection and data storage
- **IoT Sensor Simulation**: 5 sensor types generating realistic data every 5s
- **FastAPI Backend**: 15 REST endpoints + 2 WebSocket channels
- **ML Engine**: Engagement & emotion prediction models
- **Streamlit Dashboard**: Real-time visualizations with ML integration

### **🔄 Real-time Data Flow:**
```
📡 Sensors → 🗄️ Oracle FIAP → 🌐 API → 📊 Dashboard
              ↓
         🤖 ML Models → 📈 Predictions
```

---

## 🎛️ **System Management**

### **Check Status:**
```bash
# Using Aurora script
./run_aurora.sh status

# Manual check
ps aux | grep -E "(main.py|streamlit)" | grep -v grep
curl -s http://localhost:8000/ > /dev/null && echo "✅ API Running" || echo "❌ API Down"
```

### **Stop System:**
```bash
# Using Aurora script
./run_aurora.sh stop

# Manual stop
pkill -f "main.py"
pkill -f "streamlit"
```

### **Restart System:**
```bash
./run_aurora.sh restart
```

### **View Logs:**
```bash
# API logs
tail -f fastapi.log

# Dashboard logs  
tail -f streamlit.log

# Real-time system status
watch -n 2 'curl -s http://localhost:8000/api/sensors/stats'
```

---

## 🤖 **ML Model Management**

### **Train Models:**
```bash
curl -X POST "http://localhost:8000/api/ml/train-models"
```

### **Test Predictions:**
```bash
# Engagement prediction
curl -X POST "http://localhost:8000/api/ml/predict-engagement" \
  -H "Content-Type: application/json" \
  -d '{"sensor_data": {"heart_rate": 75, "skin_conductance": 6.2, "eye_tracking": 0.8}}'

# Emotion prediction  
curl -X POST "http://localhost:8000/api/ml/predict-emotion" \
  -H "Content-Type: application/json" \
  -d '{"sensor_data": {"heart_rate": 85, "face_emotion": 0.8, "voice_emotion": 0.7}}'
```

---

## 🐛 **Troubleshooting**

### **Common Issues:**

#### **❌ Oracle Client Error:**
```bash
# Install Oracle client
brew install instantclient-arm64-basic

# Set environment variables
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
export ORACLE_HOME=/opt/homebrew/lib
```

#### **❌ Port Already in Use:**
```bash
# Find and kill process using port
lsof -ti:8000 | xargs kill -9  # FastAPI
lsof -ti:8501 | xargs kill -9  # Streamlit
```

#### **❌ Dependencies Missing:**
```bash
pip install -r requirements.txt
```

#### **❌ ML Models Not Loading:**
```bash
# Delete old models and retrain
rm -rf models/
curl -X POST "http://localhost:8000/api/ml/train-models"
```

### **Fallback Mode:**
If Oracle FIAP is unavailable, the system automatically uses **in-memory storage** and continues functioning with full ML capabilities.

---

## 📈 **Performance Monitoring**

### **Key Metrics:**
```bash
# Database records
curl -s "http://localhost:8000/api/sensors/stats" | jq '.total_records'

# System health
curl -s "http://localhost:8000/" | jq '.success'

# ML model status
curl -s "http://localhost:8000/api/ml/model-status" | jq '.models_ready'
```

### **Expected Performance:**
- **API Response Time**: <100ms
- **Dashboard Refresh**: 5-60s (configurable)
- **Sensor Data Rate**: 5 sensors × 5s intervals
- **ML Prediction Time**: <200ms
- **Database Write Speed**: ~50 records/minute

---

## 🎯 **Feature Highlights**

### **📊 Dashboard Features:**
- ✅ Real-time sensor charts (temperature, humidity, light, sound, emotion)
- ✅ ML prediction gauges (engagement levels)
- ✅ Emotion distribution analytics
- ✅ Feature importance visualization
- ✅ System metrics and connection status
- ✅ Interactive controls and parameters

### **🌐 API Features:**
- ✅ 15 REST endpoints (CRUD + analytics)
- ✅ 4 ML endpoints (train, predict, status)
- ✅ 2 WebSocket channels (real-time streaming)
- ✅ Automatic data validation and error handling
- ✅ Oracle FIAP integration with fallback mode

### **🤖 ML Features:**
- ✅ Engagement prediction (high/medium/low)
- ✅ Emotion classification (happy/neutral/sad/surprised)
- ✅ Model persistence (survives system restarts)
- ✅ Auto-training with synthetic data
- ✅ Real-time prediction pipeline

---

## 📞 **Support Information**

**Project**: Aurora Totem MVP - Challenge FlexMedia FIAP  
**Course**: TIAOS (Tecnologia em IA e Ciência de Dados)  
**Group**: 36  
**Database**: Oracle FIAP (RM567686)  
**Status**: 78% Complete (Tasks 1-7 implemented)

---

## 🏁 **Success Checklist**

After startup, verify these are working:

- [ ] **API Health Check**: `curl http://localhost:8000/` returns `{"success": true}`
- [ ] **Dashboard Loading**: Browser opens http://localhost:8501 successfully  
- [ ] **Oracle Connection**: API logs show `✅ Conectado ao Oracle FIAP`
- [ ] **Sensor Data**: `curl http://localhost:8000/api/sensors/stats` shows records > 0
- [ ] **ML Models**: `curl http://localhost:8000/api/ml/model-status` shows `models_ready: true`
- [ ] **Real-time Updates**: Dashboard shows live data updates every 5-10 seconds

**🎉 If all checkmarks pass: Aurora Totem system is fully operational!**

---

*Generated on 25 de Novembro de 2025 | Aurora Totem MVP - Production Ready*