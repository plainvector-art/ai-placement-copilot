"""
Unified launcher for AI Interview & Placement Copilot.
Starts both FastAPI backend and Streamlit frontend.
"""
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).parent


def start_backend():
    """Start FastAPI backend server."""
    print("🚀 Starting FastAPI backend on http://localhost:8000 ...")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=str(ROOT),
    )


def start_frontend():
    """Start Streamlit frontend."""
    time.sleep(2)  # Wait for backend to initialize
    print("🎨 Starting Streamlit frontend on http://localhost:8501 ...")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run",
         str(ROOT / "frontend" / "app.py"),
         "--server.port", "8501",
         "--server.address", "localhost",
         "--theme.base", "dark",
         "--theme.primaryColor", "#8b5cf6",
         "--theme.backgroundColor", "#0a0a0f",
         "--theme.secondaryBackgroundColor", "#111118",
         "--theme.textColor", "#f0f0f5",
         ],
        cwd=str(ROOT),
    )


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"

    print("\n" + "═" * 60)
    print("  🎯 AI Interview & Placement Copilot")
    print("═" * 60)

    if mode == "backend":
        start_backend()
    elif mode == "frontend":
        start_frontend()
    else:
        # Run both concurrently
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        start_frontend()  # This blocks until Streamlit exits
