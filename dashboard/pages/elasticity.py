"""
elasticity.py — Lead-Time Price Elasticity & Booking Horizon Intelligence.
Analyzes fare escalation by advance purchase window, corridor comparisons, and predictive fare calculator.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dashboard.components.charts import create_elasticity_curve
import config

def render_elasticity():
    try:
        routes = getattr(config, 'ROUTES', [('DEL', 'BOM'), ('BOM', 'BLR')])
        city_names = getattr(config, 'CITY_NAMES', {})
        carriers = getattr(config, 'CARRIERS', {})
    except Exception:
        routes = [('DEL', 'BOM')]
        city_names = {}
        carriers = {}

    st.sidebar.markdown("### Corridor Filter")
    route_labels = [f"{r[0]}-{r[1]} ({city_names.get(r[0], r[0])} ➔ {city_names.get(r[1], r[1])})" for r in routes]
    selected_label = st.sidebar.selectbox("Select Focus Route", options=route_labels, key='elasticity_route')
    selected_route_str = selected_label.split(' (')[0]
    origin, dest = selected_route_str.split('-')

    conn = st.session_state.get('db_conn', None)
    if not conn:
        st.warning("⚠️ Database connection unavailable.")
        return

    try:
        query = """
            SELECT advance_days, 
                   AVG(total_fare) as avg_fare, 
                   MIN(total_fare) as min_fare, 
                   MAX(total_fare) as max_fare,
                   COUNT(*) as num_observations
            FROM fares
            WHERE origin = ? AND destination = ?
              AND is_outlier = 0 AND status = 'AVAILABLE'
            GROUP BY advance_days
            ORDER BY advance_days
        """
        elasticity_data = pd.read_sql_query(query, conn, params=[origin, dest])

        if not elasticity_data.empty:
            adv_values = elasticity_data['advance_days'].values
            min_adv = adv_values.min()
            max_adv = adv_values.max()
            fare_early = float(elasticity_data[elasticity_data['advance_days'] == max_adv]['avg_fare'].values[0])
            fare_late = float(elasticity_data[elasticity_data['advance_days'] == min_adv]['avg_fare'].values[0])
            
            savings_pct = ((fare_late - fare_early) / fare_late) * 100 if fare_late > 0 else 0
            surge_multiplier = fare_late / fare_early if fare_early > 0 else 1.0

            # 1. Metric Callout Row
            e1, e2, e3, e4 = st.columns(4)
            with e1:
                st.metric(
                    label=f"T+{min_adv} Last-Minute Fare",
                    value=f"₹{fare_late:,.0f}",
                    delta=f"1 Day Out Surge",
                    delta_color="inverse"
                )
            with e2:
                st.metric(
                    label=f"T+{max_adv} Advance Fare",
                    value=f"₹{fare_early:,.0f}",
                    delta=f"{max_adv} Days Advance Base",
                    delta_color="normal"
                )
            with e3:
                st.metric(
                    label="Advance Booking Savings",
                    value=f"{savings_pct:.1f}%",
                    delta=f"Save ₹{fare_late - fare_early:,.0f} Early",
                    delta_color="normal"
                )
            with e4:
                st.metric(
                    label="Dynamic Surge Factor",
                    value=f"{surge_multiplier:.2f}x",
                    delta="Last-Minute vs Advance",
                    delta_color="off"
                )

            st.markdown("")

            # 2. Main Elasticity Curve
            st.plotly_chart(create_elasticity_curve(elasticity_data), use_container_width=True)

            # 3. Interactive Airfare Cost Estimator Widget
            st.markdown("### 🧮 Interactive Advance Booking Simulator")
            st.markdown("Estimate expected ticket price based on selected advance booking horizon and carrier pricing algorithms.")

            sim_c1, sim_c2 = st.columns([2, 3])
            with sim_c1:
                sim_carrier = st.selectbox("Preferred Airline", options=list(carriers.keys()), format_func=lambda x: f"{x} - {carriers.get(x, x)}", key='sim_carrier')
                sim_days = st.select_slider("Booking Horizon (Days in Advance)", options=[1, 7, 15, 30, 45], value=15, key='sim_days')

                # Estimate fare from DB
                est_q = """
                    SELECT AVG(total_fare) as est_fare, MIN(total_fare) as min_f, MAX(total_fare) as max_f
                    FROM fares
                    WHERE origin = ? AND destination = ? AND carrier = ? AND advance_days = ?
                      AND is_outlier = 0 AND status = 'AVAILABLE'
                """
                est_df = pd.read_sql_query(est_q, conn, params=[origin, dest, sim_carrier, sim_days])
                est_fare = est_df.iloc[0]['est_fare'] if not est_df.empty and pd.notna(est_df.iloc[0]['est_fare']) else (fare_late * 0.7)

            with sim_c2:
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; height: 100%;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Estimated Fare Quote</div>
                    <div style="font-size: 2.25rem; font-weight: 800; color: #0f172a; margin: 0.25rem 0;">₹{est_fare:,.0f}</div>
                    <div style="font-size: 0.85rem; color: #475569; margin-bottom: 0.75rem;">
                        Flying <strong>{origin} ➔ {dest}</strong> on <strong>{carriers.get(sim_carrier, sim_carrier)}</strong> (T+{sim_days} days ahead)
                    </div>
                    <div style="background: rgba(37, 99, 235, 0.08); border-left: 4px solid #2563eb; padding: 0.6rem 0.8rem; border-radius: 4px; font-size: 0.82rem; color: #1e3a8a;">
                        💡 <strong>Economic Insight</strong>: Booking at <strong>T+{sim_days}</strong> avoids approximately 
                        <strong>{max(0.0, ((fare_late - est_fare) / fare_late * 100)):.1f}%</strong> in surge inflation compared to booking on departure eve.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 4. Multi-Route Elasticity Overlay
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            with st.expander("📊 Compare Advance Purchase Curves Across Multiple Corridors"):
                comp_corridors = st.multiselect(
                    "Select routes to overlay",
                    options=[f"{r[0]}-{r[1]}" for r in routes],
                    default=[selected_route_str, 'DEL-BLR'] if 'DEL-BLR' in [f"{r[0]}-{r[1]}" for r in routes] else [selected_route_str]
                )
                if comp_corridors:
                    fig_comp = go.Figure()
                    for r_str in comp_corridors:
                        o_i, d_i = r_str.split('-')
                        rdf = pd.read_sql_query(query, conn, params=[o_i, d_i])
                        if not rdf.empty:
                            fig_comp.add_trace(go.Scatter(
                                x=rdf['advance_days'], 
                                y=rdf['avg_fare'],
                                mode='lines+markers', 
                                name=f"{o_i} ➔ {d_i}",
                                line=dict(width=2.5, shape='spline'),
                                marker=dict(size=8)
                            ))
                    fig_comp.update_layout(
                        title="<b>Corridor Advance Price Curves Overlay</b>",
                        xaxis_title="Advance Booking Horizon (Days Ahead)",
                        yaxis_title="Mean Fare (₹)",
                        template="plotly_white",
                        height=420,
                        yaxis=dict(tickprefix="₹"),
                        legend=dict(orientation="h", y=1.05, x=1)
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)

        else:
            st.info("No elasticity observations found for the selected route.")

    except Exception as e:
        st.error(f"Error loading elasticity: {str(e)}")
