"""Data Visualization module.

Renders high-resolution meteorological trend charts using Matplotlib:
- 5-Day Temperature progression (Max vs Min)
- Precipitation Probability Bar Chart
- Humidity and Wind velocity trends
Saves static charts to outputs/ and images/ for GitHub portfolio presentation.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend suitable for headless scripts & web servers
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from src.config import OUTPUTS_DIR, IMAGES_DIR

class WeatherVisualizer:
    """Produces visually compelling meteorological plots."""

    @staticmethod
    def generate_forecast_chart(weather_data: Dict[str, Any], save_filename: str = "forecast_chart.png") -> Optional[str]:
        """Generates a combined dual-panel forecast visualization chart."""
        forecast = weather_data.get("forecast", [])
        city = weather_data.get("metadata", {}).get("city", "City")

        if not forecast:
            return None

        dates = [f["datetime"] for f in forecast]
        t_maxs = [f["temp_max"] for f in forecast]
        t_mins = [f["temp_min"] for f in forecast]
        rain_probs = [f.get("rain_prob", 0) for f in forecast]
        humidities = [f.get("humidity", 50) for f in forecast]

        # Professional clean dark/light modern palette
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, gridspec_kw={'height_ratios': [1.8, 1.2]})
        fig.patch.set_facecolor("#0F172A")  # Deep slate navy background

        # --- PANEL 1: TEMPERATURE TRENDS ---
        ax1.set_facecolor("#1E293B")
        ax1.grid(color="#334155", linestyle="--", linewidth=0.7, alpha=0.7)

        # Plot Max & Min lines
        line_max, = ax1.plot(dates, t_maxs, color="#F97316", marker="o", linewidth=2.8, markersize=8, label="Max Temp (°C)")
        line_min, = ax1.plot(dates, t_mins, color="#38BDF8", marker="s", linewidth=2.8, markersize=8, label="Min Temp (°C)")

        # Fill temperature envelope
        ax1.fill_between(dates, t_mins, t_maxs, color="#F97316", alpha=0.15)

        # Data point labels
        for x, y in zip(dates, t_maxs):
            ax1.annotate(f"{y}°", (x, y), textcoords="offset points", xytext=(0, 10), ha='center',
                         color="#FDBA74", fontweight="bold", fontsize=10)
        for x, y in zip(dates, t_mins):
            ax1.annotate(f"{y}°", (x, y), textcoords="offset points", xytext=(0, -16), ha='center',
                         color="#BAE6FD", fontweight="bold", fontsize=10)

        ax1.set_title(f"5-Day Meteorological Forecast Outlook - {city}", fontsize=15, fontweight="bold", color="#F8FAFC", pad=15)
        ax1.set_ylabel("Temperature (°C)", fontsize=11, fontweight="semibold", color="#E2E8F0")
        ax1.tick_params(colors="#94A3B8")
        ax1.legend(loc="upper right", facecolor="#0F172A", edgecolor="#475569", labelcolor="#F1F5F9", framealpha=0.9)

        # Padding for temperature range
        all_t = t_maxs + t_mins
        ax1.set_ylim(min(all_t) - 4, max(all_t) + 5)

        # --- PANEL 2: PRECIPITATION & HUMIDITY ---
        ax2.set_facecolor("#1E293B")
        ax2.grid(color="#334155", linestyle=":", linewidth=0.7, alpha=0.5)

        bars = ax2.bar(dates, rain_probs, color="#3B82F6", alpha=0.85, width=0.45, label="Rain Likelihood (%)")
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.annotate(f"{int(height)}%",
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 4), textcoords="offset points",
                             ha='center', va='bottom', color="#93C5FD", fontsize=9, fontweight="bold")

        ax2.set_ylabel("Rain Prob (%)", fontsize=11, fontweight="semibold", color="#60A5FA")
        ax2.set_ylim(0, 110)
        ax2.tick_params(colors="#94A3B8")
        ax2.xaxis.set_tick_params(rotation=0)

        # Secondary axis for humidity
        ax2_twin = ax2.twinx()
        line_hum, = ax2_twin.plot(dates, humidities, color="#A855F7", marker="^", linewidth=2.0, linestyle="--", label="Humidity (%)")
        ax2_twin.set_ylabel("Humidity (%)", fontsize=11, fontweight="semibold", color="#C084FC")
        ax2_twin.set_ylim(0, 105)
        ax2_twin.tick_params(colors="#94A3B8")

        # Combined legend for panel 2
        lines = [bars, line_hum]
        labels = ["Rain Probability (%)", "Humidity (%)"]
        ax2.legend(lines, labels, loc="upper right", facecolor="#0F172A", edgecolor="#475569", labelcolor="#F1F5F9", framealpha=0.9)

        plt.tight_layout()

        # Save to outputs and images
        output_path = OUTPUTS_DIR / save_filename
        image_path = IMAGES_DIR / save_filename
        plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
        plt.savefig(image_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)

        return str(output_path)
