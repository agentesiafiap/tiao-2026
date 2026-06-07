# 📁 Aurora Totem MVP - Project Structure

## 🏗️ **Organized Folder Structure**

```
aurora-totem-mvp/
├── 📁 src/                     # Source code (main application)
│   ├── __init__.py
│   ├── config.py               # Configuration settings
│   ├── database.py             # Oracle FIAP database manager
│   ├── main.py                 # FastAPI application
│   ├── ml_model.py             # Machine Learning models
│   ├── sensor_simulator.py     # IoT sensor simulation
│   └── dashboard.py            # Streamlit dashboard
│
├── 📁 tests/                   # Test suites
│   ├── __init__.py
│   ├── test_system_integration.py   # Complete system tests
│   ├── test_ml_frontend.py          # ML frontend tests
│   ├── test_websockets.py           # WebSocket tests
│   └── websocket_test.py            # WebSocket client test
│
├── 📁 scripts/                 # Utility scripts
│   ├── run_aurora.sh           # Main system startup script
│   └── setup_oracle_env.sh     # Oracle environment setup
│
├── 📁 docs/                    # Documentation
│   ├── QUICK_START.md          # Quick start guide
│   └── TASK8_SYSTEM_TESTING_REPORT.md  # System testing report
│
├── 📁 models/                  # ML model files (auto-generated)
│   └── *.pkl                   # Trained model files
│
├── 📁 logs/                    # Application logs
│   ├── fastapi.log             # API server logs
│   └── streamlit.log           # Dashboard logs
│
├── 📁 reports/                 # Test reports and results
│   └── *.json                  # Test result files
│
├── 📄 run_api.py               # API entry point
├── 📄 run_dashboard.py         # Dashboard entry point
├── 📄 requirements.txt         # Python dependencies
├── 📄 README.md               # Main documentation
├── 📄 .env                    # Environment variables
└── 📁 .venv/                  # Python virtual environment
```

## 🚀 **Running the Application**

### **Option 1: Complete System (Recommended)**
```bash
# From project root
./scripts/run_aurora.sh start
```

### **Option 2: Individual Components**
```bash
# API Server only
python3 run_api.py

# Dashboard only  
python3 run_dashboard.py
```

### **Option 3: Development Mode**
```bash
# From src/ directory for development
cd src/
python3 main.py                    # API
streamlit run dashboard.py         # Dashboard
```

## 🧪 **Running Tests**

```bash
# All tests
python3 -m pytest tests/

# Specific test suite
python3 tests/test_system_integration.py
python3 tests/quick_system_test.py

# WebSocket tests
python3 tests/test_websockets.py
```

## 📊 **Project Benefits**

### **✅ Organized Structure:**
- **Clear separation** of concerns
- **Easy maintenance** and debugging
- **Professional development** standards
- **Scalable architecture** for future expansion

### **✅ Improved Development:**
- **Modular imports** with proper package structure  
- **Test isolation** in dedicated directory
- **Documentation centralization** in docs/
- **Clean separation** of scripts and utilities

### **✅ Deployment Ready:**
- **Production-ready** folder structure
- **Easy Docker containerization** (future)
- **CI/CD pipeline ready** structure
- **Version control friendly** organization

## 🔧 **Key Changes Made:**

1. **Source Code**: Moved to `src/` package with proper imports
2. **Testing**: Centralized in `tests/` with updated paths
3. **Documentation**: Organized in `docs/` folder
4. **Scripts**: Utility scripts in `scripts/` directory
5. **Entry Points**: Created `run_api.py` and `run_dashboard.py` for easy execution
6. **Logging**: Separated logs in `logs/` directory
7. **Reports**: Test results in dedicated `reports/` folder

This structure follows Python packaging best practices and makes the Aurora Totem project production-ready! 🌟