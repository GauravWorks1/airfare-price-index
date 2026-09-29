"""
route_heatmap.py — Corridor Pricing Intensity Heatmap for India Airfare Price Index.
Interactive route filtering, dispersion statistics, color scales, and CSV export.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dashboard.components.charts import create_route_heatmap
from dashboard.components.filters import render_date_filter
import config

def render_route_heatmap_page():
    start_date, end_date = render_date_filter('heatmap')

    conn = st.session_state.get('db_conn', None)
    if not conn:
        st.warning("⚠️ Database connection unavailable.")
        return

    try:
        query = """
            SELECT origin, destination, scrape_date, AVG(total_fare) as avg_fare
            FROM fares
            WHERE is_outlier = 0 AND status = 'AVAILABLE'
              AND scrape_date BETWEEN ? AND ?
            GROUP BY origin, destination, scrape_date
            ORDER BY scrape_date
        """
        fares_df = pd.read_sql_query(query, conn, params=[str(start_date), str(end_date)])

        if not fares_df.empty:
            # Corridor statistics
            fares_df['route'] = fares_df['origin'] + ' ➔ ' + fares_df['destination']
            corridor_stats = fares_df.groupby('route')['avg_fare'].agg(['mean', 'min', 'max', 'std']).reset_index()
            corridor_stats = corridor_stats.sort_values('mean', ascending=False)
            
            top_corridor = corridor_stats.iloc[0]
            bottom_corridor = corridor_stats.iloc[-1]
            avg_dispersion = corridor_stats['std'].mean()

            # KPI Summary Row
            k1, k2, k3 = st.columns(3)
            with k1:
                st.metric(
                    label="Highest Fare Corridor",
                    value=f"₹{top_corridor['mean']:,.0f}",
                    delta=f"{top_corridor['route']} (Peak Corridor)",
                    delta_color="inverse"
                )
            with k2:
                st.metric(
                    label="Lowest Fare Corridor",
                    value=f"₹{bottom_corridor['mean']:,.0f}",
                    delta=f"{bottom_corridor['route']} (Best Economy)",
                    delta_color="normal"
                )
            with k3:
                st.metric(
                    label="Average Corridor Volatility",
                    value=f"₹{avg_dispersion:,.0f}",
                    delta="Daily Price Standard Deviation",
                    delta_color="off"
                )

            st.markdown("")

            # Main Heatmap
            st.plotly_chart(create_route_heatmap(fares_df), use_container_width=True)

            # Route Ranking Tables
            st.markdown("### 📊 Corridor Fare Dispersion & Rankings")
            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("#### 🔺 Top 5 Premium Corridors")
                top5 = corridor_stats.head(5).copy()
                top5['mean'] = top5['mean'].apply(lambda x: f"₹{x:,.0f}")
                top5['min'] = top5['min'].apply(lambda x: f"₹{x:,.0f}")
                top5['max'] = top5['max'].apply(lambda x: f"₹{x:,.0f}")
                top5['std'] = top5['std'].apply(lambda x: f"±₹{x:,.0f}" if pd.notna(x) else "—")
                top5.columns = ['Corridor', 'Mean Fare', 'Min Seen', 'Max Seen', 'Volatility']
                st.dataframe(top5, use_container_width=True, hide_index=True)

            with col_right:
                st.markdown("#### 🔻 Top 5 Affordable Corridors")
                bot5 = corridor_stats.tail(5).copy()
                bot5['mean'] = bot5['mean'].apply(lambda x: f"₹{x:,.0f}")
                bot5['min'] = bot5['min'].apply(lambda x: f"₹{x:,.0f}")
                bot5['max'] = bot5['max'].apply(lambda x: f"₹{x:,.0f}")
                bot5['std'] = bot5['std'].apply(lambda x: f"±₹{x:,.0f}" if pd.notna(x) else "—")
                bot5.columns = ['Corridor', 'Mean Fare', 'Min Seen', 'Max Seen', 'Volatility']
                st.dataframe(bot5, use_container_width=True, hide_index=True)

            # Download CSV capability
            csv_data = corridor_stats.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Corridor Fare Summary (CSV)",
                data=csv_data,
                file_name=f"airfare_corridor_stats_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
        else:
            st.info("No pricing records found for the selected date range.")

    except Exception as e:
        st.error(f"Error loading heatmap: {str(e)}")
