"""
charts.py — Enterprise Plotly visualization components for India Airfare Price Index.
Polished typography, customized hover templates, clean palettes, and rich interactive styling.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

TEMPLATE = 'plotly_white'

# Enterprise Color Palette
PALETTE = {
    'primary': '#2563eb',       # Cobalt
    'secondary': '#059669',     # Emerald
    'accent': '#d97706',        # Amber
    'purple': '#7c3aed',        # Violet
    'rose': '#e11d48',          # Rose
    'slate': '#64748b',         # Muted Slate
    'grid': '#f1f5f9',          # Subtle gridline
    'card_bg': '#ffffff'
}

def apply_chart_styling(fig: go.Figure, title: str = "", height: int = 440) -> go.Figure:
    """Applies modern minimalist styling, polished fonts, and clean padding to any Plotly figure."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=16, family="Plus Jakarta Sans, sans-serif", color="#0f172a"),
            x=0.01,
            y=0.96
        ),
        template=TEMPLATE,
        height=height,
        margin=dict(l=20, r=20, t=50, b=30),
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#334155"),
        hoverlabel=dict(
            bgcolor="#0f172a",
            font_size=12,
            font_family="Plus Jakarta Sans, sans-serif",
            font_color="#ffffff",
            bordercolor="rgba(255,255,255,0.1)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#475569")
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=PALETTE['grid'],
            linecolor='#cbd5e1',
            tickfont=dict(size=11, color='#64748b')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=PALETTE['grid'],
            linecolor='#cbd5e1',
            tickfont=dict(size=11, color='#64748b')
        )
    )
    return fig

def create_index_trend_chart(daily_df: pd.DataFrame, index_type: str = 'LASPEYRES') -> go.Figure:
    """Area + Line chart of the daily airfare price index with 7-day moving average and base line."""
    fig = go.Figure()
    if daily_df.empty:
        return fig

    # 1. Base 100 benchmark reference line
    fig.add_hline(
        y=100, 
        line_dash="dot", 
        line_color="#94a3b8",
        line_width=1.5,
        annotation_text="Base Benchmark (100.0)", 
        annotation_position="bottom right",
        annotation_font=dict(size=11, color="#64748b")
    )

    # 2. Main Daily Index Area with gradient fill
    fig.add_trace(go.Scatter(
        x=daily_df['date'], 
        y=daily_df['index_value'],
        mode='lines', 
        name=f'{index_type} Index (Daily)',
        line=dict(color=PALETTE['primary'], width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(37, 99, 235, 0.07)',
        hovertemplate='<b>Date</b>: %{x|%b %d, %Y}<br><b>Index Value</b>: %{y:.2f}<extra></extra>'
    ))

    # 3. 7-Day Moving Average
    if len(daily_df) >= 7:
        weekly_ma = daily_df['index_value'].rolling(window=7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=daily_df['date'], 
            y=weekly_ma,
            mode='lines', 
            name='7-Day Moving Avg',
            line=dict(color=PALETTE['accent'], width=2.2, dash='dash', shape='spline'),
            hovertemplate='<b>7-Day MA</b>: %{y:.2f}<extra></extra>'
        ))

    apply_chart_styling(fig, f"High-Frequency Airfare Inflation Index ({index_type})", height=450)
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True, thickness=0.06, bgcolor="#f8fafc"),
            type="date"
        ),
        hovermode='x unified'
    )
    return fig

def create_route_heatmap(fares_df: pd.DataFrame) -> go.Figure:
    """Pricing matrix heatmap across routes and scrape dates."""
    if fares_df.empty:
        return go.Figure()

    df = fares_df.copy()
    df['route'] = df['origin'] + ' ➔ ' + df['destination']
    
    date_col = 'scrape_date' if 'scrape_date' in df.columns else 'date'
    fare_col = 'avg_fare' if 'avg_fare' in df.columns else 'total_fare'
    
    pivot = df.pivot_table(index='route', columns=date_col, values=fare_col, aggfunc='mean')

    fig = px.imshow(
        pivot,
        color_continuous_scale='Blues',
        aspect='auto',
        labels=dict(x="Scrape Date", y="Route Corridor", color="Avg Fare (₹)")
    )
    
    fig.update_traces(
        hovertemplate='<b>Corridor</b>: %{y}<br><b>Date</b>: %{x}<br><b>Avg Fare</b>: ₹%{z:,.0f}<extra></extra>'
    )
    
    apply_chart_styling(fig, "Corridor-Wise Airfare Heatmap Matrix", height=520)
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Avg Fare (₹)",
            thickness=14,
            len=0.8,
            tickprefix="₹"
        )
    )
    return fig

def create_elasticity_curve(elasticity_data: pd.DataFrame) -> go.Figure:
    """Line+scatter with shaded confidence ribbon illustrating price vs advance booking window."""
    fig = go.Figure()
    if elasticity_data.empty:
        return fig

    # 1. Shaded Min-Max Price Band
    if 'max_fare' in elasticity_data.columns and 'min_fare' in elasticity_data.columns:
        fig.add_trace(go.Scatter(
            x=elasticity_data['advance_days'], y=elasticity_data['max_fare'],
            mode='lines', line=dict(width=0), showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=elasticity_data['advance_days'], y=elasticity_data['min_fare'],
            mode='lines', fill='tonexty', fillcolor='rgba(37, 99, 235, 0.12)',
            line=dict(width=0), name='Observed Price Range',
            hoverinfo='skip'
        ))

    # 2. Average Fare Curve
    fig.add_trace(go.Scatter(
        x=elasticity_data['advance_days'], 
        y=elasticity_data['avg_fare'],
        mode='lines+markers', 
        name='Mean Corridor Fare',
        line=dict(color=PALETTE['primary'], width=3.5, shape='spline'),
        marker=dict(size=9, color=PALETTE['primary'], line=dict(width=2, color='#ffffff')),
        hovertemplate='<b>Booking Horizon</b>: T+%{x} Days<br><b>Mean Fare</b>: ₹%{y:,.0f}<extra></extra>'
    ))

    apply_chart_styling(fig, "Lead-Time Price Elasticity Curve", height=420)
    fig.update_layout(
        xaxis_title="Advance Booking Horizon (Days Ahead of Flight)",
        yaxis_title="Average Ticket Fare (INR ₹)",
        yaxis=dict(tickprefix="₹")
    )
    return fig

def create_carrier_comparison(carrier_df: pd.DataFrame) -> go.Figure:
    """Color-coded bar chart comparing carrier fare averages with value labels."""
    if carrier_df.empty:
        return go.Figure()

    df = carrier_df.sort_values('avg_fare', ascending=True).copy()
    label_col = 'carrier_name' if 'carrier_name' in df.columns else 'carrier'

    colors = [PALETTE['primary'], PALETTE['secondary'], PALETTE['purple'], PALETTE['accent'], PALETTE['rose'], PALETTE['slate']]

    fig = px.bar(
        df, 
        x=label_col, 
        y='avg_fare',
        color=label_col,
        color_discrete_sequence=colors,
        text='avg_fare'
    )
    
    fig.update_traces(
        texttemplate='₹%{text:,.0f}',
        textposition='outside',
        textfont=dict(size=12, weight='bold'),
        hovertemplate='<b>Airline</b>: %{x}<br><b>Mean Fare</b>: ₹%{y:,.0f}<extra></extra>',
        marker=dict(line=dict(width=0))
    )
    
    apply_chart_styling(fig, "Airline Price Competitiveness", height=400)
    fig.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Average Fare (₹)",
        yaxis=dict(tickprefix="₹")
    )
    return fig

def create_carrier_market_share(carrier_df: pd.DataFrame) -> go.Figure:
    """Donut chart illustrating carrier market share by flight frequencies."""
    if carrier_df.empty:
        return go.Figure()

    label_col = 'carrier_name' if 'carrier_name' in carrier_df.columns else 'carrier'
    count_col = 'flight_count' if 'flight_count' in carrier_df.columns else 'num_flights'

    colors = [PALETTE['primary'], PALETTE['secondary'], PALETTE['purple'], PALETTE['accent'], PALETTE['rose'], PALETTE['slate']]

    fig = px.pie(
        carrier_df, 
        names=label_col, 
        values=count_col,
        hole=0.55,
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='outside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Observed Flights: %{value}<br>Share: %{percent}<extra></extra>',
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    
    # Add center KPI annotation
    total_flights = carrier_df[count_col].sum()
    fig.add_annotation(
        text=f"<b>{total_flights:,}</b><br><span style='font-size:11px; color:#64748b;'>Flights</span>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="#0f172a")
    )

    apply_chart_styling(fig, "Observed Flight Capacity Share", height=400)
    fig.update_layout(showlegend=False)
    return fig

def create_validation_scatter(backtest_df: pd.DataFrame) -> go.Figure:
    """Scatter chart comparing index fares against DGCA benchmarks with a 45° agreement line."""
    if backtest_df.empty:
        return go.Figure()

    df = backtest_df.copy()
    df['route'] = df['origin'] + ' ➔ ' + df['destination']

    fig = px.scatter(
        df, 
        x='dgca_avg_fare', 
        y='our_avg_fare', 
        color='route',
        hover_data=['route', 'month', 'pct_error']
    )

    fig.update_traces(
        marker=dict(size=10, opacity=0.85, line=dict(width=1, color='#ffffff')),
        hovertemplate='<b>Route</b>: %{customdata[0]}<br><b>Month</b>: %{customdata[1]}<br><b>DGCA Benchmark</b>: ₹%{x:,.0f}<br><b>Computed Index</b>: ₹%{y:,.0f}<br><b>Deviation</b>: %{customdata[2]:.1f}%<extra></extra>'
    )

    # 45-degree reference line
    all_vals = pd.concat([df['dgca_avg_fare'], df['our_avg_fare']]).dropna()
    if not all_vals.empty:
        max_val = float(all_vals.max()) * 1.1
        min_val = float(all_vals.min()) * 0.9
        fig.add_trace(go.Scatter(
            x=[min_val, max_val], 
            y=[min_val, max_val],
            mode='lines', 
            name='Ideal Parity (y = x)',
            line=dict(color='#dc2626', dash='dot', width=1.5),
            hoverinfo='skip'
        ))

    apply_chart_styling(fig, "Index Fares vs Official DGCA Tariff Benchmarks", height=460)
    fig.update_layout(
        xaxis_title="DGCA Official Reported Fare (INR ₹)",
        yaxis_title="Model Computed Average Fare (INR ₹)",
        xaxis=dict(tickprefix="₹"),
        yaxis=dict(tickprefix="₹")
    )
    return fig

def create_monthly_comparison(monthly_df: pd.DataFrame) -> go.Figure:
    """Bar chart comparing aggregated monthly index levels."""
    if monthly_df.empty:
        return go.Figure()

    fig = px.bar(
        monthly_df, 
        x='month', 
        y='index_value',
        text='index_value',
        color='index_value',
        color_continuous_scale='Blues'
    )
    
    fig.update_traces(
        texttemplate='%{text:.2f}', 
        textposition='outside',
        textfont=dict(weight='bold'),
        hovertemplate='<b>Month</b>: %{x}<br><b>Index Level</b>: %{y:.2f}<extra></extra>'
    )
    
    fig.add_hline(
        y=100, 
        line_dash="dot", 
        line_color="#94a3b8",
        annotation_text="Base (100.0)", 
        annotation_position="bottom right"
    )

    apply_chart_styling(fig, "Monthly Aggregated Airfare Price Index (for CPI Integration)", height=380)
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Calendar Month",
        yaxis_title="Index Level (Base = 100)"
    )
    return fig
