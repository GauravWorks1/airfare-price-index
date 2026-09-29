import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from database.db import init_db
from api.routes import router

FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'

app = FastAPI(
    title=getattr(config, 'PROJECT_NAME', 'Airfare Price Index') + ' API',
    version=getattr(config, 'VERSION', '1.0.0'),
    description='REST API for the India Real-time Airfare Price Index'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    """Serves the modern Tailwind CSS analytics dashboard."""
    index_file = FRONTEND_DIR / 'index.html'
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h2>Frontend dashboard not found</h2>", status_code=404)

@app.on_event("startup")
def startup_event():
    init_db()
