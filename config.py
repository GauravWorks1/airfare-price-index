import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'
DATABASE_PATH = DATA_DIR / 'airfare_index.db'

# Project Info
PROJECT_NAME = 'India Airfare Price Index'
VERSION = '1.0.0'

ROUTES = [
    ('DEL', 'BOM'), ('DEL', 'BLR'), ('BOM', 'BLR'), ('DEL', 'CCU'), 
    ('BLR', 'HYD'), ('MAA', 'DEL'), ('DEL', 'MAA'), ('BOM', 'CCU'), 
    ('DEL', 'HYD'), ('BLR', 'CCU'), ('DEL', 'GOI'), ('BOM', 'GOI'), 
    ('BLR', 'MAA'), ('HYD', 'DEL'), ('CCU', 'BLR'), ('DEL', 'JAI'), 
    ('BOM', 'HYD'), ('MAA', 'BLR'), ('DEL', 'PAT'), ('BOM', 'DEL')
]

CITY_NAMES = {
    'DEL': 'Delhi', 'BOM': 'Mumbai', 'BLR': 'Bengaluru', 'HYD': 'Hyderabad',
    'CCU': 'Kolkata', 'MAA': 'Chennai', 'GOI': 'Goa', 'JAI': 'Jaipur',
    'PAT': 'Patna', 'PNQ': 'Pune'
}

CARRIERS = {
    '6E': 'IndiGo', 'AI': 'Air India', 'QP': 'Akasa Air', 
    'SG': 'SpiceJet', 'IX': 'Air India Express', 'I5': 'AirAsia India'
}

ADVANCE_DAYS = [1, 7, 15, 30, 45]
BASE_PERIOD = '2023-01-01' # Adjust as needed

API_HOST = '0.0.0.0'
API_PORT = 8000
DASHBOARD_PORT = 8501
SCRAPE_HOUR = 6

INDEX_TYPES = ['LASPEYRES', 'PAASCHE', 'FISHER']

DISTANCE_KM = {
    ('DEL', 'BOM'): 1148, ('DEL', 'BLR'): 1740, ('BOM', 'BLR'): 842, 
    ('DEL', 'CCU'): 1305, ('BLR', 'HYD'): 503, ('MAA', 'DEL'): 1760, 
    ('DEL', 'MAA'): 1760, ('BOM', 'CCU'): 1654, ('DEL', 'HYD'): 1253, 
    ('BLR', 'CCU'): 1560, ('DEL', 'GOI'): 1515, ('BOM', 'GOI'): 435, 
    ('BLR', 'MAA'): 268, ('HYD', 'DEL'): 1253, ('CCU', 'BLR'): 1560, 
    ('DEL', 'JAI'): 231, ('BOM', 'HYD'): 622, ('MAA', 'BLR'): 268, 
    ('DEL', 'PAT'): 854, ('BOM', 'DEL'): 1148
}

BASE_FARE_PER_KM = 3.5
FUEL_SURCHARGE_RATE = 0.15
