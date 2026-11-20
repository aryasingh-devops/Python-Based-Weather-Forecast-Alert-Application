# System Architecture & Technical Specification
## Project: Weather Forecast & Risk Alert Application

---

## 1. High-Level Architecture Overview

The **Weather Forecast & Risk Alert Application** is engineered with a clean, decoupled **Multi-Tier Architecture**. It isolates external data retrieval, internal data normalization, risk condition evaluation, and multi-channel presentation.

```
                      +------------------------------------------+
                      |               USER CLIENT                |
                      |  CLI Terminal Menu  /  Streamlit Web UI  |
                      +--------------------+---------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                           ACQUISITION & CLIENT LAYER                              |
|  [OpenWeatherMap API]  <--->  [WeatherAPIClient Router]  <--->  [Open-Meteo API]   |
|                                         |                                         |
|                                         v                                         |
|                       [Virtual Simulation Data Store]                             |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                         PARSING & NORMALIZATION LAYER                             |
|                       [WeatherParser Standardizer]                                |
|  - JSON Extraction      - Unit Normalization      - WMO Code Translation          |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                            RISK EVALUATION ENGINE                                 |
|                       [AlertEngine Threshold Checker]                             |
|  - Heat Wave Check (>= 35°C)          - Freeze Frost Check (<= 0°C)               |
|  - High Humidity Check (>= 85%)       - Gale Wind Velocity Check (>= 40 km/h)     |
|  - Severe Storm / Precipitation       - 5-Day Forward Outlook Anomalies           |
+---------------------+------------------------------------+------------------------+
                      |                                    |
                      v                                    v
+-------------------------------+        +------------------------------------------+
|      VISUALIZATION LAYER      |        |             REPORTING LAYER              |
|  [WeatherVisualizer (Matplotlib)]      |       [WeatherReporter File Exporter]    |
|  - Temperature Envelope Trend |        |  - Tabular CSV Forecast Export           |
|  - Rain Likelihood Bar Graph  |        |  - Machine-Readable JSON Audit Traces    |
|  - Plotly Interactive Widgets |        |  - Executive Text Audit Summaries        |
+-------------------------------+        +------------------------------------------+
```

---

## 2. Detailed Data Flow

1. **Input Phase:**
   - User inputs target location (e.g., `London`, `Mumbai`, `Phoenix`).
   - System reads configuration from `.env` (or environment variables) for OpenWeatherMap API keys, default units, and threshold preferences.
2. **Acquisition Phase:**
   - `WeatherAPIClient` attempts primary authenticated query against OpenWeatherMap.
   - If no API key is detected or network encounters rate limits, it automatically fails over to Open-Meteo's live public meteorological geocoding & forecast API (zero-key required).
   - If offline or explicitly requested, it routes to `data/sample_weather.json` (Virtual Simulator).
3. **Normalization Phase:**
   - `WeatherParser` ingests diverse JSON schemas and transforms them into a canonical `WeatherData` dictionary structure with metadata, current metrics, and 5-day daily forecast slices.
4. **Alert Evaluation Phase:**
   - `AlertEngine` evaluates current metrics and forecast projections against configurable domain thresholds.
   - Generates categorized `WeatherAlert` objects containing severity (`CRITICAL`, `WARNING`, `ADVISORY`), exact delta values, and domain-specific safety advice.
   - Appends session observations into `data/historical_logs.csv` for audit logging.
5. **Output & Presentation Phase:**
   - CLI displays colored summary tables, alert callouts, and forecast timelines.
   - Streamlit Web Dashboard renders interactive metric cards, alert banners, and Plotly charts.
   - Static Matplotlib charts are exported to `outputs/` and `images/`.
   - CSV and JSON reports are persisted to `reports/`.

---

## 3. Component Responsibilities

| Module | Core Responsibility | Key Classes / Functions |
| :--- | :--- | :--- |
| `src/config.py` | Configuration management and `.env` parsing | `DEFAULT_THRESHOLDS`, `get_active_config()` |
| `src/api_client.py` | Multi-source API connectivity and failover | `WeatherAPIClient`, `WMO_CODE_MAP` |
| `src/parser.py` | Heterogeneous JSON payload parsing & normalization | `WeatherParser.parse()` |
| `src/alert_engine.py` | Rule-based meteorological risk evaluation | `AlertEngine.evaluate()`, `WeatherAlert` |
| `src/visualizer.py` | Publication-ready Matplotlib chart generation | `WeatherVisualizer.generate_forecast_chart()` |
| `src/reporter.py` | Structured audit report exports (CSV, JSON, TXT) | `WeatherReporter` |
| `main.py` | Interactive CLI interface with terminal flags | `interactive_menu()`, `execute_weather_pipeline()` |
| `app.py` | Streamlit interactive web dashboard | Multi-tab UI, Plotly charts, threshold sliders |
