"""
start.py — Unified launcher for Render deployment.
Starts both FastAPI (port from $PORT env) and Streamlit (port 8501) as subprocesses.
Render only exposes one port, so FastAPI is the primary web service.
Streamlit runs internally and FastAPI proxies to it if needed.
"""

import subprocess
import sys
import os
import signal
import time

def main():
    port = os.environ.get("PORT", "8000")
    
    procs = []
    
    # 1. Start FastAPI (primary — this is what Render exposes)
    fastapi_cmd = [
        sys.executable, "-m", "uvicorn",
        "api.main:app",
        "--host", "0.0.0.0",
        "--port", port,
        "--workers", "1"
    ]
    print(f"🚀 Starting FastAPI on port {port}...")
    p1 = subprocess.Popen(fastapi_cmd)
    procs.append(p1)
    
    # 2. Start Streamlit (secondary — runs on 8501 internally)
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run",
        "dashboard/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    print("📊 Starting Streamlit on port 8501...")
    p2 = subprocess.Popen(streamlit_cmd)
    procs.append(p2)
    
    # Handle shutdown
    def shutdown(sig, frame):
        print("\n🛑 Shutting down services...")
        for p in procs:
            p.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    
    # Wait for any process to exit
    while True:
        for p in procs:
            ret = p.poll()
            if ret is not None:
                print(f"Process {p.pid} exited with code {ret}. Shutting down all.")
                for pp in procs:
                    pp.terminate()
                sys.exit(ret)
        time.sleep(2)

if __name__ == "__main__":
    main()
