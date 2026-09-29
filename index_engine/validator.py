import pandas as pd
import numpy as np
import sqlite3

def get_dgca_fares(conn: sqlite3.Connection, 
                   start_month: str = None, end_month: str = None) -> pd.DataFrame:
    """Fetch DGCA validation fares from dgca_fares table."""
    query = "SELECT * FROM dgca_fares WHERE 1=1"
    params = []
    
    if start_month:
        query += " AND month >= ?"
        params.append(start_month)
    if end_month:
        query += " AND month <= ?"
        params.append(end_month)
        
    df = pd.read_sql_query(query, conn, params=params)
    return df

def compute_our_monthly_avg(conn: sqlite3.Connection,
                            month: str, origin: str, dest: str) -> float:
    """Compute our average fare for a specific route and month.
    month format: 'YYYY-MM'"""
    query = """
        SELECT AVG(total_fare) as avg_fare
        FROM fares
        WHERE origin = ? 
          AND destination = ?
          AND strftime('%Y-%m', scrape_date) = ?
          AND status = 'AVAILABLE'
          AND is_outlier = 0
    """
    df = pd.read_sql_query(query, conn, params=(origin, dest, month))
    return df['avg_fare'].iloc[0] if not df.empty and pd.notna(df['avg_fare'].iloc[0]) else np.nan

def backtest_against_dgca(conn: sqlite3.Connection) -> pd.DataFrame:
    """Compare our computed average fares against DGCA published averages.
    For each route-month in dgca_fares, compute our average and compare.
    Returns DataFrame with columns:
    month, origin, destination, dgca_avg_fare, our_avg_fare, 
    abs_error, pct_error, direction_match
    
    direction_match = True if both DGCA and our fare moved in same direction month-over-month"""
    
    dgca_df = get_dgca_fares(conn)
    if dgca_df.empty:
        return pd.DataFrame()
        
    dgca_df = dgca_df.sort_values(by=['origin', 'destination', 'month'])
    results = []
    
    for (origin, dest), group in dgca_df.groupby(['origin', 'destination']):
        prev_dgca = None
        prev_ours = None
        
        for _, row in group.iterrows():
            month = row['month']
            dgca_avg = row['avg_fare']
            
            our_avg = compute_our_monthly_avg(conn, month, origin, dest)
            
            abs_error = np.abs(our_avg - dgca_avg) if pd.notna(our_avg) else np.nan
            pct_error = (abs_error / dgca_avg) * 100 if pd.notna(our_avg) and dgca_avg > 0 else np.nan
            
            direction_match = None
            if prev_dgca is not None and prev_ours is not None and pd.notna(our_avg):
                dgca_diff = dgca_avg - prev_dgca
                our_diff = our_avg - prev_ours
                
                if (dgca_diff > 0 and our_diff > 0) or \
                   (dgca_diff < 0 and our_diff < 0) or \
                   (dgca_diff == 0 and our_diff == 0):
                    direction_match = True
                else:
                    direction_match = False
                    
            results.append({
                'month': month,
                'origin': origin,
                'destination': dest,
                'dgca_avg_fare': dgca_avg,
                'our_avg_fare': our_avg,
                'abs_error': abs_error,
                'pct_error': pct_error,
                'direction_match': direction_match
            })
            
            prev_dgca = dgca_avg
            prev_ours = our_avg
            
    return pd.DataFrame(results)

def compute_validation_metrics(backtest_df: pd.DataFrame) -> dict:
    """Compute overall validation metrics.
    Returns:
    - correlation: Pearson correlation between our and DGCA fares
    - mape: Mean Absolute Percentage Error
    - rmse: Root Mean Square Error  
    - directional_accuracy: % of months where price direction matches
    - r_squared: R-squared
    - num_comparisons: number of route-month pairs compared"""
    if backtest_df.empty:
        return {}
        
    valid_df = backtest_df.dropna(subset=['our_avg_fare', 'dgca_avg_fare'])
    if valid_df.empty:
        return {}
        
    correlation = valid_df['our_avg_fare'].corr(valid_df['dgca_avg_fare'])
    mape = valid_df['pct_error'].mean()
    rmse = np.sqrt((valid_df['abs_error']**2).mean())
    
    dir_match_df = valid_df.dropna(subset=['direction_match'])
    if not dir_match_df.empty:
        directional_accuracy = (dir_match_df['direction_match'].sum() / len(dir_match_df)) * 100
    else:
        directional_accuracy = np.nan
        
    y_true = valid_df['dgca_avg_fare']
    y_pred = valid_df['our_avg_fare']
    ss_res = ((y_true - y_pred) ** 2).sum()
    ss_tot = ((y_true - y_true.mean()) ** 2).sum()
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else np.nan
    
    return {
        'correlation': correlation,
        'mape': mape,
        'rmse': rmse,
        'directional_accuracy': directional_accuracy,
        'r_squared': r_squared,
        'num_comparisons': len(valid_df)
    }
