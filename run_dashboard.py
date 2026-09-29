import subprocess
import sys
import os

def run_dashboard():
    """Runs the Streamlit dashboard on port 8501."""
    
    # Try to import config to get DASHBOARD_PORT if available
    port = 8501
    try:
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        import config
        if hasattr(config, 'DASHBOARD_PORT'):
            port = config.DASHBOARD_PORT
    except ImportError:
        pass
        
    dashboard_path = os.path.join("dashboard", "app.py")
    
    print(f"Starting Streamlit dashboard on port {port}...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path, 
            "--server.port", str(port)
        ], check=True)
    except KeyboardInterrupt:
        print("Dashboard stopped by user.")
    except Exception as e:
        print(f"Failed to start dashboard: {e}")

if __name__ == "__main__":
    run_dashboard()
