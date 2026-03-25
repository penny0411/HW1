import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import timedelta

# ─── Page Configuration ───
st.set_page_config(
    page_title="DHT11 Live Monitor",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS to match dark navy theme ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Hide Streamlit default elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* Dark navy background */
    .stApp {
        background-color: #0b0f19;
        font-family: 'Inter', sans-serif;
    }

    /* Remove default padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        max-width: 1200px;
    }

    /* ─── Header ─── */
    .header-container {
        margin-bottom: 1.2rem;
    }
    .header-title {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .header-subtitle {
        color: #6b7a99;
        font-size: 0.9rem;
        margin: 6px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .code-badge {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #94a3b8;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-family: 'Courier New', monospace;
        font-weight: 500;
    }
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 230, 118, 0.1);
        border: 1px solid rgba(0, 230, 118, 0.3);
        color: #00e676;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .live-dot {
        width: 8px;
        height: 8px;
        background: #00e676;
        border-radius: 50%;
        animation: blink 1.5s infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* ─── Metric Cards ─── */
    .metrics-row {
        display: flex;
        gap: 16px;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        flex: 1;
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .metric-label {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        color: #6b7a99;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 10px;
    }
    .metric-label-icon {
        font-size: 0.8rem;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .metric-sub {
        color: #4a5568;
        font-size: 0.78rem;
        margin-top: 6px;
    }
    .temp-color { color: #f59e0b; }
    .humid-color { color: #3b82f6; }
    .avg-temp-color { color: #f59e0b; }
    .avg-humid-color { color: #06b6d4; }

    /* ─── Chart Section ─── */
    .chart-section {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.2rem 1rem 0.5rem 1rem;
        margin-bottom: 1.2rem;
    }
    .chart-title {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 0 0 0 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chart-title-dot {
        width: 10px;
        height: 10px;
        border-radius: 3px;
        display: inline-block;
    }
    .dot-temp { background: #f59e0b; }
    .dot-humid { background: #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ─── Database path ───
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiotdb.db")

# ─── Data fetching ───
@st.cache_data(ttl=1.5)
def get_sensor_data(limit=60):
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"""
            SELECT id, timestamp, temperature, humidity 
            FROM sensors ORDER BY id DESC LIMIT {limit}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()

# ─── Header ───
st.markdown("""
<div class="header-container">
    <div class="header-title">🌡️ DHT11 Live Monitor</div>
    <div class="header-subtitle">
        Real-time temperature & humidity —
        <span class="code-badge">aiotdb.db</span>
        <span class="code-badge">sensors</span>
    </div>
    <div class="live-badge"><div class="live-dot"></div> LIVE</div>
</div>
""", unsafe_allow_html=True)

# ─── Auto-refreshing fragment ───
@st.fragment(run_every=timedelta(seconds=2))
def live_monitor():
    df = get_sensor_data(60)

    if df.empty:
        st.warning("⏳ Waiting for sensor data... Run `python dht11_simulator.py` to start generating data.")
        return

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    temp_avg = round(df['temperature'].mean(), 1)
    temp_max = round(df['temperature'].max(), 1)
    humid_avg = round(df['humidity'].mean(), 1)
    humid_max = round(df['humidity'].max(), 1)

    # ─── Metric Cards (4 columns) ───
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-card">
            <div class="metric-label"><span class="metric-label-icon">🌡️</span> TEMPERATURE</div>
            <div class="metric-value temp-color">{latest['temperature']}°C</div>
            <div class="metric-sub">Prev: {prev['temperature']} °C</div>
        </div>
        <div class="metric-card">
            <div class="metric-label"><span class="metric-label-icon">💧</span> HUMIDITY</div>
            <div class="metric-value humid-color">{latest['humidity']}%</div>
            <div class="metric-sub">Prev: {prev['humidity']} %</div>
        </div>
        <div class="metric-card">
            <div class="metric-label"><span class="metric-label-icon">📊</span> TEMP AVG / MAX</div>
            <div class="metric-value avg-temp-color">{temp_avg}° / {temp_max}°</div>
            <div class="metric-sub">Last {len(df)} readings</div>
        </div>
        <div class="metric-card">
            <div class="metric-label"><span class="metric-label-icon">📊</span> HUM AVG / MAX</div>
            <div class="metric-value avg-humid-color">{humid_avg}% / {humid_max}%</div>
            <div class="metric-sub">Last {len(df)} readings</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Temperature Chart ───
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=df['timestamp'], y=df['temperature'],
        mode='lines',
        line=dict(color='#f59e0b', width=2, shape='linear'),
        fill='tozeroy',
        fillcolor='rgba(245, 158, 11, 0.08)',
        hovertemplate='<b>%{x|%H:%M:%S}</b><br>Temperature: %{y:.1f}°C<extra></extra>'
    ))
    fig_temp.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4a5568', size=11),
        xaxis=dict(
            showgrid=False,
            tickformat='%H:%M:%S',
            linecolor='rgba(255,255,255,0.05)',
            tickfont=dict(color='#4a5568'),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.04)',
            ticksuffix=' °C',
            tickfont=dict(color='#4a5568'),
            range=[0, 50],
        ),
        height=300,
        margin=dict(l=50, r=20, t=10, b=40),
        showlegend=False,
        hovermode='x unified',
    )
    st.markdown("""
    <div class="chart-section">
        <div class="chart-title"><span class="chart-title-dot dot-temp"></span> Temperature (°C)</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_temp, use_container_width=True, key="temp_chart",
                    config={'displayModeBar': False})

    # ─── Humidity Chart ───
    fig_humid = go.Figure()
    fig_humid.add_trace(go.Scatter(
        x=df['timestamp'], y=df['humidity'],
        mode='lines+markers',
        line=dict(color='#3b82f6', width=2, shape='linear'),
        marker=dict(size=5, color='#3b82f6', symbol='triangle-up'),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.06)',
        hovertemplate='<b>%{x|%H:%M:%S}</b><br>Humidity: %{y:.1f}%<extra></extra>'
    ))
    fig_humid.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4a5568', size=11),
        xaxis=dict(
            showgrid=False,
            tickformat='%H:%M:%S',
            linecolor='rgba(255,255,255,0.05)',
            tickfont=dict(color='#4a5568'),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.04)',
            ticksuffix=' %',
            tickfont=dict(color='#4a5568'),
            range=[0, 100],
        ),
        height=300,
        margin=dict(l=50, r=20, t=10, b=40),
        showlegend=False,
        hovermode='x unified',
    )
    st.markdown("""
    <div class="chart-section">
        <div class="chart-title"><span class="chart-title-dot dot-humid"></span> Humidity (%RH)</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_humid, use_container_width=True, key="humid_chart",
                    config={'displayModeBar': False})

# ─── Run ───
live_monitor()
