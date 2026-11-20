"""Weather API Client module.

Provides a unified interface to fetch real-time weather and forecast data from:
1. OpenWeatherMap (Key-authenticated production API)
2. Open-Meteo (Zero-key live public meteorological API)
3. Virtual Simulator (Offline mock database for student testing and demonstration)
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
import requests

from src.config import (
    OPENWEATHER_API_KEY,
    OPENWEATHER_BASE_URL,
    OPENMETEO_BASE_URL,
    OPENMETEO_GEO_URL,
    SAMPLE_DATA_PATH,
    WEATHER_UNITS,
)

logger = logging.getLogger(__name__)

# WMO Weather interpretation codes (WW) mapping used by Open-Meteo
WMO_CODE_MAP = {
    0: ("Clear", "Clear sky"),
    1: ("Mainly Clear", "Mainly clear"),
    2: ("Partly Cloudy", "Partly cloudy"),
    3: ("Overcast", "Overcast sky"),
    45: ("Fog", "Foggy conditions"),
    48: ("Depositing Rime Fog", "Freezing fog"),
    51: ("Drizzle", "Light drizzle"),
    53: ("Drizzle", "Moderate drizzle"),
    55: ("Drizzle", "Dense drizzle"),
    61: ("Rain", "Slight rain"),
    63: ("Rain", "Moderate rain"),
    65: ("Rain", "Heavy rain"),
    71: ("Snow", "Slight snow fall"),
    73: ("Snow", "Moderate snow fall"),
    75: ("Snow", "Heavy snow fall"),
    77: ("Snow Grains", "Snow grains"),
    80: ("Rain Showers", "Slight rain showers"),
    81: ("Rain Showers", "Moderate rain showers"),
    82: ("Violent Rain Showers", "Violent rain showers"),
    85: ("Snow Showers", "Slight snow showers"),
    86: ("Snow Showers", "Heavy snow showers"),
    95: ("Thunderstorm", "Thunderstorm: slight or moderate"),
    96: ("Thunderstorm", "Thunderstorm with slight hail"),
    99: ("Severe Thunderstorm", "Severe thunderstorm with heavy hail"),
}


class WeatherAPIClient:
    """Unified client handling Live APIs and Virtual Simulation."""

    def __init__(self, api_key: Optional[str] = None, units: str = WEATHER_UNITS):
        self.api_key = api_key if api_key else OPENWEATHER_API_KEY
        self.units = units
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "WeatherForecastAlertApp/1.0"})

    # -------------------------------------------------------------
    # 1. LIVE OPENWEATHERMAP API
    # -------------------------------------------------------------
    def fetch_openweather_data(self, city: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """Fetches current weather and 5-day forecast from OpenWeatherMap.

        Returns: (success: bool, data_dict: dict, error_message: str | None)
        """
        if not self.api_key or self.api_key == "your_openweather_api_key_here":
            return False, {}, "OpenWeatherMap API Key is missing or invalid in configuration."

        try:
            # 1. Fetch Current Weather
            curr_url = f"{OPENWEATHER_BASE_URL}/weather"
            curr_params = {"q": city, "appid": self.api_key, "units": self.units}
            curr_res = self.session.get(curr_url, params=curr_params, timeout=8)

            if curr_res.status_code == 401:
                return False, {}, "HTTP 401: Invalid API Key. Please verify your OpenWeatherMap key."
            if curr_res.status_code == 404:
                return False, {}, f"HTTP 404: City '{city}' was not found. Please check spelling."
            curr_res.raise_for_status()
            current_raw = curr_res.json()

            # 2. Fetch 5-Day Forecast
            fc_url = f"{OPENWEATHER_BASE_URL}/forecast"
            fc_params = {"q": city, "appid": self.api_key, "units": self.units}
            fc_res = self.session.get(fc_url, params=fc_params, timeout=8)
            fc_res.raise_for_status()
            forecast_raw = fc_res.json()

            return True, {
                "source": "OpenWeatherMap API",
                "city": current_raw.get("name", city),
                "country": current_raw.get("sys", {}).get("country", ""),
                "coordinates": current_raw.get("coord", {}),
                "current_raw": current_raw,
                "forecast_raw": forecast_raw,
            }, None

        except requests.exceptions.Timeout:
            return False, {}, "API request timed out. Please check your internet connection."
        except requests.exceptions.ConnectionError:
            return False, {}, "Network connection error. Unable to reach OpenWeatherMap servers."
        except requests.exceptions.HTTPError as e:
            return False, {}, f"HTTP error occurred: {str(e)}"
        except Exception as e:
            return False, {}, f"Unexpected API error: {str(e)}"

    # -------------------------------------------------------------
    # 2. LIVE OPEN-METEO PUBLIC API (ZERO KEY REQUIRED)
    # -------------------------------------------------------------
    def fetch_openmeteo_data(self, city: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """Fetches live meteorological data using Open-Meteo's free public API.

        Requires NO registration or API key.
        """
        try:
            # 1. Geocode city name to Lat/Lon
            geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}
            geo_res = self.session.get(OPENMETEO_GEO_URL, params=geo_params, timeout=8)
            geo_res.raise_for_status()
            geo_data = geo_res.json()

            if not geo_data.get("results"):
                return False, {}, f"City '{city}' could not be located via geocoding service."

            top_result = geo_data["results"][0]
            lat = top_result["latitude"]
            lon = top_result["longitude"]
            resolved_city = top_result.get("name", city)
            country = top_result.get("country_code", "")

            # 2. Fetch Weather & Daily Forecast
            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "hourly": "temperature_2m,relativehumidity_2m,precipitation,windspeed_10m,weathercode",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
                "timezone": "auto",
            }
            w_res = self.session.get(OPENMETEO_BASE_URL, params=weather_params, timeout=8)
            w_res.raise_for_status()
            w_data = w_res.json()

            return True, {
                "source": "Open-Meteo Public API (Live, No Key)",
                "city": resolved_city,
                "country": country,
                "coordinates": {"lat": lat, "lon": lon},
                "raw_openmeteo": w_data,
            }, None

        except requests.exceptions.Timeout:
            return False, {}, "Open-Meteo request timed out. Please check your connection."
        except requests.exceptions.ConnectionError:
            return False, {}, "Network error. Unable to reach Open-Meteo meteorological servers."
        except Exception as e:
            return False, {}, f"Open-Meteo integration error: {str(e)}"

    # -------------------------------------------------------------
    # 3. VIRTUAL SIMULATION MODE (OFFLINE / SAMPLE DATA)
    # -------------------------------------------------------------
    def fetch_simulation_data(self, scenario_name: str = "Mumbai") -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """Loads realistic simulated weather datasets from local JSON.

        Guarantees 100% reliable execution for offline grading, CI/CD, or classroom demos.
        """
        try:
            if not SAMPLE_DATA_PATH.exists():
                return False, {}, f"Simulation database file missing at {SAMPLE_DATA_PATH}"

            with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
                sim_data = json.load(f)

            scenarios = sim_data.get("scenarios", {})
            # Look up case-insensitively
            matched_key = next((k for k in scenarios if k.lower() == scenario_name.strip().lower()), None)

            if not matched_key:
                # Default to Mumbai or first scenario
                matched_key = "Mumbai" if "Mumbai" in scenarios else next(iter(scenarios))

            selected_data = scenarios[matched_key]

            return True, {
                "source": "Virtual Simulation Engine (Offline Synthetic)",
                "city": selected_data["city"],
                "country": selected_data.get("country", "SIM"),
                "coordinates": selected_data.get("coordinates", {"lat": 0.0, "lon": 0.0}),
                "simulation_payload": selected_data,
            }, None

        except Exception as e:
            return False, {}, f"Failed to load simulation scenario: {str(e)}"

    # -------------------------------------------------------------
    # 4. MASTER SMART ROUTER
    # -------------------------------------------------------------
    def get_weather(self, city_or_scenario: str, mode: str = "auto") -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """Smart routing method:

        - 'openweather': Attempts OpenWeatherMap API
        - 'openmeteo': Uses free live Open-Meteo API
        - 'simulation': Uses local realistic mock database
        - 'auto': Attempts OpenWeatherMap if key is valid -> falls back to Open-Meteo -> falls back to simulation
        """
        mode = mode.lower()

        if mode == "openweather":
            return self.fetch_openweather_data(city_or_scenario)

        if mode == "openmeteo":
            return self.fetch_openmeteo_data(city_or_scenario)

        if mode == "simulation":
            return self.fetch_simulation_data(city_or_scenario)

        # AUTO MODE (Failover chain)
        if self.api_key and self.api_key != "your_openweather_api_key_here":
            success, data, err = self.fetch_openweather_data(city_or_scenario)
            if success:
                return True, data, None
            logger.warning(f"OpenWeatherMap failed ({err}). Falling back to Open-Meteo...")

        # Fallback to Open-Meteo Live API
        success, data, err = self.fetch_openmeteo_data(city_or_scenario)
        if success:
            return True, data, None
        logger.warning(f"Open-Meteo failed ({err}). Falling back to Virtual Simulation...")

        # Fallback to Virtual Simulation
        return self.fetch_simulation_data(city_or_scenario)
