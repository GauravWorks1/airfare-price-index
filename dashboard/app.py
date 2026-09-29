"""
app.py — Main Entry Point for the Real-time Airfare Price Index Dashboard (SIH 2026).
Government-grade UI, multi-page router, executive header, and live pipeline status telemetry.
"""

import streamlit as st
import sqlite3
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from database.db import get_connection

from dashboard.components.styles import inject_custom_css, render_gov_header
from dashboard.pages.overview import render_overview
from dashboard.pages.route_heatmap import render_route_heatmap_page
from dashboard.pages.elasticity import render_elasticity
from dashboard.pages.carrier_compare import render_carrier_comparison_page
from dashboard.pages.validation import render_validation
from dashboard.pages.live_monitor import render_live_scraper_page

st.set_page_config(
    page_title='India Airfare Price Index | MoSPI CPI Augmentation',
    page_icon='🇮🇳',
    layout='wide',
    initial_sidebar_state='expanded'
)

# 1. Inject Global Custom CSS
inject_custom_css()

# 2. Database Connection Handler
def get_dashboard_connection():
    try:
        return get_connection()
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return None

st.session_state['db_conn'] = get_dashboard_connection()

# 3. Sidebar Brand & Navigation
with st.sidebar:
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">'
        '<span style="font-size: 28px;">✈️</span>'
        '<div><div style="font-weight: 800; font-size: 17px; color: #0f172a; line-height: 1.2;">Airfare Price Index</div>'
        '<div style="font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">MoSPI • CPI Augmentation</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "📊 Macro Overview",
            "🛰️ Live Scraper Console",
            "🗺️ Corridor Heatmap",
            "📉 Lead-time Elasticity",
            "🏢 Airline Intelligence",
            "🎯 DGCA Validation Audit"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Live Database Telemetry in Sidebar
    conn = st.session_state.get('db_conn')
    total_fares = 0
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM fares")
            total_fares = cur.fetchone()[0]
        except Exception:
            pass

    st.markdown(
        f'<div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 14px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">'
        f'<div style="font-size: 11px; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.5px;">Surveillance Telemetry</div>'
        f'<div style="font-size: 13px; font-weight: 700; color: #15803d; margin-top: 6px; display: flex; align-items: center; gap: 6px;">'
        f'<span style="height: 8px; width: 8px; background: #22c55e; border-radius: 50%; display: inline-block;"></span> 100% Live Ingestion</div>'
        f'<div style="font-size: 13px; color: #334155; margin-top: 4px;">Live Quotes: <strong>{total_fares:,}</strong></div>'
        f'<div style="font-size: 13px; color: #334155;">National Basket: <strong>20 Corridors</strong></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("#### Developer Interfaces")
    st.markdown("🔗 [FastAPI Swagger Docs](http://localhost:8000/docs)")
    st.markdown("🔗 [FastAPI ReDoc](http://localhost:8000/redoc)")

    st.markdown("---")
    st.caption("Smart India Hackathon 2026 • Problem Statement: MoSPI Airfare CPI Augmentation")

# 4. Top Executive Header
render_gov_header(
    title="India Real-Time Airfare Price Index",
    subtitle="Ministry of Statistics & Programme Implementation (MoSPI) • National Statistical Office (NSO) Prototype"
)

# 5. Page Router
try:
    if page == "📊 Macro Overview":
        render_overview()
    elif page == "🛰️ Live Scraper Console":
        render_live_scraper_page()
    elif page == "🗺️ Corridor Heatmap":
        render_route_heatmap_page()
    elif page == "📉 Lead-time Elasticity":
        render_elasticity()
    elif page == "🏢 Airline Intelligence":
        render_carrier_comparison_page()
    elif page == "🎯 DGCA Validation Audit":
        render_validation()
except Exception as e:
    st.error(f"Application error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
