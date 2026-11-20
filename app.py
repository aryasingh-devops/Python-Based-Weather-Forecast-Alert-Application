"""Weather Forecast & Alert Application - Streamlit Interactive Web Dashboard.

Provides an industry-standard meteorological control center:
- Live Public Weather API (Open-Meteo zero-key)
- Live OpenWeatherMap API
- Virtual Simulation Test Lab with extreme weather scenarios
- Real-time Alert Threshold adjustment
- Interactive Plotly & Matplotlib trend charts
- Automated Report Generation & Instant Download center
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image

from src.config import DEFAULT_THRESHOLDS, OPENWEATHER_API_KEY, HISTORICAL_LOG_PATH
from src.api_client import WeatherAPIClient
from src.parser import WeatherParser
from src.alert_engine import AlertEngine
from src.visualizer import WeatherVisualizer
from src.reporter import WeatherReporter

# Page Configuration
st.set_page_config(
    page_title="Weather Forecast & Risk Alert Control Center",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stAlert {
        border-radius: 10px;
    }
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-critical { background-color: #EF4444; color: white; }
    .badge-warning { background-color: #F59E0B; color: black; }
    .badge-advisory { background-color: #3B82F6; color: white; }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------
st.sidebar.image("https://images.unsplash.com/photo-1592210454359-9043f067919b?w=600&auto=format&fit=crop&q=80", use_container_width=True)
st.sidebar.title("⚙️ Control Panel")

# Data Mode
mode_choice = st.sidebar.radio(
    "Data Source Mode:",
    [
        "🌐 Live Public API (Open-Meteo - No Key)",
        "🧪 Virtual Simulation Lab (Offline Test)",
        "🔑 OpenWeatherMap API (Requires Key)"
    ]
)

# Input parameters
if "Live Public API" in mode_choice:
    selected_mode = "openmeteo"
    city_input = st.sidebar.text_input("Enter City Name:", value="London")
    api_key_val = None
elif "Virtual Simulation" in mode_choice:
    selected_mode = "simulation"
    sim_scenario = st.sidebar.selectbox(
        "Choose Simulated Weather Scenario:",
        ["Mumbai (Severe Monsoon Storm)", "Phoenix (Extreme Heat Wave)", "Chicago (Freezing Blizzard)", "London (Mild Overcast)", "Tokyo (High Humidity & Rain)"]
    )
    city_input = sim_scenario.split(" ")[0]
    api_key_val = None
else:
    selected_mode = "openweather"
    city_input = st.sidebar.text_input("Enter City Name:", value="London")
    api_key_val = st.sidebar.text_input("OpenWeatherMap API Key:", value=OPENWEATHER_API_KEY, type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 Alert Threshold Tuning")

thresh_temp_high = st.sidebar.slider("Heat Wave Threshold (°C)", min_value=25.0, max_value=50.0, value=float(DEFAULT_THRESHOLDS["temp_high"]), step=0.5)
thresh_temp_low = st.sidebar.slider("Freeze Frost Threshold (°C)", min_value=-20.0, max_value=15.0, value=float(DEFAULT_THRESHOLDS["temp_low"]), step=0.5)
thresh_humidity = st.sidebar.slider("High Humidity Threshold (%)", min_value=50, max_value=100, value=int(DEFAULT_THRESHOLDS["humidity_high"]), step=5)
thresh_wind = st.sidebar.slider("Gale Wind Threshold (km/h)", min_value=20.0, max_value=100.0, value=float(DEFAULT_THRESHOLDS["wind_speed"]), step=5.0)
thresh_rain = st.sidebar.checkbox("Trigger Precipitation & Storm Alerts", value=True)

custom_thresholds = {
    "temp_high": thresh_temp_high,
    "temp_low": thresh_temp_low,
    "humidity_high": thresh_humidity,
    "wind_speed": thresh_wind,
    "rain_alert": thresh_rain
}


# -------------------------------------------------------------
# MAIN APP HEADER
# -------------------------------------------------------------
st.title("🌤️ Weather Forecast & Risk Alert Control Center")
st.markdown("**Industry-Oriented Meteorological Monitoring, Real-Time Risk Analysis & Automated Advisory System**")

client = WeatherAPIClient(api_key=api_key_val)

with st.spinner(f"Acquiring meteorological telemetry for {city_input}..."):
    success, raw_payload, error_msg = client.get_weather(city_input, mode=selected_mode)

if not success or not raw_payload:
    st.error(f"⚠️ Telemetry Acquisition Failed: {error_msg}")
    st.info("Tip: Try switching to 'Virtual Simulation Lab' or 'Live Public API (Open-Meteo)' in the sidebar!")
    st.stop()

# Parse & Normalize
try:
    parsed_data = WeatherParser.parse(raw_payload)
except Exception as e:
    st.error(f"Error parsing weather data: {str(e)}")
    st.stop()

meta = parsed_data["metadata"]
curr = parsed_data["current"]
fc = parsed_data["forecast"]

# Evaluate Alerts
engine = AlertEngine(thresholds=custom_thresholds)
alerts = engine.evaluate(parsed_data)


# -------------------------------------------------------------
# TAB NAVIGATION
# -------------------------------------------------------------
tab_live, tab_forecast, tab_reports, tab_architecture = st.tabs([
    "📊 Live Dashboard & Radar",
    "📈 5-Day Outlook & Trends",
    "📑 Report Downloads & Audit",
    "🏗️ Architecture & Interview Prep"
])

# -------------------------------------------------------------
# TAB 1: LIVE DASHBOARD & RADAR
# -------------------------------------------------------------
with tab_live:
    # Status Banner
    st.caption(f"Source: **{meta['source']}** | Coordinates: `{meta['coordinates']}` | Updated: `{curr['timestamp']}`")

    # Current Metrics Row
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        st.metric("Temperature", f"{curr['temperature']}°C", delta=f"Feels {curr['feels_like']}°C")
    with m_col2:
        st.metric("Condition", curr['weather_main'], help=curr['weather_description'])
    with m_col3:
        st.metric("Humidity", f"{curr['humidity']}%")
    with m_col4:
        st.metric("Wind Speed", f"{curr['wind_speed']} km/h", delta=curr['wind_direction'])
    with m_col5:
        st.metric("Precipitation 1h", f"{curr['rain_1h']} mm")

    st.markdown("### 🚨 Active Weather Alert Radar")

    if not alerts:
        st.success("✅ **All Meteorological Conditions Normal**: No adverse temperature, precipitation, or wind risk thresholds exceeded.")
    else:
        for a in alerts:
            if a.severity == "CRITICAL":
                st.error(f"**[{a.severity}] {a.title}**\n\n- **Details:** {a.message}\n- **Metric:** Observed `{a.observed_value}` vs Threshold `{a.threshold_value}`\n- **Safety Advisory:** {a.action_advice}")
            elif a.severity == "WARNING":
                st.warning(f"**[{a.severity}] {a.title}**\n\n- **Details:** {a.message}\n- **Metric:** Observed `{a.observed_value}` vs Threshold `{a.threshold_value}`\n- **Safety Advisory:** {a.action_advice}")
            else:
                st.info(f"**[{a.severity}] {a.title}**\n\n- **Details:** {a.message}\n- **Metric:** Observed `{a.observed_value}` vs Threshold `{a.threshold_value}`\n- **Safety Advisory:** {a.action_advice}")

    st.markdown("---")
    # Quick visual summary cards
    st.subheader(f"📍 Overview for {meta['city']}, {meta.get('country', '')}")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(f"""
        - **Barometric Pressure:** `{curr['pressure']} hPa`
        - **Cloud Cover:** `{curr['cloudiness']}%`
        - **Sky Condition:** `{curr['weather_description']}`
        - **UV Index Estimate:** `{curr.get('uv_index') or 'Moderate'}`
        """)
    with col_r:
        if alerts:
            st.markdown(f"**Total Active Alerts Detected:** `{len(alerts)}`")
            sev_counts = pd.Series([a.severity for a in alerts]).value_counts().to_dict()
            st.write(sev_counts)
        else:
            st.write("🟢 Safe operational status for outdoor logistics, travel, and agriculture.")

# -------------------------------------------------------------
# TAB 2: 5-DAY OUTLOOK & TRENDS
# -------------------------------------------------------------
with tab_forecast:
    st.subheader(f"📅 5-Day Meteorological Outlook for {meta['city']}")

    # Render Day Cards
    fc_cols = st.columns(len(fc))
    for i, col in enumerate(fc_cols):
        day_data = fc[i]
        with col:
            st.markdown(f"**{day_data['datetime']}**")
            st.markdown(f"### {day_data['temp']}°C")
            st.caption(f"Min: {day_data['temp_min']}° | Max: {day_data['temp_max']}°")
            st.write(f"🌧️ Rain: **{day_data['rain_prob']}%**")
            st.write(f"*{day_data['condition']}*")

    st.markdown("### 📈 Interactive Weather Trend Visualizations")

    # Plotly interactive dual-axis chart
    dates = [f["datetime"] for f in fc]
    t_maxs = [f["temp_max"] for f in fc]
    t_mins = [f["temp_min"] for f in fc]
    rain_probs = [f.get("rain_prob", 0) for f in fc]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=t_maxs,
        name="Max Temp (°C)",
        line=dict(color="#F97316", width=3),
        mode="lines+markers+text",
        text=[f"{t}°" for t in t_maxs],
        textposition="top center"
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=t_mins,
        name="Min Temp (°C)",
        line=dict(color="#38BDF8", width=3),
        mode="lines+markers+text",
        text=[f"{t}°" for t in t_mins],
        textposition="bottom center"
    ))
    fig.add_trace(go.Bar(
        x=dates, y=rain_probs,
        name="Rain Probability (%)",
        yaxis="y2",
        opacity=0.4,
        marker=dict(color="#3B82F6")
    ))

    fig.update_layout(
        title=f"Temperature Range and Precipitation Outlook - {meta['city']}",
        xaxis=dict(title="Forecast Date"),
        yaxis=dict(title="Temperature (°C)"),
        yaxis2=dict(
            title="Rain Probability (%)",
            overlaying="y",
            side="right",
            range=[0, 100]
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    # Static Matplotlib Preview
    with st.expander("🖼️ View & Download Static Matplotlib Chart (Saved to outputs/)"):
        chart_path = WeatherVisualizer.generate_forecast_chart(parsed_data, f"forecast_{meta['city'].lower()}.png")
        if chart_path:
            st.image(chart_path, caption=f"Matplotlib Generated Chart for {meta['city']}", use_container_width=True)

# -------------------------------------------------------------
# TAB 3: REPORT DOWNLOADS & AUDIT LOGS
# -------------------------------------------------------------
with tab_reports:
    st.subheader("📑 Automated Export & Compliance Reporting Center")
    st.write("Generate industry-standard audit summaries, tabular CSV datasets, and machine-readable JSON logs.")

    rep_col1, rep_col2, rep_col3 = st.columns(3)

    csv_path = WeatherReporter.generate_csv_report(parsed_data)
    json_path = WeatherReporter.generate_json_audit(parsed_data, alerts)
    txt_summary = WeatherReporter.generate_text_summary(parsed_data, alerts)

    with rep_col1:
        st.markdown("#### 📊 CSV Forecast Data")
        with open(csv_path, "r", encoding="utf-8") as f:
            csv_data = f.read()
        st.download_button(
            label="⬇️ Download Forecast CSV",
            data=csv_data,
            file_name=f"weather_forecast_{meta['city'].lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with rep_col2:
        st.markdown("#### 🤖 JSON Audit Log")
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = f.read()
        st.download_button(
            label="⬇️ Download Audit JSON",
            data=json_data,
            file_name=f"weather_audit_{meta['city'].lower()}.json",
            mime="application/json",
            use_container_width=True
        )

    with rep_col3:
        st.markdown("#### 📝 Executive Text Report")
        st.download_button(
            label="⬇️ Download Executive Report",
            data=txt_summary,
            file_name=f"weather_report_{meta['city'].lower()}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("📜 Executive Report Preview")
    st.text(txt_summary)

    if HISTORICAL_LOG_PATH.exists():
        st.markdown("---")
        st.subheader("🕒 Historical Session Audit Log (Last 10 Records)")
        try:
            df_hist = pd.read_csv(HISTORICAL_LOG_PATH)
            st.dataframe(df_hist.tail(10), use_container_width=True)
        except Exception:
            pass

# -------------------------------------------------------------
# TAB 4: ARCHITECTURE & INTERVIEW PREP
# -------------------------------------------------------------
with tab_architecture:
    st.subheader("🏛️ Project Architecture & Data Flow")
    st.markdown("""
```
┌─────────────────┐       ┌────────────────────────┐       ┌──────────────────────┐
│  User / Client  │ ────> │  Smart API Client      │ ────> │  Weather Data Parser │
│  (CLI/Streamlit)│       │  (OpenWeather/Meteo/Sim│       │  (Schema Standardizer│
└─────────────────┘       └────────────────────────┘       └──────────┬───────────┘
                                                                      │
                                   ┌──────────────────────────────────┴─────────────┐
                                   ▼                                                ▼
                        ┌───────────────────────┐                        ┌──────────────────────┐
                        │   Alert Engine Radar  │                        │  Visualization & Rep │
                        │  (Threshold Evaluation│                        │  (Matplotlib/CSV/JSON│
                        └──────────┬────────────┘                        └──────────┬───────────┘
                                   │                                                │
                                   ▼                                                ▼
                        ┌───────────────────────┐                        ┌──────────────────────┐
                        │ Real-Time Safety Alert│                        │ Historical CSV Logs &│
                        │ (Critical/Warn/Adviso)│                        │ Executive Summaries  │
                        └───────────────────────┘                        └──────────────────────┘
```
    """)
    st.markdown("""
    ### 🎯 Key Engineering Highlights for Resume & Interviews:
    - **Zero-Dependency Resilient Fallback:** Implemented a multi-tier API acquisition pattern (OpenWeatherMap -> Free Open-Meteo -> Local Virtual Simulation).
    - **Domain-Specific Alert Engine:** Configurable thresholds for temperature, wind, humidity, and storm patterns with actionable advisory guidelines.
    - **Automated Reporting:** Generates instant tabular CSV, JSON audit traces, and executive summaries.
    - **Modular Clean Architecture:** Strict separation of concerns across `config`, `api_client`, `parser`, `alert_engine`, `visualizer`, and `reporter`.
    """)
