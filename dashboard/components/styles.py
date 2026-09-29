"""
styles.py — Clean, robust UI styling for the Airfare Price Index Dashboard.
Eliminates brittle multi-line HTML indentation that causes Markdown code block leakage.
"""

import streamlit as st

def inject_custom_css():
    """Injects clean modern typography and removes Streamlit excess padding."""
    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
}

/* Cleaner header spacing */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
    max-width: 95% !important;
}

/* Metric styling */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
}

div[data-testid="stMetricLabel"] {
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #475569;
}

div[data-testid="stMetricValue"] {
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f172a;
}

/* Selectbox and Input styling */
div[data-baseweb="select"] {
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    font-weight: 500;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background-color: #f1f5f9;
    padding: 0.4rem;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.9rem;
    color: #475569;
    border: none;
    padding: 0 1.2rem;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #ffffff !important;
    color: #1d4ed8 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
</style>
"""
    st.markdown(css.strip(), unsafe_allow_html=True)

def render_gov_header(title="Real-Time Airfare Price Index", subtitle="MoSPI / National Statistical Office (NSO) • High-Frequency Inflation Monitoring Prototype"):
    """Renders a clean top banner with title, badges and zero indented markdown."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 🇮🇳 {title}")
        st.caption(subtitle)
    with col2:
        st.markdown(
            '<div style="text-align: right; padding-top: 8px;">'
            '<span style="background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; margin-right: 6px;">● LIVE FEED</span>'
            '<span style="background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600;">SIH 2026</span>'
            '</div>',
            unsafe_allow_html=True
        )
    st.divider()
