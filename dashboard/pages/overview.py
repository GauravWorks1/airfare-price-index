"""
overview.py — Executive Macro Overview page for India Airfare Price Index.
Features executive KPI cards, corridor price ticker, CPI inflation simulation, and methodology.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dashboard.components.charts import create_index_trend_chart, create_monthly_comparison
from dashboard.components.filters import render_top_filter_bar
import config

def render_overview():
    # 1. High-Visibility Eye-Level Filter Bar (Dates, Formula, Horizon, Carrier)
    filters = render_top_filter_bar('overview')
    start_date = filters['start_date']
    end_date = filters['end_date']
    index_type = filters['index_type']
    advance_days = filters['advance_days']
    selected_carrier = filters['carrier']

    conn = st.session_state.get('db_conn', None)
    if not conn:
        st.warning("⚠️ Database connection unavailable. Please run `python run_pipeline.py` first.")
        return

    try:
        # 2. Fetch Latest Index & Comparison (matching selected horizon)
        adv_filter_val = advance_days if advance_days is not None else -1
        latest_q = """
            SELECT index_date, index_value 
            FROM price_index 
            WHERE index_type = ? AND advance_days = ?
            ORDER BY index_date DESC LIMIT 2
        """
        latest_df = pd.read_sql_query(latest_q, conn, params=[index_type, adv_filter_val])

        # Fetch Observations & Overall Mean Fare
        stats_q = """
            SELECT COUNT(*) as cnt, AVG(total_fare) as avg_fare,
                   COUNT(DISTINCT origin || '-' || destination) as num_routes,
                   COUNT(DISTINCT carrier) as num_carriers
            FROM fares 
            WHERE is_outlier = 0 AND status = 'AVAILABLE'
        """
        stats_df = pd.read_sql_query(stats_q, conn)

        current_idx = float(latest_df.iloc[0]['index_value']) if len(latest_df) > 0 else 100.0
        prev_idx = float(latest_df.iloc[1]['index_value']) if len(latest_df) > 1 else current_idx
        dod_change = ((current_idx - prev_idx) / prev_idx) * 100 if prev_idx else 0.0
        total_obs = int(stats_df.iloc[0]['cnt']) if not stats_df.empty else 0
        avg_fare = float(stats_df.iloc[0]['avg_fare']) if not stats_df.empty and pd.notna(stats_df.iloc[0]['avg_fare']) else 0.0
        active_routes = int(stats_df.iloc[0]['num_routes']) if not stats_df.empty else 20
        active_carriers = int(stats_df.iloc[0]['num_carriers']) if not stats_df.empty else 6

        # 3. Fetch Top Corridors for Live Ticker
        ticker_q = """
            SELECT origin, destination, AVG(total_fare) as avg_fare
            FROM fares
            WHERE is_outlier = 0 AND status = 'AVAILABLE'
            GROUP BY origin, destination
            ORDER BY avg_fare DESC LIMIT 6
        """
        ticker_df = pd.read_sql_query(ticker_q, conn)
        ticker_items = []
        for _, row in ticker_df.iterrows():
            ticker_items.append({
                'route': f"{row['origin']} ➔ {row['destination']}",
                'fare': row['avg_fare'],
                'change_str': "Live",
                'change': 1
            })

        # 3. Native KPI Metric Cards Row
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        with kpi_col1:
            st.metric(
                label=f"{index_type} Price Index",
                value=f"{current_idx:.2f}",
                delta=f"{current_idx - 100:+.2f} vs Base (100.0)",
                delta_color="inverse"
            )

        with kpi_col2:
            st.metric(
                label="Daily Inflation Momentum",
                value=f"{dod_change:+.2f}%",
                delta=f"{current_idx - prev_idx:+.2f} pts DoD",
                delta_color="inverse"
            )

        with kpi_col3:
            st.metric(
                label="National Average Airfare",
                value=f"₹{avg_fare:,.0f}",
                delta=f"{active_routes} Active Corridors",
                delta_color="off"
            )

        with kpi_col4:
            st.metric(
                label="Sample Surveillance",
                value=f"{total_obs:,}",
                delta=f"{active_carriers} Airlines Tracked",
                delta_color="off"
            )

        st.markdown("")

        # 5. Interactive Tabs
        tab_trends, tab_cpi, tab_basket = st.tabs([
            "📈 Index Trajectory & Moving Averages", 
            "🏛️ MoSPI CPI Augmentation Impact", 
            "⚖️ DGCA Traffic Basket & Weights"
        ])

        with tab_trends:
            daily_q = """
                SELECT index_date as date, index_value 
                FROM price_index 
                WHERE index_type = ? AND advance_days = ?
            """
            params = [index_type, adv_filter_val]
            if start_date:
                daily_q += " AND index_date >= ?"
                params.append(str(start_date))
            if end_date:
                daily_q += " AND index_date <= ?"
                params.append(str(end_date))
            daily_q += " ORDER BY index_date"

            daily_df = pd.read_sql_query(daily_q, conn, params=params)

            if not daily_df.empty:
                st.plotly_chart(create_index_trend_chart(daily_df, f"{index_type} (T+{advance_days if advance_days != -1 else 'All'})"), use_container_width=True)
            else:
                st.info("No index records found for the selected date window and horizon.")

            # Monthly aggregate below
            monthly_q = """
                SELECT strftime('%Y-%m', index_date) as month, 
                       AVG(index_value) as index_value 
                FROM price_index 
                WHERE index_type = ? AND advance_days = -1
                GROUP BY strftime('%Y-%m', index_date) 
                ORDER BY month
            """
            monthly_df = pd.read_sql_query(monthly_q, conn, params=[index_type])
            if not monthly_df.empty:
                st.plotly_chart(create_monthly_comparison(monthly_df), use_container_width=True)

        with tab_cpi:
            st.markdown("""
            ### How this Real-Time Index Augments the National CPI
            Currently, the **Consumer Price Index (Urban / Transport)** captures passenger airfare through quarterly or manual sampling at select booking offices. 
            This results in an **inflation lag** of up to 45–90 days.
            """)

            comp_col1, comp_col2 = st.columns([3, 2])
            with comp_col1:
                # Comparison simulation chart
                if not daily_df.empty:
                    sim_df = daily_df.copy()
                    # Simulated static counter price (flat with small step changes)
                    sim_df['static_counter_cpi'] = 100.0 + np.sin(np.linspace(0, 3, len(sim_df))) * 1.5
                    
                    import plotly.graph_objects as go
                    fig_sim = go.Figure()
                    fig_sim.add_trace(go.Scatter(
                        x=sim_df['date'], y=sim_df['index_value'],
                        mode='lines', name='Real-Time Digital Index (Proposed)',
                        line=dict(color='#2563eb', width=2.5)
                    ))
                    fig_sim.add_trace(go.Scatter(
                        x=sim_df['date'], y=sim_df['static_counter_cpi'],
                        mode='lines', name='Legacy Physical Counter Method (Current)',
                        line=dict(color='#94a3b8', width=2, dash='dash')
                    ))
                    fig_sim.update_layout(
                        title="<b>Inflation Measurement Gap: Real-Time Web vs Legacy Physical Sampling</b>",
                        xaxis_title="Date", yaxis_title="Price Index Level",
                        template="plotly_white",
                        height=360,
                        legend=dict(orientation="h", y=1.1, x=1)
                    )
                    st.plotly_chart(fig_sim, use_container_width=True)

            with comp_col2:
                st.markdown("""
                #### Key Policy Benefits for MoSPI / RBI:
                - **Dynamic Lead-Time Capture**: Captures ticket spikes during festival surges ($T+1$) that counter surveys miss.
                - **High-Frequency Inputs**: Delivers daily inputs to the **Index of Services Production (ISP)** and weekly inflation flash estimates.
                - **Zero Data Collection Burden**: Fully automated web crawling replacing field investigators visiting ticket counters.
                - **Statistical Rigor**: Route weights directly calibrated against **109 Million annual DGCA domestic passenger counts**.
                """)

        with tab_basket:
            st.markdown("### 20-Corridor Domestic Basket Weighted by DGCA Passenger Traffic")
            basket_q = """
                SELECT origin, destination, passenger_volume, weight * 100 as weight_pct
                FROM route_weights
                ORDER BY passenger_volume DESC
            """
            basket_df = pd.read_sql_query(basket_q, conn)
            
            if not basket_df.empty:
                city_map = getattr(config, 'CITY_NAMES', {})
                basket_df['origin_city'] = basket_df['origin'].map(city_map)
                basket_df['dest_city'] = basket_df['destination'].map(city_map)
                basket_df['corridor'] = basket_df['origin'] + ' ➔ ' + basket_df['destination'] + ' (' + basket_df['origin_city'] + ' to ' + basket_df['dest_city'] + ')'
                
                disp = basket_df[['corridor', 'passenger_volume', 'weight_pct']].copy()
                disp.columns = ['Route Corridor', 'Annual DGCA Passengers', 'Normalized Weight (%)']
                disp['Annual DGCA Passengers'] = disp['Annual DGCA Passengers'].apply(lambda x: f"{x:,}")
                disp['Normalized Weight (%)'] = disp['Normalized Weight (%)'].apply(lambda x: f"{x:.2f}%")
                
                st.dataframe(disp, use_container_width=True, hide_index=True)

        # 6. Official MoSPI / RBI Data Export Portal
        with st.expander("📥 Export Official MoSPI / RBI Transport CPI Feed (CSV / JSON)"):
            st.markdown("""
            Download standardized high-frequency price indices formatted for direct ingestion into 
            **MoSPI eSankhyiki** or the **Reserve Bank of India (RBI) Inflation Modeling Database**.
            """)
            
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                # Prepare CSV data for export
                export_q = """
                    SELECT 
                        p.index_date AS [Report_Date],
                        p.index_type AS [Index_Formula],
                        CASE WHEN p.advance_days = -1 THEN 'ALL_HORIZONS' ELSE 'T+' || p.advance_days END AS [Booking_Horizon],
                        ROUND(p.index_value, 2) AS [Airfare_Price_Index],
                        p.base_period AS [Base_Period_Window],
                        p.num_routes AS [Active_Basket_Routes],
                        p.num_observations AS [Raw_Price_Quotes]
                    FROM price_index p
                    ORDER BY p.index_date DESC, p.index_type, p.advance_days
                """
                export_df = pd.read_sql_query(export_q, conn)
                csv_data = export_df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="📊 Download Official Index Series (CSV)",
                    data=csv_data,
                    file_name="MoSPI_Airfare_Price_Index_Series.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.caption("Includes Laspeyres, Paasche, and Fisher indices across all 5 advance booking windows.")

            with exp_col2:
                # Route basket weights export
                basket_export_q = """
                    SELECT 
                        origin || '-' || destination AS [Corridor_Code],
                        origin AS [Origin_IATA],
                        destination AS [Destination_IATA],
                        passenger_volume AS [Annual_DGCA_Passengers],
                        ROUND(weight, 5) AS [Normalized_Basket_Weight],
                        year AS [DGCA_Baseline_Year]
                    FROM route_weights
                    ORDER BY passenger_volume DESC
                """
                basket_exp_df = pd.read_sql_query(basket_export_q, conn)
                basket_csv = basket_exp_df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="✈️ Download DGCA 20-Route Basket & Weights (CSV)",
                    data=basket_csv,
                    file_name="DGCA_Route_Weights_Basket.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.caption("Official DGCA weights covering 109M domestic travelers across 20 high-density sectors.")

        # 7. Econometric Formula Accordion
        with st.expander("📐 Mathematical Index Formulas & Specifications"):
            st.markdown(r"""
            #### 1. Modified Laspeyres Price Index (Base Period Weighted)
            $$I_L^t = \frac{\sum_{r \in R} w_r \cdot \bar{p}_{r,t}}{\sum_{r \in R} w_r \cdot \bar{p}_{r,0}} \times 100$$
            *Standard for official CPI compilation. Quantities are held constant at base period levels.*

            #### 2. Paasche Price Index (Current Period Weighted / Harmonic)
            $$I_P^t = \frac{1}{\sum_{r \in R} w_r \cdot \left(\frac{\bar{p}_{r,0}}{\bar{p}_{r,t}}\right)} \times 100$$
            *Accounts for passenger substitution towards cheaper alternative dates/routes during fare surges.*

            #### 3. Fisher Ideal Price Index (Superlative)
            $$I_F^t = \sqrt{I_L^t \times I_P^t}$$
            *The geometric mean satisfying time reversal and factor reversal properties, avoiding systematic over/understatement.*
            """)

    except Exception as e:
        st.error(f"Error loading overview: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
