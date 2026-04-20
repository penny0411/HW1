import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import os
import random
from datetime import datetime, timedelta

# ─── Page Configuration ───
st.set_page_config(
    page_title="DHT11 Live Monitor",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp { background-color: #0b0f19; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.5rem !important; max-width: 1200px; }
    .header-container { margin-bottom: 1.2rem; }
    .header-title { color: #ffffff; font-size: 1.6rem; font-weight: 700; display: flex; align-items: center; gap: 10px; }
    .code-badge { background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); color: #94a3b8; padding: 2px 10px; border-radius: 6px; font-size: 0.8rem; }
    .live-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(0, 230, 118, 0.1); border: 1px solid rgba(0, 230, 118, 0.3); color: #00e676; padding: 4px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .live-dot { width: 8px; height: 8px; background: #00e676; border-radius: 50%; animation: blink 1.5s infinite; }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    .metrics-row { display: flex; gap: 16px; margin-bottom: 1.5rem; }
    .metric-card { flex: 1; background: #111827; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center; }
    .metric-label { color: #6b7a99; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; }
    .metric-value { font-size: 2.2rem; font-weight: 700; }
    .temp-color { color: #f59e0b; }
    .humid-color { color: #3b82f6; }
    .chart-section { background: #111827; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 1.2rem 1rem 0.5rem 1rem; margin-top: 20px; }
    .chart-title { color: #94a3b8; font-size: 0.82rem; display: flex; align-items: center; gap: 8px; }
</style>
""", unsafe_allow_html=True)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiotdb.db")

# ─── Data fetching with Auto-Simulation ───
@st.cache_data(ttl=1.5)
def get_sensor_data(limit=60):
    # 嘗試讀取真實資料庫
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            query = f"SELECT timestamp, temperature, humidity FROM sensors ORDER BY id DESC LIMIT {limit}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df.sort_values(by='timestamp').reset_index(drop=True), "Real-time DB"
        except:
            pass

    # 如果沒資料庫或讀取失敗，自動進入模擬模式 (Random Data)
    now = datetime.now()
    data = {
        'timestamp': [now - timedelta(seconds=i*2) for i in range(limit)],
        'temperature': [round(random.uniform(24.0, 28.0), 1) for _ in range(limit)],
        'humidity': [round(random.uniform(50.0, 65.0), 1) for _ in range(limit)]
    }
    df_sim = pd.DataFrame(data).sort_values(by='timestamp').reset_index(drop=True)
    return df_sim, "Simulation Mode"

# ─── Header ───
st.markdown("""
<div class="header-container">
    <div class="header-title">🌡️ DHT11 Cloud Monitor</div>
    <div class="live-badge"><div class="live-dot"></div> LIVE</div>
</div>
""", unsafe_allow_html=True)

# ─── Main Content ───
@st.fragment(run_every=timedelta(seconds=2))
def live_monitor():
    df, mode = get_sensor_data(60)
    
    # 顯示目前模式（小字提示）
    st.caption(f"Status: {mode}")

    latest = df.iloc[-1]
    
    # 數據卡片
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">🌡️ TEMPERATURE</div>
            <div class="metric-value temp-color">{latest['temperature']}°C</div>
        </div>""", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">💧 HUMIDITY</div>
            <div class="metric-value humid-color">{latest['humidity']}%</div>
        </div>""", unsafe_allow_html=True)

    # 溫度圖表
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], line=dict(color='#f59e0b', width=3), fill='tozeroy'))
    fig_temp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
    st.plotly_chart(fig_temp, use_container_width=True)

    # 濕度圖表
    fig_humid = go.Figure()
    fig_humid.add_trace(go.Scatter(x=df['timestamp'], y=df['humidity'], line=dict(color='#3b82f6', width=3), fill='tozeroy'))
    fig_humid.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
    st.plotly_chart(fig_humid, use_container_width=True)

live_monitor()
