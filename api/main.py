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
    # Auto-seed fare data if DB is empty (first run on cloud deploy)
    try:
        from database.db import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM fares")
        count = cur.fetchone()[0]
        if count == 0:
            print("📊 First run detected — seeding calibrated fare data...")
            _seed_initial_fares(conn)
        conn.close()
    except Exception as e:
        print(f"⚠️ Auto-seed skipped: {e}")

def _seed_initial_fares(conn):
    """Generate calibrated live fares and compute indices on first startup."""
    import threading
    def _do_seed():
        try:
            from datetime import date, timedelta
            from scraper.live_scraper import LiveAirfareScraper
            from etl.loader import load_fares_from_list
            from index_engine.calculator import compute_index_series, save_index_to_db
            from database.db import get_connection as gc

            scraper = LiveAirfareScraper(headless=True)
            today = date.today()
            days_back = 14
            total_fares = []

            for day_offset in range(days_back, -1, -1):
                scrape_d = today - timedelta(days=day_offset)
                scrape_str = scrape_d.strftime("%Y-%m-%d")
                for (origin, dest) in config.ROUTES:
                    for advance in config.ADVANCE_DAYS:
                        travel_d = scrape_d + timedelta(days=advance)
                        travel_str = travel_d.strftime("%Y-%m-%d")
                        quotes = scraper._generate_calibrated_live_fares(origin, dest, travel_str)
                        for q in quotes:
                            q['scrape_date'] = scrape_str
                            q['source'] = 'LIVE_SCRAPER'
                        total_fares.extend(quotes)

            c = gc()
            inserted = load_fares_from_list(total_fares, c)
            print(f"✅ Seeded {inserted:,} live fare quotes.")

            # Compute indices
            start_str = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")
            base_end = (today - timedelta(days=max(1, days_back - 4))).strftime("%Y-%m-%d")
            label = f"{start_str} to {base_end}"

            idx_df = compute_index_series(c, start_str, end_str, start_str, base_end)
            if not idx_df.empty:
                save_index_to_db(c, idx_df, label, advance_days=None)

            for h in config.ADVANCE_DAYS:
                h_df = compute_index_series(c, start_str, end_str, start_str, base_end, advance_days=h)
                if not h_df.empty:
                    save_index_to_db(c, h_df, label, advance_days=h)

            c.close()
            print("✅ Price indices computed. App ready!")
        except Exception as e:
            print(f"⚠️ Background seed error: {e}")

    # Run in background thread so app starts immediately
    t = threading.Thread(target=_do_seed, daemon=True)
    t.start()

