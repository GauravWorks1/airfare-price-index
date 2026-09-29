"""
filters.py — High-visibility, modern top-bar & sidebar filters for MoSPI Airfare Index.
Provides clean segmented controls, accessible dropdowns, and date pickers.
"""

import streamlit as st
from datetime import date, timedelta
import config

def render_top_filter_bar(key_prefix: str = 'main') -> dict:
    """
    Renders an eye-level, horizontal filter control deck right at the top of the page.
    Drastically improves visibility and usability over hidden sidebar controls.
    """
    st.markdown("""
    <style>
    .filter-panel {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 14px 18px 10px 18px;
        margin-bottom: 22px;
        box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .filter-title {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #475569;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    today = date.today()
    default_start = today - timedelta(days=14)

    st.markdown('<div class="filter-panel"><div class="filter-title">⚡ Interactive Surveillance Filters</div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([2.5, 2, 2, 2.5])
    
    with c1:
        date_range = st.date_input(
            "📅 Date Horizon",
            value=(default_start, today),
            key=f"{key_prefix}_top_date_range",
            help="Select the start and end dates to filter airfare indices"
        )
        if len(date_range) == 2:
            start_date, end_date = date_range[0].strftime('%Y-%m-%d'), date_range[1].strftime('%Y-%m-%d')
        elif len(date_range) == 1:
            start_date, end_date = date_range[0].strftime('%Y-%m-%d'), date_range[0].strftime('%Y-%m-%d')
        else:
            start_date, end_date = None, None

    with c2:
        index_type = st.selectbox(
            "📐 Index Formula",
            options=['LASPEYRES', 'PAASCHE', 'FISHER'],
            index=0,
            key=f"{key_prefix}_top_idx_type",
            help="Laspeyres (Base weighted), Paasche (Current weighted), Fisher (Superlative Ideal)"
        )

    with c3:
        horizon_options = ['All Horizons', 'T+1 Day', 'T+7 Days', 'T+15 Days', 'T+30 Days', 'T+45 Days']
        horizon_map = {'All Horizons': -1, 'T+1 Day': 1, 'T+7 Days': 7, 'T+15 Days': 15, 'T+30 Days': 30, 'T+45 Days': 45}
        selected_h = st.selectbox(
            "⏱️ Advance Window",
            options=horizon_options,
            index=0,
            key=f"{key_prefix}_top_horizon",
            help="Analyze price changes based on how far in advance tickets were booked"
        )
        advance_days = horizon_map[selected_h]

    with c4:
        carrier_options = ['All Airlines (National)'] + [f"{code} — {name}" for code, name in config.CARRIERS.items()]
        selected_c = st.selectbox(
            "✈️ Airline Carrier",
            options=carrier_options,
            index=0,
            key=f"{key_prefix}_top_carrier",
            help="Filter fares by airline operator"
        )
        carrier = None if selected_c == 'All Airlines (National)' else selected_c.split(' — ')[0]

    st.markdown('</div>', unsafe_allow_html=True)

    return {
        'start_date': start_date,
        'end_date': end_date,
        'index_type': index_type,
        'advance_days': advance_days,
        'carrier': carrier
    }


def render_date_filter(key_prefix: str = 'main') -> tuple:
    """Render date range picker in sidebar."""
    today = date.today()
    default_start = today - timedelta(days=14)
    
    date_range = st.sidebar.date_input(
        "📅 Date Window",
        value=(default_start, today),
        key=f"{key_prefix}_date_range"
    )
    
    if len(date_range) == 2:
        return date_range[0].strftime('%Y-%m-%d'), date_range[1].strftime('%Y-%m-%d')
    elif len(date_range) == 1:
        return date_range[0].strftime('%Y-%m-%d'), date_range[0].strftime('%Y-%m-%d')
    return None, None


def render_route_filter(routes: list, key: str = 'route') -> tuple:
    """Render origin/destination dropdowns."""
    origins = sorted(list(set([r[0] for r in routes])))
    dests = sorted(list(set([r[1] for r in routes])))
    
    origin = st.sidebar.selectbox("🛫 Origin City", options=['All Cities'] + origins, key=f"{key}_origin")
    
    if origin != 'All Cities':
        valid_dests = sorted(list(set([r[1] for r in routes if r[0] == origin])))
        dest = st.sidebar.selectbox("🛬 Destination City", options=['All Cities'] + valid_dests, key=f"{key}_dest")
    else:
        dest = st.sidebar.selectbox("🛬 Destination City", options=['All Cities'] + dests, key=f"{key}_dest")
        
    return (None if origin == 'All Cities' else origin, None if dest == 'All Cities' else dest)


def render_carrier_filter(carriers: dict, key: str = 'carrier') -> str:
    """Render carrier dropdown."""
    options = ['All Airlines'] + [f"{code} — {name}" for code, name in carriers.items()]
    selected = st.sidebar.selectbox("✈️ Airline Operator", options=options, key=f"{key}_carrier")
    return None if selected == 'All Airlines' else selected.split(' — ')[0]


def render_advance_days_filter(advance_days: list, key: str = 'adv') -> int:
    """Render advance days dropdown."""
    options = ['All Horizons'] + [f"T+{d} Days" for d in sorted(advance_days)]
    selected = st.sidebar.selectbox("⏱️ Advance Window", options=options, key=f"{key}_adv")
    if selected == 'All Horizons':
        return None
    return int(selected.replace("T+", "").replace(" Days", ""))


def render_index_type_filter(key: str = 'idx') -> str:
    """Render index type radio buttons."""
    return st.sidebar.radio(
        "📐 Index Formula",
        options=['LASPEYRES', 'PAASCHE', 'FISHER'],
        key=f"{key}_idx_type"
    )
