#!/usr/bin/env python3
"""
Launcher script for Dr. Resume Application
Run this from the root directory to start the application
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add backend directory to Python path
backend_dir = os.path.join(current_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Change to the backend directory for proper imports
os.chdir(backend_dir)

# Import and run the app
try:
    from app import main
    if __name__ == '__main__':
        main()
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("🔧 Trying to run app.py directly...")

    # Try to run the app directly
    import subprocess
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except Exception as e2:
        print(f"❌ Failed to run app.py: {e2}")
        print("📍 Please run: python backend/app.py")
