"""Weather Forecast & Alert Application - Primary CLI Entrypoint.

Industry-oriented, modular, and fault-tolerant Weather Monitoring & Alert System.
Supports Live OpenWeatherMap API, Live Open-Meteo Free API, and Virtual Simulation mode.

Usage:
    python main.py                     # Interactive terminal menu
    python main.py --city Mumbai       # Run for specific city
    python main.py --sim Phoenix       # Run virtual simulation scenario
    python main.py --help              # View available command flags
"""

import sys
import argparse
from typing import Optional

from src.config import get_active_config, DEFAULT_THRESHOLDS
from src.api_client import WeatherAPIClient
from src.parser import WeatherParser
from src.alert_engine import AlertEngine
from src.visualizer import WeatherVisualizer
from src.reporter import WeatherReporter

# Terminal Styling Constants
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    """Renders high-impact ASCII banner."""
    print(f"""{CYAN}{BOLD}
╔═════════════════════════════════════════════════════════════════════════╗
║         🌤️  WEATHER FORECAST & RISK ALERT MONITORING SYSTEM             ║
║            Industry-Grade Python Automation & Meteorological Tool       ║
╚═════════════════════════════════════════════════════════════════════════╝{RESET}""")


def execute_weather_pipeline(
    city: str,
    mode: str = "auto",
    generate_chart: bool = True,
    save_reports: bool = True,
    custom_thresholds: Optional[dict] = None
) -> bool:
    """Executes full end-to-end workflow:

    1. Fetch data -> 2. Parse & normalize -> 3. Evaluate alerts -> 4. Render visuals -> 5. Export reports
    """
    print(f"\n{BOLD}[+] Initializing Weather Data Pipeline for:{RESET} {CYAN}{city}{RESET} (Mode: {mode.upper()})")

    # 1. API Fetch
    client = WeatherAPIClient()
    success, raw_payload, error_msg = client.get_weather(city, mode=mode)

    if not success or not raw_payload:
        print(f"{RED}[✖] Error fetching weather data:{RESET} {error_msg}")
        return False

    # 2. Parse & Normalize
    try:
        parsed_data = WeatherParser.parse(raw_payload)
    except Exception as e:
        print(f"{RED}[✖] Failed to parse weather payload:{RESET} {str(e)}")
        return False

    meta = parsed_data["metadata"]
    curr = parsed_data["current"]
    fc = parsed_data["forecast"]

    print(f"{GREEN}[✓] Data Acquired Successfully from: {meta['source']}{RESET}")
    print(f"    Location: {meta['city']}, {meta.get('country', '')} | Coordinates: {meta['coordinates']}")

    # 3. Print Current Weather Summary Table
    print(f"\n{BOLD}─────────────── CURRENT METEOROLOGICAL CONDITIONS ───────────────{RESET}")
    print(f" • Temperature:      {BOLD}{curr['temperature']}°C{RESET} (Feels like: {curr['feels_like']}°C)")
    print(f" • Weather Status:   {CYAN}{curr['weather_main']}{RESET} - {curr['weather_description']}")
    print(f" • Relative Humidity:{curr['humidity']}%")
    print(f" • Wind Velocity:    {curr['wind_speed']} km/h (Direction: {curr['wind_direction']})")
    print(f" • Air Pressure:     {curr['pressure']} hPa")
    print(f" • Precipitation 1h: {curr['rain_1h']} mm")
    print(f" • Cloud Cover:      {curr['cloudiness']}%")

    # 4. Alert Evaluation
    engine = AlertEngine(thresholds=custom_thresholds or DEFAULT_THRESHOLDS)
    alerts = engine.evaluate(parsed_data)

    print(f"\n{BOLD}─────────────────────── ACTIVE ALERT RADAR ───────────────────────{RESET}")
    if not alerts:
        print(f"{GREEN}[✓] CLEAR: No adverse weather thresholds exceeded. All systems nominal.{RESET}")
    else:
        for a in alerts:
            color = RED if a.severity == "CRITICAL" else (YELLOW if a.severity == "WARNING" else CYAN)
            print(f" {color}{BOLD}[{a.severity}] {a.title}{RESET}")
            print(f"   ├─ Description: {a.message}")
            print(f"   ├─ Metric:      Observed {a.observed_value} vs Threshold {a.threshold_value}")
            print(f"   └─ Action:      {BOLD}{a.action_advice}{RESET}\n")

    # 5. Forecast Table
    print(f"{BOLD}───────────────────────── 5-DAY OUTLOOK ─────────────────────────{RESET}")
    print(f"{'Date':<14} {'Avg Temp':<10} {'Min/Max':<14} {'Rain Prob':<12} {'Condition'}")
    print("-" * 65)
    for day in fc:
        print(f"{day['datetime']:<14} {str(day['temp'])+'°C':<10} {str(day['temp_min'])+'° / '+str(day['temp_max'])+'°':<14} {str(day['rain_prob'])+'%':<12} {day['condition']}")

    # 6. Generate Visual Charts
    if generate_chart:
        chart_file = WeatherVisualizer.generate_forecast_chart(parsed_data, f"forecast_{meta['city'].lower()}.png")
        if chart_file:
            print(f"\n{GREEN}[✓] Forecast Visualization Chart Saved:{RESET} {chart_file}")

    # 7. Generate Reports
    if save_reports:
        csv_file = WeatherReporter.generate_csv_report(parsed_data)
        json_file = WeatherReporter.generate_json_audit(parsed_data, alerts)
        summary_text = WeatherReporter.generate_text_summary(parsed_data, alerts)
        print(f"{GREEN}[✓] CSV Forecast Exported:{RESET} {csv_file}")
        print(f"{GREEN}[✓] JSON Audit Log Exported:{RESET} {json_file}")
        print(f"{GREEN}[✓] Text Executive Summary Saved to reports/ directory{RESET}")

    print(f"\n{GREEN}{BOLD}[✔] Pipeline Finished Successfully!{RESET}\n")
    return True


def interactive_menu():
    """Runs intuitive console-guided interactive user interface."""
    print_banner()
    config = get_active_config()

    while True:
        print(f"""
{BOLD}SELECT AN OPTION:{RESET}
  1. Live Weather Forecast (Public API - No Key Needed)
  2. Live Weather Forecast (OpenWeatherMap API with Key)
  3. Virtual Simulation Scenarios (Offline Test Lab)
  4. View Application Architecture & Configuration
  5. Exit

""")
        choice = input(f"{BOLD}Enter choice (1-5): {RESET}").strip()

        if choice == "1":
            city = input("Enter city name (e.g., London, Tokyo, Mumbai, New York): ").strip()
            if not city:
                city = "London"
            execute_weather_pipeline(city, mode="openmeteo")

        elif choice == "2":
            if not config["api_key_configured"]:
                print(f"\n{YELLOW}[!] Notice: No valid OpenWeatherMap API key detected in .env file.{RESET}")
                manual_key = input("Enter your OpenWeatherMap API key (or press Enter to return): ").strip()
                if not manual_key:
                    continue
                client = WeatherAPIClient(api_key=manual_key)
            city = input("Enter city name: ").strip() or "London"
            execute_weather_pipeline(city, mode="openweather")

        elif choice == "3":
            print(f"\n{CYAN}{BOLD}Available Simulation Scenarios:{RESET}")
            print("  [1] Phoenix - Extreme Heat Wave (42.5°C)")
            print("  [2] Mumbai  - Tropical Thunderstorm & Heavy Rain (94% Humidity)")
            print("  [3] Chicago - Freezing Blizzard & Cold Frost (-8.5°C)")
            print("  [4] London  - Mild Normal Overcast Day (16.4°C)")
            print("  [5] Tokyo   - High Humidity Monsoon Outer Bands")
            sim_choice = input("\nSelect scenario (1-5 or name): ").strip()
            sim_map = {"1": "Phoenix", "2": "Mumbai", "3": "Chicago", "4": "London", "5": "Tokyo"}
            selected_city = sim_map.get(sim_choice, sim_choice)
            execute_weather_pipeline(selected_city, mode="simulation")

        elif choice == "4":
            print(f"\n{BOLD}ACTIVE RUNTIME CONFIGURATION:{RESET}")
            for k, v in config.items():
                print(f"  • {k}: {v}")
            input(f"\n{BOLD}Press Enter to return to main menu...{RESET}")

        elif choice == "5":
            print(f"\n{CYAN}Thank you for using the Weather Forecast & Alert System!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}Invalid selection. Please choose an option from 1 to 5.{RESET}")


def main():
    """CLI Argument parser and dispatcher."""
    parser = argparse.ArgumentParser(
        description="Weather Forecast & Risk Alert Automation Application"
    )
    parser.add_argument("--city", "-c", type=str, help="Target city name (e.g., London, Paris, Tokyo)")
    parser.add_argument(
        "--mode", "-m",
        choices=["auto", "openmeteo", "openweather", "simulation"],
        default="auto",
        help="Weather data acquisition engine (default: auto)"
    )
    parser.add_argument("--sim", "-s", type=str, help="Quick shortcut to execute a virtual simulation scenario (Phoenix, Mumbai, Chicago, London, Tokyo)")
    parser.add_argument("--no-chart", action="store_true", help="Disable Matplotlib forecast plot generation")
    parser.add_argument("--no-report", action="store_true", help="Disable CSV/JSON report exports")

    args = parser.parse_args()

    if args.sim:
        print_banner()
        execute_weather_pipeline(args.sim, mode="simulation", generate_chart=not args.no_chart, save_reports=not args.no_report)
    elif args.city:
        print_banner()
        execute_weather_pipeline(args.city, mode=args.mode, generate_chart=not args.no_chart, save_reports=not args.no_report)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
