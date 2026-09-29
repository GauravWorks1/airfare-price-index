import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class MockScraper:
    def __init__(self, seed=42):
        self.seed = seed
        random.seed(self.seed)
        self.carrier_factors = {'AI': 1.15, '6E': 1.0, 'QP': 0.95, 'SG': 0.92, 'IX': 0.88, 'I5': 0.90}
        
        # Pre-assign consistent flight numbers for each route/carrier combination
        self.flight_info = {}
        for origin, dest in config.ROUTES:
            for carrier in config.CARRIERS:
                num_flights = random.randint(2, 4)
                flights = []
                for i in range(num_flights):
                    flights.append({
                        'flight_number': f"{carrier}{random.randint(100, 9999)}",
                        'flight_idx': i,
                        'num_flights': num_flights
                    })
                self.flight_info[(origin, dest, carrier)] = flights
                
    def _get_time_factor_and_time(self, flight_idx, num_flights):
        times = [
            ("06:00", 0.90), # Early morning
            ("09:30", 1.10), # Morning
            ("13:30", 0.95), # Afternoon
            ("18:00", 1.15), # Evening
            ("21:30", 0.92)  # Night
        ]
        idx = (flight_idx * len(times)) // num_flights
        return times[idx]

    def generate_fare(self, origin, dest, travel_date, scrape_date, carrier) -> dict:
        """
        Since we need 2-4 flights per carrier/route/day, this returns a list of dicts.
        Wait, requirement specifies returning dict, but logically returning list of dicts 
        suits the 2-4 flights requirement better. However, to keep signature, 
        we'll pick one flight at random here or return a list and flatten later.
        Let's adjust to return a single flight dict if called strictly, 
        but use a helper to generate all flights for the day in daily fares.
        """
        return self._generate_flight_fare(origin, dest, travel_date, scrape_date, carrier, flight_idx=0, num_flights=1, flight_no=f"{carrier}1234")

    def _generate_flight_fare(self, origin, dest, travel_date, scrape_date, carrier, flight_idx, num_flights, flight_no):
        distance = config.DISTANCE_KM.get((origin, dest), 1000)
        base = distance * config.BASE_FARE_PER_KM
        
        carrier_factor = self.carrier_factors.get(carrier, 1.0)
        
        advance_days = (travel_date - scrape_date).days
        if advance_days <= 1:
            adv_factor = random.uniform(2.5, 3.0)
        elif advance_days <= 7:
            adv_factor = random.uniform(1.8, 2.2)
        elif advance_days <= 15:
            adv_factor = random.uniform(1.3, 1.5)
        elif advance_days <= 30:
            adv_factor = random.uniform(1.0, 1.1)
        else:
            adv_factor = random.uniform(1.05, 1.15)
            
        dow = travel_date.weekday()
        if dow in [0, 4]: dow_factor = 1.15
        elif dow == 6: dow_factor = 1.10
        elif dow in [1, 2]: dow_factor = 0.90
        else: dow_factor = 1.0
        
        month = travel_date.month
        if month in [12, 1]: month_factor = 1.25
        elif month in [3, 4]: month_factor = 1.15
        elif month in [6, 7]: month_factor = 0.85
        elif month == 10: month_factor = 1.30
        else: month_factor = 1.0
        
        dep_time, time_factor = self._get_time_factor_and_time(flight_idx, num_flights)
        
        # Inflation trend (approx 0.05% per day)
        trend_days = (scrape_date - datetime(2026, 1, 1).date()).days
        trend_factor = 1.0 + (trend_days * 0.0005)
        
        raw_fare = base * carrier_factor * adv_factor * dow_factor * month_factor * time_factor * trend_factor
        
        noise = random.gauss(0, 0.05 * raw_fare)
        base_fare = max(raw_fare + noise, 500) 
        
        taxes = round(base_fare * 0.12, 2)
        udf = round(config.DISTANCE_KM.get((origin, dest), 1200) * 0.35, 2)
        convenience_fee = 350.0
        total_fare = round(base_fare + taxes + udf)
        base_fare = round(base_fare)
        taxes = round(taxes)
        
        seats = random.randint(1, 180)
        if advance_days <= 7:
            seats = random.randint(0, 50)
            
        rand_val = random.random()
        if rand_val < 0.02:
            status = 'CANCELLED'
        elif rand_val < 0.05 or seats == 0 or (advance_days <= 1 and rand_val < 0.08):
            status = 'SOLD_OUT'
            seats = 0
        else:
            status = 'AVAILABLE'
            
        return {
            'scrape_date': scrape_date.strftime('%Y-%m-%d'),
            'travel_date': travel_date.strftime('%Y-%m-%d'),
            'advance_days': advance_days,
            'origin': origin,
            'destination': dest,
            'carrier': carrier,
            'flight_number': flight_no,
            'departure_time': dep_time,
            'base_fare': base_fare,
            'taxes': taxes,
            'udf': udf,
            'convenience_fee': convenience_fee,
            'total_fare': total_fare,
            'fare_class': 'ECONOMY',
            'seats_available': seats,
            'status': status,
            'is_outlier': 0,
            'source': 'MOCK'
        }

    def generate_daily_fares(self, scrape_date) -> list[dict]:
        daily_data = []
        for origin, dest in config.ROUTES:
            for advance in config.ADVANCE_DAYS:
                travel_date = scrape_date + timedelta(days=advance)
                
                # Use 2-4 random carriers per route
                carriers_to_use = random.sample(list(config.CARRIERS.keys()), k=random.randint(2, min(4, len(config.CARRIERS))))
                
                for carrier in carriers_to_use:
                    flights = self.flight_info.get((origin, dest, carrier), [{'flight_number': f"{carrier}123", 'flight_idx': 0, 'num_flights': 1}])
                    for flight in flights:
                        fare_dict = self._generate_flight_fare(
                            origin, dest, travel_date, scrape_date, carrier,
                            flight['flight_idx'], flight['num_flights'], flight['flight_number']
                        )
                        daily_data.append(fare_dict)
        return daily_data

    def generate_historical_data(self, num_days=90) -> list[dict]:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=num_days)
        
        hist_data = []
        curr_date = start_date
        while curr_date <= end_date:
            hist_data.extend(self.generate_daily_fares(curr_date))
            curr_date += timedelta(days=1)
            
        return hist_data
