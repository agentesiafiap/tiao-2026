# 🎯 **Aurora Totem MVP - Demo Execution Guide**
**Step-by-Step Live Demonstration Instructions**

---

## 🚀 **Pre-Demo Setup (5 minutes)**

### **Environment Preparation**
```bash
# 1. Navigate to project directory
cd /Users/danielbaiao/Documents/challenge-flexmedia/cursotiaos-challenge-ano1-flexmedia/aurora-totem-mvp

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Verify system status
echo "🔍 Verifying system readiness..."
python3 -c "import fastapi, streamlit, sklearn; print('✅ Dependencies OK')"
```

### **Pre-flight Checks**
```bash
# 4. Check Oracle connection
python3 -c "
from src.database import DatabaseManager
db = DatabaseManager()
try:
    db.test_connection()
    print('✅ Oracle FIAP Connected')
except Exception as e:
    print(f'❌ Database Error: {e}')
"

# 5. Verify ports are available
lsof -ti:8000 && echo "⚠️ Port 8000 occupied" || echo "✅ Port 8000 available"
lsof -ti:8501 && echo "⚠️ Port 8501 occupied" || echo "✅ Port 8501 available"
```

### **Demo Environment Setup**
```bash
# 6. Clear any existing logs
> logs/fastapi.log
> logs/streamlit.log

# 7. Prepare demonstration windows
# Terminal 1: System startup and monitoring
# Terminal 2: Live API testing
# Browser 1: Dashboard (http://localhost:8501)
# Browser 2: API docs (http://localhost:8000/docs)
```

---

## 🎬 **Demo Execution Steps**

### **Phase 1: System Startup (2 minutes)**

#### **Step 1: Launch Aurora Totem**
```bash
# In Terminal 1
echo "🚀 Starting Aurora Totem MVP System..."
./scripts/run_aurora.sh start
```

**Expected Output:**
```
🚀 Starting Aurora Totem MVP System...
📁 Project directory: /Users/.../aurora-totem-mvp
✅ Python dependencies verified
🗄️ Oracle FIAP database connection: OK
🤖 ML models loaded successfully
📡 Starting sensor simulation...
🌐 FastAPI server starting on http://localhost:8000
📊 Streamlit dashboard starting on http://localhost:8501
✅ System startup complete!
```

#### **Step 2: Verify System Health**
```bash
# In Terminal 2
echo "🔍 System Health Check..."
curl -s http://localhost:8000/ | python3 -m json.tool
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Aurora Totem MVP API",
  "timestamp": "2025-11-25T21:00:00Z",
  "data": {
    "database_connected": true,
    "ml_models_loaded": true,
    "sensors_active": 5,
    "version": "1.0.0"
  }
}
```

### **Phase 2: Live Dashboard Demo (3 minutes)**

#### **Step 3: Open Dashboard**
```bash
# Navigate browser to: http://localhost:8501
# Or run: open http://localhost:8501
```

**Demonstrate:**
1. **Real-time Sensor Data** - Show live updating charts
2. **Emotion Detection** - Point out emotion classifications  
3. **Environmental Monitoring** - Temperature, humidity, motion
4. **ML Predictions** - Engagement scores and recommendations
5. **Historical Trends** - Data patterns over time

#### **Step 4: API Documentation**
```bash
# Navigate browser to: http://localhost:8000/docs
# Or run: open http://localhost:8000/docs
```

**Show:**
- **Interactive API docs** - Swagger UI interface
- **15 endpoints** - Complete API surface
- **WebSocket connections** - Real-time streaming
- **Data models** - Request/response schemas

### **Phase 3: Live API Demonstration (4 minutes)**

#### **Step 5: Sensor Data Retrieval**
```bash
# Get latest sensor readings
echo "📡 Latest Sensor Data:"
curl -s "http://localhost:8000/api/sensors/data?limit=5" | python3 -m json.tool
```

**Expected Output:**
```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": 1245,
      "sensor_type": "emotion",
      "sensor_value": 0.87,
      "emotion_type": "joy",
      "confidence": 0.93,
      "timestamp": "2025-11-25T21:00:15Z",
      "location": "entrance"
    },
    {
      "id": 1246,
      "sensor_type": "temperature", 
      "sensor_value": 22.5,
      "timestamp": "2025-11-25T21:00:15Z"
    }
  ]
}
```

#### **Step 6: Sensor Statistics**
```bash
# Get comprehensive sensor stats
echo "📊 Sensor Statistics:"
curl -s http://localhost:8000/api/sensors/stats | python3 -m json.tool
```

#### **Step 7: ML Predictions**
```bash
# Get current ML predictions
echo "🤖 ML Predictions:"
curl -s http://localhost:8000/api/ml/predictions/current | python3 -m json.tool
```

**Expected Output:**
```json
{
  "success": true,
  "data": {
    "engagement_score": 0.78,
    "dominant_emotion": "joy",
    "emotion_confidence": 0.91,
    "environmental_comfort": 0.85,
    "recommendation": "Optimal conditions - high engagement potential",
    "prediction_timestamp": "2025-11-25T21:00:20Z"
  }
}
```

#### **Step 8: Model Status**
```bash
# Check ML model health
echo "🧠 ML Model Status:"
curl -s http://localhost:8000/api/ml/model-status | python3 -m json.tool
```

### **Phase 4: Real-time WebSocket Demo (2 minutes)**

#### **Step 9: WebSocket Testing**
```bash
# Test WebSocket connection (in new terminal)
python3 tests/websocket_test.py
```

**Show:** Live streaming data updates in terminal

#### **Step 10: Database Integration**
```bash
# Show database connectivity and data persistence
echo "🗄️ Database Integration:"
curl -s http://localhost:8000/api/database/health | python3 -m json.tool
```

### **Phase 5: System Testing (3 minutes)**

#### **Step 11: Comprehensive System Test**
```bash
# Run complete system validation
echo "🧪 Running System Tests..."
python3 tests/quick_system_test.py
```

**Expected Output:**
```
🚀 Aurora Totem - Quick System Test
==================================================

1️⃣ Testing API Health...
   ✅ API Status: True
   📊 Database Connected: True

2️⃣ Testing Database Connection...
   ✅ Database accessible: 15420 total readings

3️⃣ Testing Sensor Data Endpoints...
   ✅ Sensor data retrieved: 3 records

4️⃣ Testing ML Models...
   ✅ ML models operational: engagement=0.78, emotion=joy

5️⃣ Testing End-to-End Data Flow...
   ✅ Complete data pipeline functional

6️⃣ Testing System Performance...
   ✅ Response time: 45ms (excellent)

==================================================
🎯 Success Rate: 100.0% (6/6 tests passed)
🎉 Overall Status: ✅ SYSTEM HEALTHY
```

#### **Step 12: Performance Metrics**
```bash
# Show system performance
echo "⚡ Performance Metrics:"
curl -s http://localhost:8000/api/system/metrics | python3 -m json.tool
```

---

## 🎭 **Presentation Talking Points**

### **During Startup (Steps 1-2):**
> "Aurora Totem starts up in under 30 seconds, automatically connecting to Oracle FIAP database, loading ML models, and beginning real-time sensor simulation. This represents a production-ready system that could be deployed in retail stores, museums, or corporate spaces immediately."

### **Dashboard Demo (Steps 3-4):**
> "The dashboard provides business stakeholders with instant insights - emotion trends, environmental conditions, and engagement predictions. This level of analytics typically requires expensive third-party solutions, but Aurora provides it natively with real-time updates."

### **API Demonstration (Steps 5-8):**
> "Our REST API provides 15 endpoints covering every aspect of the system. Notice the clean JSON responses, proper error handling, and comprehensive data models. The ML predictions show 78% engagement likelihood - actionable intelligence for optimizing customer experiences."

### **WebSocket Demo (Step 9):**
> "Real-time data streams via WebSockets enable instant dashboard updates and live monitoring. This supports applications like dynamic content adjustment based on crowd emotion or environmental optimization in real-time."

### **System Testing (Steps 11-12):**
> "Aurora Totem includes comprehensive testing achieving 100% success rate in this demo. The system processes requests in under 50ms and maintains enterprise-grade reliability suitable for production deployment."

---

## 🛠️ **Troubleshooting Guide**

### **Common Issues & Solutions**

#### **Port Already in Use**
```bash
# Kill processes on ports 8000 and 8501
kill $(lsof -ti:8000)
kill $(lsof -ti:8501)
# Then restart system
./scripts/run_aurora.sh restart
```

#### **Oracle Connection Failed**
```bash
# Test Oracle connectivity
python3 -c "
import cx_Oracle
try:
    conn = cx_Oracle.connect('rm99519/150905@oracle.fiap.com.br:1521/orcl')
    print('✅ Oracle connection OK')
    conn.close()
except Exception as e:
    print(f'❌ Oracle error: {e}')
"
```

#### **Dependencies Missing**
```bash
# Reinstall requirements
pip install -r requirements.txt

# Verify key packages
python3 -c "import fastapi, streamlit, sklearn, cx_Oracle; print('✅ All dependencies OK')"
```

#### **Dashboard Not Loading**
```bash
# Check Streamlit process
ps aux | grep streamlit

# Restart dashboard only
streamlit run src/dashboard.py --server.port 8501
```

#### **API Returning Errors**
```bash
# Check API logs
tail -f logs/fastapi.log

# Test basic endpoint
curl http://localhost:8000/health
```

### **Performance Optimization**
```bash
# Check system resources
htop  # or top on Linux/macOS
df -h  # disk space
free -m  # memory (Linux) or vm_stat (macOS)
```

---

## 📊 **Demo Success Metrics**

### **Technical Indicators:**
- [ ] **System startup** < 45 seconds
- [ ] **API response time** < 100ms  
- [ ] **Dashboard loads** within 10 seconds
- [ ] **WebSocket streams** updating smoothly
- [ ] **Database queries** executing successfully
- [ ] **ML predictions** generating correctly

### **Business Value Demonstrated:**
- [ ] **Real-time emotion detection** visible
- [ ] **Environmental monitoring** active
- [ ] **Engagement predictions** accurate
- [ ] **Business insights** clearly presented
- [ ] **Scalability potential** communicated
- [ ] **ROI justification** explained

### **Audience Engagement:**
- [ ] **Technical complexity** appropriately explained
- [ ] **Business benefits** clearly articulated  
- [ ] **Live system** demonstrating reliability
- [ ] **Questions** addressed confidently
- [ ] **Next steps** clearly outlined

---

## 🎯 **Post-Demo Actions**

### **System Cleanup**
```bash
# Graceful shutdown
./scripts/run_aurora.sh stop

# Archive demo logs
mkdir -p demo_logs/$(date +%Y%m%d_%H%M%S)
cp logs/* demo_logs/$(date +%Y%m%d_%H%M%S)/

# Reset for next demo
> logs/fastapi.log
> logs/streamlit.log
```

### **Feedback Collection**
```bash
# Create demo feedback file
echo "# Aurora Totem Demo - $(date)" > demo_feedback.md
echo "## Technical Performance:" >> demo_feedback.md
echo "- System startup time: [X] seconds" >> demo_feedback.md
echo "- API response time: [X] ms" >> demo_feedback.md
echo "- Issues encountered: [None/Details]" >> demo_feedback.md
echo "" >> demo_feedback.md
echo "## Audience Feedback:" >> demo_feedback.md
echo "- Questions asked: " >> demo_feedback.md
echo "- Interest level: " >> demo_feedback.md  
echo "- Suggested improvements: " >> demo_feedback.md
```

### **Documentation Updates**
- [ ] Update demo script based on feedback
- [ ] Record actual performance metrics
- [ ] Note any issues for future resolution
- [ ] Update troubleshooting guide if needed

---

**This comprehensive execution guide ensures successful, professional demonstration of Aurora Totem MVP's complete capabilities! 🌟**