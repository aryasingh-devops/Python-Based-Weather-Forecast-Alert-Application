"""Configuration module for the Weather Forecast & Alert Application.

Loads settings from .env file or environment variables with resilient fallback defaults.
Handles directory paths, threshold parameters, and API configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = BASE_DIR / "reports"
IMAGES_DIR = BASE_DIR / "images"
SAMPLE_DATA_PATH = DATA_DIR / "sample_weather.json"
HISTORICAL_LOG_PATH = DATA_DIR / "historical_logs.csv"

# Ensure runtime directories exist
for folder in [DATA_DIR, OUTPUTS_DIR, REPORTS_DIR, IMAGES_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env file if available
load_dotenv(BASE_DIR / ".env")

# API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
OPENMETEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
OPENMETEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Default Preferences
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "London")
WEATHER_UNITS = os.getenv("WEATHER_UNITS", "metric").lower()

# Default Alert Thresholds
def get_float_env(key: str, default: float) -> float:
    """Helper to safely parse float environment variables."""
    try:
        val = os.getenv(key)
        return float(val) if val is not None else default
    except (ValueError, TypeError):
        return default

def get_bool_env(key: str, default: bool) -> bool:
    """Helper to safely parse boolean environment variables."""
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes", "on")

DEFAULT_THRESHOLDS = {
    "temp_high": get_float_env("ALERT_TEMP_HIGH", 35.0),
    "temp_low": get_float_env("ALERT_TEMP_LOW", 0.0),
    "humidity_high": get_float_env("ALERT_HUMIDITY_HIGH", 85.0),
    "wind_speed": get_float_env("ALERT_WIND_SPEED", 40.0),
    "rain_alert": get_bool_env("ALERT_RAIN_DETECTED", True)
}

def get_active_config() -> dict:
    """Returns a dictionary summarizing active application runtime settings."""
    return {
        "base_dir": str(BASE_DIR),
        "api_key_configured": bool(OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "your_openweather_api_key_here"),
        "default_city": DEFAULT_CITY,
        "units": WEATHER_UNITS,
        "thresholds": DEFAULT_THRESHOLDS
    }
