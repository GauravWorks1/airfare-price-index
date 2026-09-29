#!/usr/bin/env python3
"""
run_pipeline.py — Main orchestration script for the India Airfare Price Index.

This script runs the complete pipeline:
  1. Initialize the database
  2. Generate mock fare data (90 days)
  3. Seed DGCA route weights & validation fares
  4. Run ETL cleaning pipeline
  5. Compute price indices (Laspeyres, Paasche, Fisher)
  6. Run DGCA back-test validation
  7. Print summary statistics

Usage:
    python run_pipeline.py              # Run full pipeline
    python run_pipeline.py --days 30    # Generate 30 days of data
    python run_pipeline.py --skip-gen   # Skip data generation, just recompute index
"""

import sys
import os
import argparse
from datetime import datetime, timedelta

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from config import DATABASE_PATH, ROUTES, CARRIERS, ADVANCE_DAYS, BASE_PERIOD
from database.db import get_connection, init_db
from database.seed_dgca import seed_all
from scraper.mock_scraper import MockScraper
from etl.parser import parse_batch
from etl.cleaner import clean_fares
from etl.loader import load_fares_to_db, get_fares_df
from index_engine.calculator import (
    compute_index_series, compute_weekly_index,
    compute_monthly_index, save_index_to_db
)
from index_engine.validator import backtest_against_dgca, compute_validation_metrics


def print_banner():
    """Print a nice startup banner."""
    print("=" * 65)
    print("  ✈️  INDIA AIRFARE PRICE INDEX — PIPELINE RUNNER")
    print("  SIH 2026 | MoSPI/NSO CPI Augmentation Project")
    print("=" * 65)
    print()


def step_1_init_db(clean=True):
    """Initialize database tables. If clean=True, clear existing data first."""
    print("📦 STEP 1: Initializing database...")
    if clean and DATABASE_PATH.exists():
        try:
            import os
            os.remove(DATABASE_PATH)
            print(f"   Removed old database at {DATABASE_PATH}")
        except Exception as e:
            print(f"   Warning: could not delete DB file ({e}), clearing tables instead")
    init_db()
    if clean:
        conn = get_connection()
        for tbl in ['fares', 'price_index', 'route_weights', 'dgca_fares']:
            try:
                conn.execute(f"DELETE FROM {tbl}")
            except Exception:
                pass
        conn.commit()
        conn.close()
    print(f"   ✅ Database ready at: {DATABASE_PATH}")
    print()


def step_2_generate_data(num_days=90):
    """Generate mock fare data."""
    print(f"🎲 STEP 2: Generating {num_days} days of mock fare data...")
    print(f"   Routes: {len(ROUTES)} city-pairs")
    print(f"   Carriers: {len(CARRIERS)} airlines")
    print(f"   Horizons: {ADVANCE_DAYS}")
    
    scraper = MockScraper(seed=42)
    raw_fares = scraper.generate_historical_data(num_days=num_days)
    
    print(f"   ✅ Generated {len(raw_fares):,} raw fare observations")
    print()
    return raw_fares


def step_3_seed_dgca(conn):
    """Seed DGCA route weights and validation data."""
    print("📊 STEP 3: Seeding DGCA route weights & validation fares...")
    seed_all(conn)
    
    # Verify
    cursor = conn.execute("SELECT COUNT(*) FROM route_weights")
    rw_count = cursor.fetchone()[0]
    cursor = conn.execute("SELECT COUNT(*) FROM dgca_fares")
    df_count = cursor.fetchone()[0]
    
    print(f"   ✅ Route weights: {rw_count} entries")
    print(f"   ✅ DGCA validation fares: {df_count} entries")
    print()


def step_4_etl(raw_fares, conn):
    """Run ETL pipeline: parse, clean, load."""
    print("🔧 STEP 4: Running ETL pipeline...")
    
    # Parse
    parsed_fares, failures = parse_batch(raw_fares)
    print(f"   Parsed: {len(parsed_fares):,} fares ({failures} failures)")
    
    # Clean
    if len(parsed_fares) > 0:
        df = pd.DataFrame(parsed_fares)
        cleaned_df = clean_fares(df, outlier_method='iqr')
        
        # Load to DB
        rows_inserted = load_fares_to_db(cleaned_df, conn)
        
        outlier_count = cleaned_df['is_outlier'].sum() if 'is_outlier' in cleaned_df.columns else 0
        print(f"   Cleaned: {len(cleaned_df):,} fares ({outlier_count} outliers flagged)")
        print(f"   ✅ Loaded {rows_inserted:,} fares into database")
    else:
        print("   ⚠️  No fares to process!")
    print()


def step_5_compute_index(conn):
    """Compute price indices."""
    print("📈 STEP 5: Computing price indices...")
    
    # Determine date range from actual data
    cursor = conn.execute("SELECT MIN(scrape_date), MAX(scrape_date) FROM fares")
    row = cursor.fetchone()
    if row[0] is None:
        print("   ⚠️  No fare data found in database!")
        return
    
    start_date = row[0]
    end_date = row[1]
    
    # Use first 7 days as base period
    base_start = start_date
    base_end_dt = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=6)
    base_end = base_end_dt.strftime('%Y-%m-%d')
    
    print(f"   Date range: {start_date} to {end_date}")
    print(f"   Base period: {base_start} to {base_end}")
    
    # Compute for all horizons combined
    print("   Computing daily index (all horizons)...")
    daily_df = compute_index_series(conn, start_date, end_date, base_start, base_end)
    
    if daily_df is not None and len(daily_df) > 0:
        # Save to DB
        save_index_to_db(conn, daily_df, base_start)
        
        # Compute weekly and monthly
        weekly_df = compute_weekly_index(daily_df)
        monthly_df = compute_monthly_index(daily_df)
        
        # Print summary
        latest = daily_df.iloc[-1] if len(daily_df) > 0 else None
        if latest is not None:
            print(f"   Latest Laspeyres Index: {latest.get('LASPEYRES', 'N/A'):.2f}")
            print(f"   Latest Paasche Index:   {latest.get('PAASCHE', 'N/A'):.2f}")
            print(f"   Latest Fisher Index:    {latest.get('FISHER', 'N/A'):.2f}")
        
        print(f"   ✅ Computed {len(daily_df)} daily index values")
        print(f"   ✅ Computed {len(weekly_df)} weekly index values")
        print(f"   ✅ Computed {len(monthly_df)} monthly index values")
    else:
        print("   ⚠️  Could not compute index (insufficient data)")
    
    # Also compute per-horizon indices
    for adv in ADVANCE_DAYS:
        print(f"   Computing index for T+{adv} horizon...")
        horizon_df = compute_index_series(conn, start_date, end_date, 
                                           base_start, base_end, advance_days=adv)
        if horizon_df is not None and len(horizon_df) > 0:
            save_index_to_db(conn, horizon_df, base_start, advance_days=adv)
    
    print()


def step_6_validate(conn):
    """Run DGCA back-test validation."""
    print("✅ STEP 6: Running DGCA back-test validation...")
    
    try:
        backtest_df = backtest_against_dgca(conn)
        
        if backtest_df is not None and len(backtest_df) > 0:
            metrics = compute_validation_metrics(backtest_df)
            
            print(f"   Comparisons: {metrics.get('num_comparisons', 0)}")
            print(f"   Correlation:  {metrics.get('correlation', 0):.4f}")
            print(f"   MAPE:         {metrics.get('mape', 0):.2f}%")
            print(f"   RMSE:         {metrics.get('rmse', 0):.2f} INR")
            print(f"   R²:           {metrics.get('r_squared', 0):.4f}")
            print(f"   Direction:    {metrics.get('directional_accuracy', 0):.1f}%")
            print(f"   ✅ Validation complete!")
        else:
            print("   ⚠️  No overlapping data for validation")
    except Exception as e:
        print(f"   ⚠️  Validation error: {e}")
    
    print()


def print_summary(conn):
    """Print final summary statistics."""
    print("=" * 65)
    print("  📊 PIPELINE SUMMARY")
    print("=" * 65)
    
    cursor = conn.execute("SELECT COUNT(*) FROM fares")
    total_fares = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(DISTINCT origin || '-' || destination) FROM fares")
    total_routes = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(DISTINCT carrier) FROM fares")
    total_carriers = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT MIN(scrape_date), MAX(scrape_date) FROM fares")
    date_range = cursor.fetchone()
    
    cursor = conn.execute("SELECT COUNT(*) FROM price_index")
    total_indices = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT AVG(total_fare) FROM fares WHERE is_outlier = 0")
    avg_fare_row = cursor.fetchone()
    avg_fare = avg_fare_row[0] if avg_fare_row[0] else 0
    
    print(f"  Total fare observations: {total_fares:,}")
    print(f"  Active routes:           {total_routes}")
    print(f"  Airlines tracked:        {total_carriers}")
    print(f"  Date range:              {date_range[0]} → {date_range[1]}")
    print(f"  Index values computed:   {total_indices}")
    print(f"  Average fare (non-outlier): ₹{avg_fare:,.0f}")
    print()
    print("  🚀 Next steps:")
    print("     1. Start API:       python run_api.py")
    print("     2. Start Dashboard: streamlit run dashboard/app.py")
    print("     3. API docs:        http://localhost:8000/docs")
    print("     4. Dashboard:       http://localhost:8501")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description='India Airfare Price Index Pipeline')
    parser.add_argument('--days', type=int, default=90, 
                        help='Number of days of historical data to generate (default: 90)')
    parser.add_argument('--skip-gen', action='store_true',
                        help='Skip data generation, just recompute index')
    args = parser.parse_args()
    
    print_banner()
    
    # Step 1: Init DB
    step_1_init_db()
    
    conn = get_connection()
    
    try:
        if not args.skip_gen:
            # Step 2: Generate data
            raw_fares = step_2_generate_data(num_days=args.days)
            
            # Step 3: Seed DGCA
            step_3_seed_dgca(conn)
            
            # Step 4: ETL
            step_4_etl(raw_fares, conn)
        else:
            print("⏭️  Skipping data generation (--skip-gen)")
            print()
        
        # Step 5: Compute index
        step_5_compute_index(conn)
        
        # Step 6: Validate
        step_6_validate(conn)
        
        # Summary
        print_summary(conn)
        
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
