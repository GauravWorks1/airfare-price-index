import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional

def load_fares_to_db(df: pd.DataFrame, conn: sqlite3.Connection) -> int:
    """
    Insert cleaned fare data into the fares table.
    Uses INSERT OR IGNORE to handle duplicates.
    Filters out any columns not in the DB schema.
    Returns number of rows inserted.
    """
    if df.empty:
        return 0

    # Only include columns that exist in the fares table
    db_columns = [
        'scrape_date', 'travel_date', 'advance_days', 'origin', 'destination',
        'carrier', 'flight_number', 'base_fare', 'taxes', 'udf', 'convenience_fee',
        'total_fare', 'fare_class', 'seats_available', 'status', 'is_outlier', 'source'
    ]
    # Filter to columns that exist in both the DataFrame and the DB
    columns = [col for col in db_columns if col in df.columns]
    filtered_df = df[columns]

    cols_str = ", ".join(columns)
    placeholders = ", ".join(["?" for _ in columns])

    insert_sql = f"""
        INSERT OR IGNORE INTO fares ({cols_str})
        VALUES ({placeholders})
    """

    records = filtered_df.to_dict('records')
    values = [tuple(record[col] for col in columns) for record in records]

    try:
        cursor = conn.cursor()
        cursor.executemany(insert_sql, values)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        print(f"Error inserting into database: {e}")
        conn.rollback()
        return 0

def load_fares_from_list(fares: List[Dict[str, Any]], conn: sqlite3.Connection) -> int:
    """
    Convenience: convert list of dicts to DataFrame, then load.
    """
    if not fares:
        return 0
    df = pd.DataFrame(fares)
    return load_fares_to_db(df, conn)

def get_fares_df(conn: sqlite3.Connection, 
                 start_date: Optional[str] = None, 
                 end_date: Optional[str] = None,
                 origin: Optional[str] = None, 
                 destination: Optional[str] = None,
                 carrier: Optional[str] = None, 
                 exclude_outliers: bool = True,
                 date_col: str = "scrape_date") -> pd.DataFrame:
    """
    Query fares table with optional filters. Returns DataFrame.
    """
    query = "SELECT * FROM fares WHERE 1=1"
    params = []
    
    if start_date:
        query += f" AND {date_col} >= ?"
        params.append(start_date)
        
    if end_date:
        query += f" AND {date_col} <= ?"
        params.append(end_date)
        
    if origin:
        query += " AND origin = ?"
        params.append(origin)
        
    if destination:
        query += " AND destination = ?"
        params.append(destination)
        
    if carrier:
        query += " AND carrier = ?"
        params.append(carrier)
        
    if exclude_outliers:
        query += " AND is_outlier = 0"
        
    return pd.read_sql_query(query, conn, params=params)
