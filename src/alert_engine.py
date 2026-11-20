"""Weather Alert Engine module.

Evaluates meteorological metrics against configurable thresholds and triggers
multi-level alerts (Critical, Warning, Advisory) with actionable domain safety guidelines.
"""

import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.config import DEFAULT_THRESHOLDS, HISTORICAL_LOG_PATH


class WeatherAlert:
    """Represents an instantiated weather alert notification."""

    def __init__(
        self,
        alert_id: str,
        severity: str,
        category: str,
        title: str,
        message: str,
        observed_value: Any,
        threshold_value: Any,
        action_advice: str,
        timestamp: Optional[str] = None
    ):
        self.alert_id = alert_id
        self.severity = severity  # "CRITICAL", "WARNING", "ADVISORY", "NORMAL"
        self.category = category
        self.title = title
        self.message = message
        self.observed_value = observed_value
        self.threshold_value = threshold_value
        self.action_advice = action_advice
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "observed_value": str(self.observed_value),
            "threshold_value": str(self.threshold_value),
            "action_advice": self.action_advice
        }


class AlertEngine:
    """Core evaluation engine assessing parsed weather data."""

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        self.thresholds = thresholds or DEFAULT_THRESHOLDS.copy()

    def update_thresholds(self, new_thresholds: Dict[str, Any]):
        """Allows dynamic threshold customization from UI or CLI."""
        self.thresholds.update(new_thresholds)

    def evaluate(self, weather_data: Dict[str, Any]) -> List[WeatherAlert]:
        """Analyzes parsed weather data and generates active alerts."""
        alerts: List[WeatherAlert] = []
        city = weather_data["metadata"]["city"]
        current = weather_data["current"]
        forecast = weather_data.get("forecast", [])

        temp = current.get("temperature", 0.0)
        humidity = current.get("humidity", 0)
        wind = current.get("wind_speed", 0.0)
        weather_main = current.get("weather_main", "").lower()
        weather_desc = current.get("weather_description", "")
        rain_1h = current.get("rain_1h", 0.0)

        t_now_str = datetime.now().strftime("%Y%m%d%H%M%S")

        # ---------------------------------------------------------
        # 1. HIGH TEMPERATURE / HEAT WAVE ALERT
        # ---------------------------------------------------------
        temp_high_thresh = self.thresholds.get("temp_high", 35.0)
        if temp >= temp_high_thresh:
            severity = "CRITICAL" if temp >= (temp_high_thresh + 5.0) else "WARNING"
            alerts.append(WeatherAlert(
                alert_id=f"ALT-HEAT-{t_now_str}",
                severity=severity,
                category="HIGH_TEMPERATURE",
                title=f"🔥 High Temperature Alert: {temp}°C",
                message=f"Current temperature in {city} is {temp}°C, exceeding safe threshold of {temp_high_thresh}°C.",
                observed_value=f"{temp}°C",
                threshold_value=f">= {temp_high_thresh}°C",
                action_advice="Stay hydrated, avoid direct sun exposure between 11 AM - 4 PM. Logistics: Check cold-chain refrigeration."
            ))

        # ---------------------------------------------------------
        # 2. LOW TEMPERATURE / FREEZING FROST ALERT
        # ---------------------------------------------------------
        temp_low_thresh = self.thresholds.get("temp_low", 0.0)
        if temp <= temp_low_thresh:
            severity = "CRITICAL" if temp <= (temp_low_thresh - 5.0) else "WARNING"
            alerts.append(WeatherAlert(
                alert_id=f"ALT-COLD-{t_now_str}",
                severity=severity,
                category="LOW_TEMPERATURE",
                title=f"❄️ Freezing Condition Alert: {temp}°C",
                message=f"Freezing frost condition detected in {city} at {temp}°C (Threshold: <= {temp_low_thresh}°C).",
                observed_value=f"{temp}°C",
                threshold_value=f"<= {temp_low_thresh}°C",
                action_advice="Wear insulated thermal layers. Protect agricultural crops against frost. Motorists beware of black ice."
            ))

        # ---------------------------------------------------------
        # 3. HIGH HUMIDITY & MUGGINESS ALERT
        # ---------------------------------------------------------
        hum_thresh = self.thresholds.get("humidity_high", 85.0)
        if humidity >= hum_thresh:
            alerts.append(WeatherAlert(
                alert_id=f"ALT-HUM-{t_now_str}",
                severity="ADVISORY",
                category="HIGH_HUMIDITY",
                title=f"💧 Excessive Humidity Alert: {humidity}%",
                message=f"Relative humidity in {city} reached {humidity}%, exceeding threshold of {hum_thresh}%.",
                observed_value=f"{humidity}%",
                threshold_value=f">= {hum_thresh}%",
                action_advice="High heat exhaustion risk indoors. Ensure adequate ventilation; monitor perishables for mold and moisture."
            ))

        # ---------------------------------------------------------
        # 4. HIGH WIND & GALE FORCE ALERT
        # ---------------------------------------------------------
        wind_thresh = self.thresholds.get("wind_speed", 40.0)
        if wind >= wind_thresh:
            severity = "CRITICAL" if wind >= (wind_thresh + 20.0) else "WARNING"
            alerts.append(WeatherAlert(
                alert_id=f"ALT-WIND-{t_now_str}",
                severity=severity,
                category="HIGH_WIND",
                title=f"💨 Gale Force Wind Alert: {wind} km/h",
                message=f"Strong wind velocity of {wind} km/h detected in {city} (Threshold: >= {wind_thresh} km/h).",
                observed_value=f"{wind} km/h",
                threshold_value=f">= {wind_thresh} km/h",
                action_advice="Secure outdoor signage and loose objects. Construction cranes and high-profile freight transport should halt."
            ))

        # ---------------------------------------------------------
        # 5. RAINSTORM / THUNDERSTORM / BLIZZARD ALERT
        # ---------------------------------------------------------
        if self.thresholds.get("rain_alert", True):
            storm_keywords = ["thunderstorm", "tornado", "squall", "heavy rain", "violent rain", "blizzard"]
            is_storm = any(k in weather_main or k in weather_desc.lower() for k in storm_keywords)
            is_rain = "rain" in weather_main or "drizzle" in weather_main or rain_1h > 1.0

            if is_storm:
                alerts.append(WeatherAlert(
                    alert_id=f"ALT-STORM-{t_now_str}",
                    severity="CRITICAL",
                    category="SEVERE_STORM",
                    title=f"⛈️ Severe Storm Warning: {weather_desc}",
                    message=f"Violent storm conditions reported in {city} with intense precipitation ({rain_1h} mm/hr).",
                    observed_value=f"{weather_desc} ({rain_1h} mm/h)",
                    threshold_value="Severe Storm Pattern",
                    action_advice="Seek sturdy shelter immediately. Avoid waterlogged roadways and electrical installations. Event planners: Postpone outdoor functions."
                ))
            elif is_rain:
                alerts.append(WeatherAlert(
                    alert_id=f"ALT-RAIN-{t_now_str}",
                    severity="ADVISORY",
                    category="RAIN_WARNING",
                    title=f"🌧️ Precipitation Alert: {weather_desc}",
                    message=f"Active rain detected in {city}. Precipitation rate: {rain_1h} mm/h.",
                    observed_value=f"{rain_1h} mm/h",
                    threshold_value="Active Rainfall",
                    action_advice="Carry rain gear. Logistics: anticipate roadway delivery delays and adjust travel speed."
                ))

        # ---------------------------------------------------------
        # 6. FORECAST TREND ALERTS (Upcoming heavy rain / extreme temp)
        # ---------------------------------------------------------
        upcoming_high_rain = [f for f in forecast if f.get("rain_prob", 0) >= 80]
        if upcoming_high_rain:
            f_day = upcoming_high_rain[0]
            alerts.append(WeatherAlert(
                alert_id=f"ALT-FC-RAIN-{t_now_str}",
                severity="WARNING",
                category="FORECAST_RAIN",
                title=f"⚠️ Heavy Rain Forecast Ahead ({f_day['datetime']})",
                message=f"Forecast indicates {f_day['rain_prob']}% precipitation likelihood with {f_day['description']} on {f_day['datetime']}.",
                observed_value=f"{f_day['rain_prob']}% chance",
                threshold_value=">= 80% rain likelihood",
                action_advice="Farmers: clear drainage channels. Municipal bodies: inspect stormwater drainage infrastructure."
            ))

        # Log alerts to historical persistence
        self._log_alerts_to_history(city, alerts, current)

        return alerts

    def _log_alerts_to_history(self, city: str, alerts: List[WeatherAlert], current: Dict[str, Any]):
        """Appends observed metrics and triggered alerts into historical CSV."""
        file_exists = HISTORICAL_LOG_PATH.exists()
        try:
            with open(HISTORICAL_LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow([
                        "timestamp", "city", "temperature_c", "humidity_pct",
                        "wind_kmh", "condition", "alert_count", "highest_severity", "alert_categories"
                    ])

                highest_sev = "NORMAL"
                if any(a.severity == "CRITICAL" for a in alerts):
                    highest_sev = "CRITICAL"
                elif any(a.severity == "WARNING" for a in alerts):
                    highest_sev = "WARNING"
                elif any(a.severity == "ADVISORY" for a in alerts):
                    highest_sev = "ADVISORY"

                categories = "|".join([a.category for a in alerts]) if alerts else "NONE"

                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    city,
                    current.get("temperature", ""),
                    current.get("humidity", ""),
                    current.get("wind_speed", ""),
                    current.get("weather_main", ""),
                    len(alerts),
                    highest_sev,
                    categories
                ])
        except Exception as e:
            # Silent fallback if logging encounters file lock
            pass
