"""Report Generation module.

Exports weather summaries, active alerts, and forecast outlooks into:
- Structured tabular CSV files
- Machine-readable JSON payloads
- Executive Text / Markdown audit summaries
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from tabulate import tabulate

from src.config import REPORTS_DIR
from src.alert_engine import WeatherAlert

class WeatherReporter:
    """Handles report compilation and disk persistence."""

    @staticmethod
    def generate_csv_report(weather_data: Dict[str, Any], filename: str = None) -> str:
        """Exports 5-day forecast into a clean CSV spreadsheet."""
        city = weather_data["metadata"]["city"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not filename:
            filename = f"forecast_{city.lower()}_{timestamp}.csv"

        filepath = REPORTS_DIR / filename
        forecast = weather_data.get("forecast", [])

        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date/Slot", "Temp (°C)", "Min Temp (°C)", "Max Temp (°C)", "Humidity (%)", "Rain Prob (%)", "Condition", "Description"])
            for row in forecast:
                writer.writerow([
                    row.get("datetime"),
                    row.get("temp"),
                    row.get("temp_min"),
                    row.get("temp_max"),
                    row.get("humidity"),
                    row.get("rain_prob"),
                    row.get("condition"),
                    row.get("description")
                ])

        return str(filepath)

    @staticmethod
    def generate_json_audit(weather_data: Dict[str, Any], alerts: List[WeatherAlert], filename: str = None) -> str:
        """Exports a full audit log in JSON format."""
        city = weather_data["metadata"]["city"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not filename:
            filename = f"audit_{city.lower()}_{timestamp}.json"

        filepath = REPORTS_DIR / filename
        payload = {
            "metadata": weather_data.get("metadata"),
            "current_weather": weather_data.get("current"),
            "forecast_outlook": weather_data.get("forecast"),
            "active_alerts": [a.to_dict() for a in alerts],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return str(filepath)

    @staticmethod
    def generate_text_summary(weather_data: Dict[str, Any], alerts: List[WeatherAlert], filename: str = None) -> str:
        """Generates an executive text summary report."""
        meta = weather_data["metadata"]
        c = weather_data["current"]
        fc = weather_data.get("forecast", [])
        city = meta["city"]
        country = meta.get("country", "")
        source = meta.get("source", "Live API")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = []
        lines.append("=" * 70)
        lines.append(f" WEATHER FORECAST & ALERT AUDIT REPORT: {city.upper()} ({country})")
        lines.append(f" Generated At: {timestamp} | Data Source: {source}")
        lines.append("=" * 70)
        lines.append("")
        lines.append("📌 CURRENT OBSERVATION:")
        lines.append(f"  • Temperature:       {c.get('temperature')}°C (Feels like: {c.get('feels_like')}°C)")
        lines.append(f"  • Condition:         {c.get('weather_main')} - {c.get('weather_description')}")
        lines.append(f"  • Humidity:          {c.get('humidity')}%")
        lines.append(f"  • Wind Velocity:     {c.get('wind_speed')} km/h ({c.get('wind_direction')})")
        lines.append(f"  • Barometric Press.: {c.get('pressure')} hPa")
        lines.append(f"  • Precipitation (1h):{c.get('rain_1h')} mm")
        lines.append("")

        lines.append("⚠️ ACTIVE WEATHER ALERTS:")
        if not alerts:
            lines.append("  [✓] All meteorological indicators are within normal safe operating thresholds.")
        else:
            for idx, a in enumerate(alerts, 1):
                lines.append(f"  [{idx}] {a.title} ({a.severity})")
                lines.append(f"      - Message: {a.message}")
                lines.append(f"      - Rule:    Observed {a.observed_value} vs Threshold {a.threshold_value}")
                lines.append(f"      - Advisory: {a.action_advice}")
                lines.append("")

        lines.append("📅 5-DAY OUTLOOK SUMMARY:")
        table_rows = []
        for row in fc:
            table_rows.append([
                row.get("datetime"),
                f"{row.get('temp')}°C",
                f"{row.get('temp_min')}°C / {row.get('temp_max')}°C",
                f"{row.get('rain_prob')}%",
                row.get("condition")
            ])
        lines.append(tabulate(table_rows, headers=["Date", "Avg Temp", "Min / Max", "Rain Prob", "Condition"], tablefmt="presto"))
        lines.append("")
        lines.append("=" * 70)
        lines.append(" End of Automated Weather & Risk Assessment Report")
        lines.append("=" * 70)

        report_content = "\n".join(lines)

        if not filename:
            filename = f"report_{city.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        filepath = REPORTS_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)

        return report_content
