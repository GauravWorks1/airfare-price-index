import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import sqlite3
from typing import Optional, Dict, Any

def compute_route_avg_fare(fares_df: pd.DataFrame, 
                           origin: str, dest: str,
                           target_date: str,
                           advance_days: int = None) -> float:
    """Compute weighted average fare for a single route on a given date.
    If advance_days specified, filter to that horizon only.
    Otherwise average across all horizons.
    Only include non-outlier, AVAILABLE fares.
    Returns mean total_fare, or NaN if no data."""
    if fares_df.empty:
        return np.nan
        
    mask = (fares_df['origin'] == origin) & (fares_df['destination'] == dest) & (fares_df['scrape_date'] == target_date)
    if 'status' in fares_df.columns:
        mask = mask & (fares_df['status'] == 'AVAILABLE')
    if 'is_outlier' in fares_df.columns:
        mask = mask & (fares_df['is_outlier'] == 0)
        
    if advance_days is not None and 'advance_days' in fares_df.columns:
        mask = mask & (fares_df['advance_days'] == advance_days)
        
    filtered = fares_df[mask]
    if filtered.empty:
        return np.nan
        
    return float(filtered['total_fare'].mean())

def compute_base_period_prices(fares_df: pd.DataFrame, 
                               base_start: str, base_end: str,
                               weights: dict,
                               advance_days: int = None) -> dict:
    """Compute average prices during the base period for each route.
    base_start, base_end are date strings (YYYY-MM-DD).
    Returns {(origin, dest): avg_fare_in_base_period}"""
    if fares_df.empty:
        return {}
        
    mask = (fares_df['scrape_date'] >= base_start) & (fares_df['scrape_date'] <= base_end)
    if 'status' in fares_df.columns:
        mask = mask & (fares_df['status'] == 'AVAILABLE')
    if 'is_outlier' in fares_df.columns:
        mask = mask & (fares_df['is_outlier'] == 0)
    if advance_days is not None and 'advance_days' in fares_df.columns:
        mask = mask & (fares_df['advance_days'] == advance_days)
        
    base_df = fares_df[mask]
    base_prices = {}
    
    for route in weights.keys():
        r_df = base_df[(base_df['origin'] == route[0]) & (base_df['destination'] == route[1])]
        if not r_df.empty:
            base_prices[route] = float(r_df['total_fare'].mean())
            
    return base_prices

def laspeyres_index(current_prices: dict, base_prices: dict, weights: dict) -> float:
    """Compute Laspeyres Price Index.
    I_L = (sum(w_r * p_r_t) / sum(w_r * p_r_0)) * 100
    where w_r = route weight, p_r_t = current price, p_r_0 = base price.
    Only include routes where both current and base prices exist.
    Returns index value (base = 100)."""
    numerator = 0.0
    denominator = 0.0
    
    for route, w in weights.items():
        if route in current_prices and route in base_prices and pd.notna(current_prices[route]) and pd.notna(base_prices[route]):
            numerator += w * current_prices[route]
            denominator += w * base_prices[route]
            
    if denominator == 0:
        return np.nan
    return float((numerator / denominator) * 100)

def paasche_index(current_prices: dict, base_prices: dict, weights: dict) -> float:
    """Compute Paasche Price Index (harmonic form with route weights)."""
    denominator = 0.0
    total_w = 0.0
    
    for route, w in weights.items():
        if route in current_prices and route in base_prices and pd.notna(current_prices[route]) and pd.notna(base_prices[route]):
            if current_prices[route] > 0:
                denominator += w * (base_prices[route] / current_prices[route])
                total_w += w
    
    if denominator == 0:
        return np.nan
    return float((total_w / denominator) * 100)

def fisher_index(laspeyres: float, paasche: float) -> float:
    """Fisher Ideal Index = geometric mean of Laspeyres and Paasche.
    I_F = sqrt(I_L * I_P)"""
    if pd.isna(laspeyres) or pd.isna(paasche) or laspeyres <= 0 or paasche <= 0:
        return np.nan
    return float(np.sqrt(laspeyres * paasche))

def compute_daily_index(conn: sqlite3.Connection, 
                        target_date: str,
                        base_start: str, base_end: str,
                        advance_days: int = None,
                        all_fares_df: Optional[pd.DataFrame] = None,
                        base_prices: Optional[dict] = None) -> dict:
    """Compute all three index types for a given date.
    Returns {'LASPEYRES': value, 'PAASCHE': value, 'FISHER': value,
             'num_routes': n, 'num_observations': n}"""
    from index_engine.weights import get_route_weights
    from etl.loader import get_fares_df
        
    weights = get_route_weights(conn)
    
    if all_fares_df is not None:
        fares_df = all_fares_df
    else:
        fares_df = get_fares_df(conn, min(base_start, target_date), max(base_end, target_date), exclude_outliers=True, date_col='scrape_date')
    
    if base_prices is None:
        base_prices = compute_base_period_prices(fares_df, base_start, base_end, weights, advance_days)
    
    # Filter for target date
    day_mask = (fares_df['scrape_date'] == target_date)
    if 'status' in fares_df.columns:
        day_mask = day_mask & (fares_df['status'] == 'AVAILABLE')
    if 'is_outlier' in fares_df.columns:
        day_mask = day_mask & (fares_df['is_outlier'] == 0)
    if advance_days is not None and 'advance_days' in fares_df.columns:
        day_mask = day_mask & (fares_df['advance_days'] == advance_days)
    current_fares_df = fares_df[day_mask]
    
    # Compute current prices for each route
    current_prices = {}
    num_obs = 0
    
    if not current_fares_df.empty:
        route_avgs = current_fares_df.groupby(['origin', 'destination'])['total_fare'].agg(['mean', 'count'])
        for route in weights.keys():
            if route in route_avgs.index:
                current_prices[route] = float(route_avgs.loc[route, 'mean'])
                num_obs += int(route_avgs.loc[route, 'count'])
            
    # Calculate all three indices
    laspeyres = laspeyres_index(current_prices, base_prices, weights)
    paasche = paasche_index(current_prices, base_prices, weights)
    fisher = fisher_index(laspeyres, paasche)
    
    num_routes = sum(1 for r in weights.keys() if r in current_prices and r in base_prices)
    
    return {
        'LASPEYRES': laspeyres,
        'PAASCHE': paasche,
        'FISHER': fisher,
        'num_routes': num_routes,
        'num_observations': num_obs
    }

def compute_index_series(conn: sqlite3.Connection,
                         start_date: str, end_date: str,
                         base_start: str, base_end: str,
                         advance_days: int = None) -> pd.DataFrame:
    """Compute daily index for a date range efficiently using single DB read."""
    from index_engine.weights import get_route_weights
    from etl.loader import get_fares_df
    
    weights = get_route_weights(conn)
    query_start = min(start_date, base_start)
    query_end = max(end_date, base_end)
    
    all_fares_df = get_fares_df(conn, query_start, query_end, exclude_outliers=True, date_col='scrape_date')
    base_prices = compute_base_period_prices(all_fares_df, base_start, base_end, weights, advance_days)
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    results = []
    curr_dt = start_dt
    while curr_dt <= end_dt:
        curr_str = curr_dt.strftime('%Y-%m-%d')
        daily_res = compute_daily_index(
            conn, curr_str, base_start, base_end, advance_days,
            all_fares_df=all_fares_df, base_prices=base_prices
        )
        daily_res['index_date'] = curr_str
        results.append(daily_res)
        curr_dt += timedelta(days=1)
        
    df = pd.DataFrame(results)
    return df[['index_date', 'LASPEYRES', 'PAASCHE', 'FISHER', 'num_routes', 'num_observations']]

def compute_weekly_index(daily_df: pd.DataFrame) -> pd.DataFrame:
    """Compute 7-day rolling average of the daily index."""
    df = daily_df.copy()
    df['index_date'] = pd.to_datetime(df['index_date'])
    df = df.sort_values('index_date')
    
    for col in ['LASPEYRES', 'PAASCHE', 'FISHER']:
        df[f'{col}_7d'] = df[col].rolling(window=7, min_periods=1).mean()
        
    return df

def compute_monthly_index(daily_df: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly average of the daily index. Group by year-month, take mean."""
    df = daily_df.copy()
    df['index_date'] = pd.to_datetime(df['index_date'])
    df['year_month'] = df['index_date'].dt.to_period('M')
    
    monthly_df = df.groupby('year_month')[['LASPEYRES', 'PAASCHE', 'FISHER']].mean().reset_index()
    monthly_df['year_month'] = monthly_df['year_month'].astype(str)
    return monthly_df

def save_index_to_db(conn: sqlite3.Connection, index_df: pd.DataFrame, 
                     base_period: str, advance_days: int = None):
    """Save computed index values to the price_index table."""
    adv_val = advance_days if advance_days is not None else -1
    
    cursor = conn.cursor()
    for _, row in index_df.iterrows():
        idx_date = str(row['index_date'])[:10]
        num_routes = int(row.get('num_routes', 0))
        num_obs = int(row.get('num_observations', 0))
        
        for idx_type in ['LASPEYRES', 'PAASCHE', 'FISHER']:
            val = row.get(idx_type, None)
            if val is not None and not pd.isna(val):
                cursor.execute('''
                    INSERT OR REPLACE INTO price_index 
                    (index_date, index_type, advance_days, index_value, base_period, num_routes, num_observations)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (idx_date, idx_type, adv_val, float(val), base_period, num_routes, num_obs))
    conn.commit()
