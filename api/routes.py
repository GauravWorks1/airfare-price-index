import sys
import os
import sqlite3
import pandas as pd
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from database.db import get_connection
from etl.loader import get_fares_df
from index_engine.calculator import (
    compute_daily_index, compute_index_series,
    compute_weekly_index, compute_monthly_index
)
from index_engine.validator import backtest_against_dgca, compute_validation_metrics
from index_engine.weights import get_route_weights

from api.schemas import (
    HealthResponse, IndexResponse, IndexValue, RouteInfo,
    FareResponse, FareRecord, HeatmapCell, ElasticityPoint,
    ValidationResult, ValidationMetrics, CarrierStats
)

router = APIRouter(prefix='/api/v1')

@router.get('/health', response_model=HealthResponse)
def health_check():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM fares")
        total_fares_row = cur.fetchone()
        total_fares = total_fares_row[0] if total_fares_row else 0
        
        cur.execute("SELECT MIN(travel_date), MAX(travel_date) FROM fares")
        date_range_row = cur.fetchone()
        min_date = date_range_row[0] if date_range_row else None
        max_date = date_range_row[1] if date_range_row else None
        
        conn.close()
        
        return HealthResponse(
            status="healthy",
            version=getattr(config, 'VERSION', '1.0'),
            database="connected",
            total_fares=total_fares,
            date_range={"min_date": min_date, "max_date": max_date}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/index/daily', response_model=IndexResponse)
def get_daily_index(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    index_type: str = Query('LASPEYRES'),
    advance_days: Optional[int] = Query(None)
):
    conn = get_connection()
    query = "SELECT * FROM price_index WHERE index_type = ?"
    params = [index_type]
    
    if start_date:
        query += " AND index_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND index_date <= ?"
        params.append(end_date)
    if advance_days is not None:
        query += " AND advance_days = ?"
        params.append(advance_days)
        
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    records = df.to_dict('records')
    return IndexResponse(
        data=[IndexValue(**r) for r in records],
        count=len(records)
    )

@router.get('/index/monthly')
def get_monthly_index(index_type: str = Query('LASPEYRES')):
    conn = get_connection()
    query = "SELECT * FROM price_index WHERE index_type = ?"
    df = pd.read_sql_query(query, conn, params=[index_type])
    conn.close()
    
    if df.empty:
        return {"data": [], "count": 0}
        
    df['index_date'] = pd.to_datetime(df['index_date'])
    df['month'] = df['index_date'].dt.to_period('M').astype(str)
    
    monthly_df = df.groupby(['month', 'index_type', 'advance_days']).agg({
        'index_value': 'mean',
        'base_period': 'first',
        'num_routes': 'mean',
        'num_observations': 'sum'
    }).reset_index()
    
    monthly_df.rename(columns={'month': 'index_date'}, inplace=True)
    records = monthly_df.to_dict('records')
    return {"data": records, "count": len(records)}

@router.get('/fares/routes')
def get_routes():
    routes_list = []
    conn = get_connection()
    weights = get_route_weights(conn)
    conn.close()
    city_names = getattr(config, 'CITY_NAMES', {})
    
    for route in getattr(config, 'ROUTES', []):
        origin, dest = route
        weight = weights.get(route)
        routes_list.append(RouteInfo(
            origin=origin,
            origin_city=city_names.get(origin, origin),
            destination=dest,
            destination_city=city_names.get(dest, dest),
            weight=weight
        ))
    return routes_list

@router.get('/fares/route/{origin}/{dest}', response_model=FareResponse)
def get_route_fares(
    origin: str, dest: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    carrier: Optional[str] = Query(None)
):
    conn = get_connection()
    df = get_fares_df(conn, start_date, end_date, origin, dest, carrier, exclude_outliers=False)
    conn.close()
    
    if df.empty:
        return FareResponse(data=[], count=0)
        
    records = df.to_dict('records')
    return FareResponse(
        data=[FareRecord(**r) for r in records],
        count=len(records)
    )

@router.get('/fares/search')
def search_fares(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    limit: int = Query(10)
):
    """Returns unbundled fare quotes for specified origin and destination."""
    conn = get_connection()
    query = "SELECT * FROM fares WHERE is_outlier = 0"
    params = []
    if origin:
        query += " AND origin = ?"
        params.append(origin)
    if destination:
        query += " AND destination = ?"
        params.append(destination)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df.empty:
        return []
    return df.to_dict('records')

@router.post('/fares/live-scrape')
def trigger_live_scrape(
    origin: str = Query('DEL'),
    destination: str = Query('BOM'),
    travel_date: Optional[str] = Query(None)
):
    """Triggers live Playwright / calibrated dynamic scraper for a corridor."""
    from scraper.live_scraper import LiveAirfareScraper
    from etl.loader import load_fares_from_list
    from datetime import date, timedelta
    
    t_date = travel_date or (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
    scraper = LiveAirfareScraper(headless=True)
    quotes = scraper.scrape_route_sync(origin, destination, t_date)
    
    if quotes:
        conn = get_connection()
        load_fares_from_list(quotes, conn)
        conn.close()
        
    return quotes

@router.get('/fares/heatmap')
def get_fare_heatmap(date: Optional[str] = Query(None)):
    conn = get_connection()
    query = "SELECT origin, destination, AVG(total_fare) as avg_fare, travel_date FROM fares "
    params = []
    
    if date:
        query += "WHERE travel_date = ? "
        params.append(date)
        
    query += "GROUP BY origin, destination, travel_date"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    records = df.to_dict('records')
    return [HeatmapCell(
        origin=r['origin'],
        destination=r['destination'],
        avg_fare=r['avg_fare'],
        date=r['travel_date']
    ) for r in records]

@router.get('/fares/elasticity/{origin}/{dest}')
def get_elasticity(origin: str, dest: str):
    conn = get_connection()
    df = get_fares_df(conn, None, None, origin, dest, None, exclude_outliers=True)
    conn.close()
    
    if df.empty:
        return []
        
    elasticity_df = df.groupby('advance_days').agg(
        avg_fare=('total_fare', 'mean'),
        min_fare=('total_fare', 'min'),
        max_fare=('total_fare', 'max'),
        num_observations=('total_fare', 'count')
    ).reset_index()
    
    records = elasticity_df.to_dict('records')
    return [ElasticityPoint(**r) for r in records]

@router.get('/validation/backtest')
def get_backtest():
    import numpy as np
    conn = get_connection()
    results_df = backtest_against_dgca(conn)
    metrics_dict = compute_validation_metrics(results_df)
    conn.close()
    
    clean_records = []
    for r in results_df.to_dict('records'):
        clean_r = {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in r.items()}
        clean_records.append(ValidationResult(**clean_r))
        
    clean_metrics = {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in metrics_dict.items()}
    metrics = ValidationMetrics(**clean_metrics)
    
    return {
        "results": clean_records,
        "metrics": metrics
    }

@router.get('/carriers')
def get_carrier_stats(origin: Optional[str] = Query(None), destination: Optional[str] = Query(None)):
    conn = get_connection()
    query = "SELECT * FROM fares"
    conditions = []
    params = []
    if origin:
        conditions.append("origin = ?")
        params.append(origin)
    if destination:
        conditions.append("destination = ?")
        params.append(destination)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if df.empty:
        return []
        
    total_flights = len(df)
    carriers = getattr(config, 'CARRIERS', {})
    
    stats_df = df.groupby('carrier').agg(
        avg_fare=('total_fare', 'mean'),
        min_fare=('total_fare', 'min'),
        max_fare=('total_fare', 'max'),
        num_flights=('total_fare', 'count')
    ).reset_index()
    
    stats_df['market_share_pct'] = (stats_df['num_flights'] / total_flights) * 100
    
    records = stats_df.to_dict('records')
    return [CarrierStats(
        carrier=r['carrier'],
        carrier_name=carriers.get(r['carrier'], r['carrier']),
        avg_fare=r['avg_fare'],
        min_fare=r['min_fare'],
        max_fare=r['max_fare'],
        num_flights=r['num_flights'],
        market_share_pct=r['market_share_pct']
    ) for r in records]
