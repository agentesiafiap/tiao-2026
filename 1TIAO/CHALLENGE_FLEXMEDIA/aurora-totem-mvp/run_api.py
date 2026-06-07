#!/usr/bin/env python3
"""
Aurora Totem MVP - Main Application Entry Point
Run from project root directory
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from src.main import app
    import uvicorn
    
    # Run FastAPI server
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )