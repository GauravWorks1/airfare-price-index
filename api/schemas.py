from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class FareRecord(BaseModel):
    scrape_date: str
    travel_date: str
    advance_days: int
    origin: str
    destination: str
    carrier: str
    flight_number: Optional[str] = None
    base_fare: float
    taxes: float
    udf: Optional[float] = 0.0
    convenience_fee: Optional[float] = 350.0
    total_fare: float
    fare_class: str
    seats_available: Optional[int] = None
    status: str

class IndexValue(BaseModel):
    index_date: str
    index_type: str
    advance_days: Optional[int] = None
    index_value: float
    base_period: str
    num_routes: int
    num_observations: int

class RouteInfo(BaseModel):
    origin: str
    origin_city: str
    destination: str
    destination_city: str
    weight: Optional[float] = None

class HeatmapCell(BaseModel):
    origin: str
    destination: str
    avg_fare: float
    date: str

class ElasticityPoint(BaseModel):
    advance_days: int
    avg_fare: float
    min_fare: float
    max_fare: float
    num_observations: int

class ValidationResult(BaseModel):
    month: str
    origin: str
    destination: str
    dgca_avg_fare: float
    our_avg_fare: Optional[float] = None
    pct_error: Optional[float] = None
    direction_match: Optional[bool] = None

class ValidationMetrics(BaseModel):
    correlation: Optional[float] = None
    mape: Optional[float] = None
    rmse: Optional[float] = None
    directional_accuracy: Optional[float] = None
    r_squared: Optional[float] = None
    num_comparisons: int = 0

class CarrierStats(BaseModel):
    carrier: str
    carrier_name: str
    avg_fare: float
    min_fare: float
    max_fare: float
    num_flights: int
    market_share_pct: float

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    total_fares: int
    date_range: Dict[str, Any]

class IndexResponse(BaseModel):
    data: List[IndexValue]
    count: int

class FareResponse(BaseModel):
    data: List[FareRecord]
    count: int
