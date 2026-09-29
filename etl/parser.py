import datetime
import re
from typing import Any, Dict, List, Optional, Tuple

def parse_raw_fare(raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse and validate a raw fare dict from any scraper source.
    Ensures all required fields are present and correctly typed.
    Returns cleaned dict or None if unparseable.
    """
    required_keys = [
        "scrape_date", "travel_date", "advance_days", "origin", 
        "destination", "carrier", "total_fare", "source"
    ]
    
    # Check if all required fields are present
    for key in required_keys:
        if key not in raw_data or raw_data[key] is None:
            return None
            
    try:
        # Validate IATA codes
        origin = str(raw_data["origin"]).strip().upper()
        destination = str(raw_data["destination"]).strip().upper()
        if not (re.match(r"^[A-Z]{3}$", origin) and re.match(r"^[A-Z]{3}$", destination)):
            return None
            
        # Validate dates
        try:
            datetime.datetime.strptime(str(raw_data["scrape_date"]), "%Y-%m-%d")
            datetime.datetime.strptime(str(raw_data["travel_date"]), "%Y-%m-%d")
        except ValueError:
            return None
            
        # Validate fares
        total_fare = float(raw_data["total_fare"])
        if total_fare <= 0:
            return None
            
        advance_days = int(raw_data["advance_days"])
        if advance_days < 0:
            return None
            
        parsed_fare = {
            "scrape_date": str(raw_data["scrape_date"]),
            "travel_date": str(raw_data["travel_date"]),
            "advance_days": advance_days,
            "origin": origin,
            "destination": destination,
            "carrier": str(raw_data["carrier"]).strip(),
            "total_fare": total_fare,
            "source": str(raw_data["source"]).strip(),
            "flight_number": str(raw_data.get("flight_number", "")).strip(),
            "fare_class": str(raw_data.get("fare_class", "ECONOMY")).strip() or "ECONOMY",
            "status": str(raw_data.get("status", "AVAILABLE")).strip() or "AVAILABLE",
            "is_outlier": int(raw_data.get("is_outlier", 0)),
        }
        
        # Handle seats_available
        seats_available = raw_data.get("seats_available")
        if seats_available is not None:
            try:
                parsed_fare["seats_available"] = int(seats_available)
            except ValueError:
                parsed_fare["seats_available"] = -1
        else:
            parsed_fare["seats_available"] = -1

        # Handle base_fare, taxes, udf, and convenience_fee
        base_fare = raw_data.get("base_fare")
        taxes = raw_data.get("taxes")
        udf = raw_data.get("udf")
        convenience_fee = raw_data.get("convenience_fee", 350.0)
        
        parsed_fare["convenience_fee"] = float(convenience_fee) if convenience_fee is not None else 350.0

        if udf is not None:
            parsed_fare["udf"] = float(udf)
        else:
            parsed_fare["udf"] = round(total_fare * 0.05, 2)

        if base_fare is not None and taxes is not None:
            parsed_fare["base_fare"] = float(base_fare)
            parsed_fare["taxes"] = float(taxes)
        elif base_fare is None and taxes is None:
            parsed_fare["taxes"] = round(total_fare * 0.12, 2)
            parsed_fare["base_fare"] = round(total_fare - parsed_fare["taxes"] - parsed_fare["udf"], 2)
        elif base_fare is None:
            parsed_fare["taxes"] = float(taxes)
            parsed_fare["base_fare"] = round(total_fare - parsed_fare["taxes"] - parsed_fare["udf"], 2)
        elif taxes is None:
            parsed_fare["base_fare"] = float(base_fare)
            parsed_fare["taxes"] = round(total_fare - parsed_fare["base_fare"] - parsed_fare["udf"], 2)
            
        return parsed_fare
    except (ValueError, TypeError):
        return None

def parse_batch(raw_fares: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    """
    Parse a batch of raw fares, skipping invalid ones.
    Return list of parsed fares + count of failures.
    """
    parsed_fares = []
    failures = 0
    
    for raw_fare in raw_fares:
        parsed = parse_raw_fare(raw_fare)
        if parsed is not None:
            parsed_fares.append(parsed)
        else:
            failures += 1
            
    return parsed_fares, failures
