import pytest
from datetime import date
from scraper.mock_scraper import MockScraper

def test_mock_scraper_daily_generation():
    scraper = MockScraper(seed=100)
    today = date(2026, 9, 1)
    fares = scraper.generate_daily_fares(today)
    
    assert len(fares) > 0
    sample = fares[0]
    
    assert sample["scrape_date"] == "2026-09-01"
    assert "total_fare" in sample
    assert sample["total_fare"] > 0
    assert sample["fare_class"] == "ECONOMY"
    assert sample["advance_days"] in [1, 7, 15, 30, 45]
    assert sample["origin"] != sample["destination"]

def test_mock_scraper_advance_purchase_discount():
    scraper = MockScraper(seed=42)
    today = date(2026, 9, 1)
    fares = scraper.generate_daily_fares(today)
    
    # Check that average fare for T+1 is significantly higher than T+30
    fares_t1 = [f["total_fare"] for f in fares if f["advance_days"] == 1]
    fares_t30 = [f["total_fare"] for f in fares if f["advance_days"] == 30]
    
    avg_t1 = sum(fares_t1) / len(fares_t1)
    avg_t30 = sum(fares_t30) / len(fares_t30)
    
    # T+1 should be at least 1.5x more expensive on average than T+30
    assert avg_t1 > 1.5 * avg_t30
