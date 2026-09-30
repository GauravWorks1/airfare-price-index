"""
docker_init_db.py — Lightweight DB initialization for Docker builds.
Only creates tables and seeds DGCA reference data.
Fare data is generated on first app startup instead.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

import config
from database.db import init_db, get_connection
from database.seed_dgca import seed_route_weights, seed_dgca_validation_fares

def init_docker_db():
    print("=" * 50)
    print("  Initializing Database for Docker Deployment")
    print("=" * 50)

    # 1. Create tables
    print("\n[1/3] Creating database tables...")
    init_db()
    print("  Done.")

    # 2. Seed route weights
    print("[2/3] Seeding DGCA route weights...")
    conn = get_connection()
    seed_route_weights(conn)
    print("  Done.")

    # 3. Seed validation fares
    print("[3/3] Seeding DGCA validation fares...")
    seed_dgca_validation_fares(conn)
    conn.close()
    print("  Done.")

    print("\n" + "=" * 50)
    print("  Database initialized successfully!")
    print("=" * 50)

if __name__ == "__main__":
    init_docker_db()
