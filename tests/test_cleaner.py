import pytest
import pandas as pd
import numpy as np
from etl.cleaner import remove_duplicates, handle_missing_data, detect_outliers_iqr, detect_outliers_zscore, clean_fares

def test_remove_duplicates():
    data = [
        {"scrape_date": "2026-09-01", "travel_date": "2026-09-02", "origin": "DEL", "destination": "BOM", "carrier": "6E", "flight_number": "6E101", "total_fare": 5000},
        {"scrape_date": "2026-09-01", "travel_date": "2026-09-02", "origin": "DEL", "destination": "BOM", "carrier": "6E", "flight_number": "6E101", "total_fare": 5000},
        {"scrape_date": "2026-09-01", "travel_date": "2026-09-02", "origin": "DEL", "destination": "BOM", "carrier": "AI", "flight_number": "AI202", "total_fare": 6000},
    ]
    df = pd.DataFrame(data)
    deduped = remove_duplicates(df)
    assert len(deduped) == 2
    assert "carrier" in deduped.columns

def test_handle_missing_data():
    data = [
        {"total_fare": 5600, "base_fare": None, "taxes": None, "seats_available": None},
        {"total_fare": 1120, "base_fare": 1000, "taxes": None, "seats_available": 10},
    ]
    df = pd.DataFrame(data)
    cleaned = handle_missing_data(df)
    assert cleaned.loc[0, "base_fare"] == 5000.0
    assert cleaned.loc[0, "taxes"] == 600.0
    assert cleaned.loc[0, "seats_available"] == -1
    assert cleaned.loc[1, "taxes"] == 120.0

def test_detect_outliers_iqr_preserves_columns():
    data = [
        {"origin": "DEL", "destination": "BOM", "advance_days": 1, "total_fare": 5000},
        {"origin": "DEL", "destination": "BOM", "advance_days": 1, "total_fare": 5100},
        {"origin": "DEL", "destination": "BOM", "advance_days": 1, "total_fare": 4900},
        {"origin": "DEL", "destination": "BOM", "advance_days": 1, "total_fare": 5050},
        {"origin": "DEL", "destination": "BOM", "advance_days": 1, "total_fare": 99999}, # Outlier
    ]
    df = pd.DataFrame(data)
    flagged = detect_outliers_iqr(df)
    assert "origin" in flagged.columns
    assert "destination" in flagged.columns
    assert "advance_days" in flagged.columns
    assert flagged.loc[4, "is_outlier"] == 1
    assert flagged.loc[0, "is_outlier"] == 0
