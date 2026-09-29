"""
carrier_compare.py — Airline Price Competitiveness & Market Concentration Intelligence.
Compares domestic carrier fare bands, flight frequencies, and pricing dispersion.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dashboard.components.charts import create_carrier_comparison, create_carrier_market_share
from dashboard.components.filters import render_route_filter
import config

def render_carrier_comparison_page():
    try:
        routes = getattr(config, 'ROUTES', [('DEL', 'BOM'), ('BOM', 'BLR')])
        carriers = getattr(config, 'CARRIERS', {})
    except Exception:
        routes = [('DEL', 'BOM')]
        carriers = {}

    origin, dest = render_route_filter(routes, 'carrier_pg')

    conn = st.session_state.get('db_conn', None)
    if not conn:
        st.warning("⚠️ Database connection unavailable.")
        return

    try:
        query = """
            SELECT carrier, 
                   AVG(total_fare) as avg_fare, 
                   MIN(total_fare) as min_fare,
                   MAX(total_fare) as max_fare,
                   COUNT(*) as flight_count
            FROM fares
            WHERE is_outlier = 0 AND status = 'AVAILABLE'
        """
        params = []
        if origin and dest:
            query += " AND origin = ? AND destination = ?"
            params.extend([origin, dest])
        query += " GROUP BY carrier ORDER BY avg_fare"

        carrier_df = pd.read_sql_query(query, conn, params=params)

        if not carrier_df.empty:
            carrier_df['carrier_name'] = carrier_df['carrier'].map(carriers).fillna(carrier_df['carrier'])
            total_flights = carrier_df['flight_count'].sum()
            carrier_df['market_share_pct'] = (carrier_df['flight_count'] / total_flights * 100).round(1)

            cheapest_carrier = carrier_df.iloc[0]
            most_expensive_carrier = carrier_df.iloc[-1]
            dominant_carrier = carrier_df.sort_values('flight_count', ascending=False).iloc[0]
            price_spread = most_expensive_carrier['avg_fare'] - cheapest_carrier['avg_fare']

            # 1. KPI Cards Row
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric(
                    label="Lowest Fare Carrier",
                    value=f"₹{cheapest_carrier['avg_fare']:,.0f}",
                    delta=f"{cheapest_carrier['carrier_name']} ({cheapest_carrier['carrier']})",
                    delta_color="normal"
                )
            with c2:
                st.metric(
                    label="Premium Benchmark",
                    value=f"₹{most_expensive_carrier['avg_fare']:,.0f}",
                    delta=f"{most_expensive_carrier['carrier_name']} ({most_expensive_carrier['carrier']})",
                    delta_color="inverse"
                )
            with c3:
                st.metric(
                    label="Inter-Airline Spread",
                    value=f"₹{price_spread:,.0f}",
                    delta="Max Price Differential",
                    delta_color="off"
                )
            with c4:
                st.metric(
                    label="Market Share Leader",
                    value=f"{dominant_carrier['market_share_pct']:.1f}%",
                    delta=f"{dominant_carrier['carrier_name']} ({dominant_carrier['flight_count']:,} Flights)",
                    delta_color="off"
                )

            st.markdown("")

            # 2. Side-by-side Visualizations
            chart_c1, chart_c2 = st.columns(2)
            with chart_c1:
                st.plotly_chart(create_carrier_comparison(carrier_df), use_container_width=True)
            with chart_c2:
                st.plotly_chart(create_carrier_market_share(carrier_df), use_container_width=True)

            # 3. Detailed Statistics Table
            st.markdown("### 📋 Carrier Pricing Matrix & Flight Frequency")
            display_df = carrier_df[['carrier', 'carrier_name', 'avg_fare', 'min_fare', 'max_fare',
                                      'flight_count', 'market_share_pct']].copy()
            display_df['avg_fare'] = display_df['avg_fare'].apply(lambda x: f"₹{x:,.0f}")
            display_df['min_fare'] = display_df['min_fare'].apply(lambda x: f"₹{x:,.0f}")
            display_df['max_fare'] = display_df['max_fare'].apply(lambda x: f"₹{x:,.0f}")
            display_df['market_share_pct'] = display_df['market_share_pct'].apply(lambda x: f"{x:.1f}%")
            display_df.columns = ['Code', 'Airline Name', 'Mean Fare', 'Lowest Observed', 'Peak Observed', 'Flight Count', 'Observed Share']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        else:
            st.info("No carrier flight data available for the selected filters.")

    except Exception as e:
        st.error(f"Error loading carrier data: {str(e)}")
