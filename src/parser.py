"""Data Normalization and Parsing module.

Extracts, cleans, and transforms raw API responses (OpenWeatherMap, Open-Meteo,
or Virtual Simulation) into a unified, predictable, and strongly-typed data structure.
"""

from datetime import datetime
from typing import Dict, Any, List
from src.api_client import WMO_CODE_MAP

class WeatherParser:
    """Standardizes heterogeneous weather payloads into a canonical dictionary format."""

    @staticmethod
    def parse(raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main dispatcher for parsing payload based on payload keys."""
        source = raw_payload.get("source", "Unknown")

        if "current_raw" in raw_payload:
            return WeatherParser._parse_openweather(raw_payload)
        elif "raw_openmeteo" in raw_payload:
            return WeatherParser._parse_openmeteo(raw_payload)
        elif "simulation_payload" in raw_payload:
            return WeatherParser._parse_simulation(raw_payload)
        else:
            raise ValueError(f"Unrecognized data structure from source: {source}")

    @staticmethod
    def _parse_openweather(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Parses OpenWeatherMap 2.5 API JSON payload."""
        c = raw["current_raw"]
        fc_list = raw["forecast_raw"].get("list", [])

        main = c.get("main", {})
        wind = c.get("wind", {})
        weather_arr = c.get("weather", [{}])
        first_w = weather_arr[0] if weather_arr else {}

        # Parse current
        current_data = {
            "timestamp": datetime.fromtimestamp(c.get("dt", datetime.now().timestamp())).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(float(main.get("temp", 0.0)), 1),
            "feels_like": round(float(main.get("feels_like", 0.0)), 1),
            "temp_min": round(float(main.get("temp_min", 0.0)), 1),
            "temp_max": round(float(main.get("temp_max", 0.0)), 1),
            "humidity": int(main.get("humidity", 0)),
            "pressure": float(main.get("pressure", 1013)),
            "wind_speed": round(float(wind.get("speed", 0.0)) * 3.6, 1), # m/s to km/h
            "wind_direction": str(wind.get("deg", 0)) + "°",
            "weather_main": first_w.get("main", "Clear"),
            "weather_description": first_w.get("description", "Clear sky").capitalize(),
            "rain_1h": float(c.get("rain", {}).get("1h", 0.0)),
            "cloudiness": int(c.get("clouds", {}).get("all", 0)),
            "uv_index": None
        }

        # Parse 5-day forecast (OpenWeather gives 3-hour slices, we sample mid-day forecasts or aggregate)
        forecast_items: List[Dict[str, Any]] = []
        seen_days = set()

        for item in fc_list:
            dt_txt = item.get("dt_txt", "")
            date_part = dt_txt.split(" ")[0] if " " in dt_txt else dt_txt

            # Pick 1 representative time slot per day (ideally 12:00:00 or first seen)
            if "12:00:00" in dt_txt or date_part not in seen_days:
                seen_days.add(date_part)
                f_main = item.get("main", {})
                f_w = item.get("weather", [{}])[0]
                pop = int(float(item.get("pop", 0.0)) * 100) # Probability of precipitation

                forecast_items.append({
                    "datetime": date_part,
                    "temp": round(float(f_main.get("temp", 0.0)), 1),
                    "temp_min": round(float(f_main.get("temp_min", 0.0)), 1),
                    "temp_max": round(float(f_main.get("temp_max", 0.0)), 1),
                    "humidity": int(f_main.get("humidity", 0)),
                    "rain_prob": pop,
                    "condition": f_w.get("main", "Clear"),
                    "description": f_w.get("description", "").capitalize()
                })

            if len(forecast_items) >= 5:
                break

        return {
            "metadata": {
                "city": raw["city"],
                "country": raw["country"],
                "source": raw["source"],
                "coordinates": raw["coordinates"]
            },
            "current": current_data,
            "forecast": forecast_items
        }

    @staticmethod
    def _parse_openmeteo(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Parses Open-Meteo free live API meteorological response."""
        data = raw["raw_openmeteo"]
        cw = data.get("current_weather", {})
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})

        wcode = int(cw.get("weathercode", 0))
        cond_main, cond_desc = WMO_CODE_MAP.get(wcode, ("Clear", "Clear conditions"))

        # Approximate humidity and rain from hourly data at index 0
        current_humidity = hourly.get("relativehumidity_2m", [65])[0] if hourly.get("relativehumidity_2m") else 65
        current_rain = hourly.get("precipitation", [0.0])[0] if hourly.get("precipitation") else 0.0

        current_data = {
            "timestamp": cw.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "temperature": round(float(cw.get("temperature", 0.0)), 1),
            "feels_like": round(float(cw.get("temperature", 0.0)), 1),
            "temp_min": round(float(daily.get("temperature_2m_min", [cw.get("temperature", 0.0)])[0]), 1),
            "temp_max": round(float(daily.get("temperature_2m_max", [cw.get("temperature", 0.0)])[0]), 1),
            "humidity": int(current_humidity),
            "pressure": 1013.2,
            "wind_speed": round(float(cw.get("windspeed", 0.0)), 1),
            "wind_direction": str(cw.get("winddirection", 0)) + "°",
            "weather_main": cond_main,
            "weather_description": cond_desc,
            "rain_1h": float(current_rain),
            "cloudiness": 50 if "Cloud" in cond_main else 10,
            "uv_index": 5.0
        }

        # Daily forecast
        forecast_items: List[Dict[str, Any]] = []
        times = daily.get("time", [])
        t_maxs = daily.get("temperature_2m_max", [])
        t_mins = daily.get("temperature_2m_min", [])
        rain_probs = daily.get("precipitation_probability_max", [])
        wcodes = daily.get("weathercode", [])

        for i in range(min(5, len(times))):
            code = int(wcodes[i]) if i < len(wcodes) else 0
            main_c, desc_c = WMO_CODE_MAP.get(code, ("Clear", "Clear sky"))
            t_max = float(t_maxs[i]) if i < len(t_maxs) else 20.0
            t_min = float(t_mins[i]) if i < len(t_mins) else 10.0
            avg_temp = round((t_max + t_min) / 2.0, 1)

            forecast_items.append({
                "datetime": times[i],
                "temp": avg_temp,
                "temp_min": round(t_min, 1),
                "temp_max": round(t_max, 1),
                "humidity": 65,
                "rain_prob": int(rain_probs[i]) if i < len(rain_probs) and rain_probs[i] is not None else 0,
                "condition": main_c,
                "description": desc_c
            })

        return {
            "metadata": {
                "city": raw["city"],
                "country": raw["country"],
                "source": raw["source"],
                "coordinates": raw["coordinates"]
            },
            "current": current_data,
            "forecast": forecast_items
        }

    @staticmethod
    def _parse_simulation(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Parses simulated scenario dataset."""
        payload = raw["simulation_payload"]
        return {
            "metadata": {
                "city": raw["city"],
                "country": raw["country"],
                "source": raw["source"],
                "coordinates": raw["coordinates"]
            },
            "current": payload["current"],
            "forecast": payload["forecast"]
        }
