#!/bin/bash
# Aurora Totem MVP - Quick Start Script
# Executes the complete system with proper paths

echo "🤖 Aurora Totem MVP - Quick Start"
echo "=================================="

# Global variables for process IDs
FASTAPI_PID=""
STREAMLIT_PID=""

# Trap function to handle Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Stopping Aurora Totem services..."
    if [ ! -z "$FASTAPI_PID" ] && kill -0 "$FASTAPI_PID" 2>/dev/null; then
        kill "$FASTAPI_PID" && echo "✅ FastAPI server stopped"
    fi
    if [ ! -z "$STREAMLIT_PID" ] && kill -0 "$STREAMLIT_PID" 2>/dev/null; then
        kill "$STREAMLIT_PID" && echo "✅ Streamlit dashboard stopped"
    fi
    # Force kill anything on our ports as backup
    lsof -ti:8000,8501 2>/dev/null | xargs kill -9 2>/dev/null || true
    echo "🏁 All services stopped"
    exit 0
}

# Set trap for Ctrl+C
trap cleanup SIGINT SIGTERM

# Get the project root directory (parent of scripts directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
echo "📁 Project directory: $PROJECT_DIR"

# Check if we're in the right directory
if [ ! -f "$PROJECT_DIR/src/main.py" ]; then
    echo "❌ Error: src/main.py not found in $PROJECT_DIR"
    echo "💡 Make sure this script is in the aurora-totem-mvp/scripts directory"
    exit 1
fi

# Check Python dependencies
echo "🔍 Checking dependencies..."
python3 -c "import fastapi, streamlit, cx_Oracle, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip3 install -r "$PROJECT_DIR/requirements.txt"
fi

# Function to start FastAPI server
start_fastapi() {
    echo "🚀 Starting FastAPI server..."
    cd "$PROJECT_DIR"
    python3 "$PROJECT_DIR/run_api.py" &
    FASTAPI_PID=$!
    echo "📡 FastAPI PID: $FASTAPI_PID"
    
    # Wait for server to start
    echo "⏳ Waiting for API server to start..."
    for i in {1..10}; do
        if curl -s http://localhost:8000/ > /dev/null 2>&1; then
            echo "✅ FastAPI server is running at http://localhost:8000"
            break
        fi
        sleep 2
        echo "   Attempt $i/10..."
    done
}

# Function to start Streamlit dashboard  
start_streamlit() {
    echo "📊 Starting Streamlit dashboard..."
    cd "$PROJECT_DIR"
    python3 "$PROJECT_DIR/run_dashboard.py" &
    STREAMLIT_PID=$!
    echo "📈 Streamlit PID: $STREAMLIT_PID"
    
    # Wait for dashboard to start
    echo "⏳ Waiting for dashboard to start..."
    sleep 3
    echo "✅ Streamlit dashboard should be at http://localhost:8501"
}

# Function to check system status
check_status() {
    echo ""
    echo "🔍 System Status Check:"
    echo "======================"
    
    # Check FastAPI
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ FastAPI Server: Running (http://localhost:8000)"
    else
        echo "❌ FastAPI Server: Not responding"
    fi
    
    # Check Streamlit (just check if process exists)
    if pgrep -f "streamlit.*dashboard.py" > /dev/null 2>&1; then
        echo "✅ Streamlit Dashboard: Running (http://localhost:8501)"
    else
        echo "❌ Streamlit Dashboard: Not running"
    fi
    
    # Check Oracle connection
    python3 -c "
from database import DatabaseManager
try:
    db = DatabaseManager()
    if db.connect():
        print('✅ Oracle FIAP: Connected')
        db.connection.close()
    else:
        print('❌ Oracle FIAP: Connection failed')
except Exception as e:
    print(f'❌ Oracle FIAP: Error - {str(e)}')
" 2>/dev/null
}

# Main execution
case "${1:-start}" in
    "start")
        echo "🚀 Starting complete Aurora Totem system..."
        start_fastapi
        sleep 3
        start_streamlit
        sleep 2
        check_status
        
        echo ""
        echo "🎉 Aurora Totem MVP is ready!"
        echo "=============================="
        echo "🌐 API Server:     http://localhost:8000"
        echo "📊 Dashboard:      http://localhost:8501"  
        echo "📚 API Docs:       http://localhost:8000/docs"
        echo ""
        echo "💡 To stop services: Ctrl+C or ./run_aurora.sh stop"
        echo "📋 To check status:  ./run_aurora.sh status"
        echo ""
        echo "Press Ctrl+C to stop all services..."
        
        # Wait for background processes and handle Ctrl+C
        wait
        ;;
        
    "stop")
        echo "🛑 Stopping Aurora Totem services..."
        
        # Kill FastAPI processes
        pkill -f "run_api.py\|uvicorn" 2>/dev/null && echo "✅ FastAPI server stopped" || echo "  Stopping..."
        
        # Kill Streamlit processes
        pkill -f "run_dashboard.py\|streamlit.*dashboard.py" 2>/dev/null && echo "✅ Streamlit dashboard stopped" || echo "  Stopping..."
        
        # Force kill anything on our ports as backup
        lsof -ti:8000,8501 2>/dev/null | xargs kill -9 2>/dev/null || true
        
        echo "🏁 All services stopped"
        ;;
        
    "status")
        check_status
        ;;
        
    "restart")
        echo "🔄 Restarting Aurora Totem..."
        $0 stop
        sleep 2  
        $0 start
        ;;
        
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start FastAPI + Streamlit (default)"
        echo "  stop    - Stop all services"
        echo "  status  - Check system status"
        echo "  restart - Restart all services"
        exit 1
        ;;
esac