#!/usr/bin/env python3
"""
Aurora Totem MVP - Dashboard Entry Point
Run from project root directory
"""

import sys
import os
import subprocess

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    # Run Streamlit dashboard
    dashboard_path = os.path.join(os.path.dirname(__file__), 'src', 'dashboard.py')
    
    cmd = [
        sys.executable, 
        "-m", "streamlit", 
        "run", 
        dashboard_path,
        "--server.port", "8501",
        "--server.address", "localhost"
    ]
    
    subprocess.run(cmd)