import sqlite3
import pandas as pd

def get_route_weights(conn: sqlite3.Connection, year: int = 2024) -> dict:
    """Fetch route weights from route_weights table.
    Returns dict: {(origin, dest): weight} where weights sum to 1.0"""
    query = "SELECT origin, destination, weight FROM route_weights WHERE year = ?"
    df = pd.read_sql_query(query, conn, params=(year,))
    
    total_weight = df['weight'].sum()
    if total_weight > 0:
        df['weight'] = df['weight'] / total_weight
        
    weights = {}
    for _, row in df.iterrows():
        weights[(row['origin'], row['destination'])] = row['weight']
        
    return weights

def calculate_weights_from_traffic(traffic_data: dict) -> dict:
    """Given {(origin,dest): passenger_count}, compute normalized weights.
    weight_r = passengers_r / sum(all passengers)
    Returns dict: {(origin, dest): weight}"""
    total_passengers = sum(traffic_data.values())
    if total_passengers == 0:
        return {}
        
    weights = {route: (passengers / total_passengers) for route, passengers in traffic_data.items()}
    return weights
