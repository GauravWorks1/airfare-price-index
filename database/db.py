import sqlite3
import os
from pathlib import Path

# Use absolute import from config
from config import DATABASE_PATH

def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with Row factory and multi-threading enabled."""
    # Ensure directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database by creating necessary tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create fares table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scrape_date TEXT,
            travel_date TEXT,
            advance_days INTEGER,
            origin TEXT,
            destination TEXT,
            carrier TEXT,
            flight_number TEXT,
            base_fare REAL,
            taxes REAL,
            udf REAL DEFAULT 0.0,
            convenience_fee REAL DEFAULT 0.0,
            total_fare REAL,
            fare_class TEXT DEFAULT 'ECONOMY',
            seats_available INTEGER,
            status TEXT DEFAULT 'AVAILABLE',
            is_outlier INTEGER DEFAULT 0,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create route_weights table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS route_weights (
            origin TEXT,
            destination TEXT,
            passenger_volume INTEGER,
            weight REAL,
            year INTEGER,
            PRIMARY KEY(origin, destination, year)
        )
    ''')

    # Create price_index table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_index (
            index_date TEXT,
            index_type TEXT,
            advance_days INTEGER,
            index_value REAL,
            base_period TEXT,
            num_routes INTEGER,
            num_observations INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(index_date, index_type, advance_days)
        )
    ''')

    # Create dgca_fares table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dgca_fares (
            month TEXT,
            origin TEXT,
            destination TEXT,
            avg_fare REAL,
            passengers INTEGER,
            source_report TEXT,
            PRIMARY KEY(month, origin, destination)
        )
    ''')

    # Create indexes on fares table
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fares_scrape_date ON fares(scrape_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fares_origin_destination ON fares(origin, destination)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fares_carrier ON fares(carrier)')

    conn.commit()
    conn.close()
