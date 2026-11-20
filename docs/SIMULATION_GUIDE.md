# Virtual Simulation & Safe Demonstration Guide
## Weather Forecast & Risk Alert Application

---

## 1. Why Virtual Simulation?

In professional software development and meteorological automation:
- External public APIs impose strict rate limits (e.g. 60 calls/minute, daily quotas).
- New API keys often require 2-4 hours to activate after signing up.
- Automated testing, CI/CD pipelines, and academic grading require deterministic, predictable test fixtures.
- Real-world extreme events (typhoons, blizzards, extreme 44°C heatwaves) cannot be summoned on demand during a live demonstration or interview!

The **Virtual Simulation Engine** provides a complete offline lab mirroring real API response payloads.

---

## 2. Pre-Configured Scenarios

Located in `data/sample_weather.json`:

### Scenario 1: `Phoenix` - Extreme Heat Wave & Drought
- **Current Temperature:** `42.5°C` (Feels like: `43.8°C`)
- **Humidity:** `14%` | **Wind:** `18.5 km/h`
- **Triggered Alerts:**
  - `🔥 [CRITICAL] High Temperature Alert (42.5°C vs Threshold >= 35.0°C)`
- **Safety Action:** Logistics cold-chain check, hydration advisory, outdoor work restrictions between 11 AM - 4 PM.

### Scenario 2: `Mumbai` - Tropical Thunderstorm & Heavy Rain
- **Current Temperature:** `28.2°C` | **Rainfall (1h):** `28.4 mm`
- **Humidity:** `94%` | **Wind:** `48.0 km/h`
- **Triggered Alerts:**
  - `⛈️ [CRITICAL] Severe Storm Warning: Torrential downpour`
  - `💨 [WARNING] Gale Force Wind Alert (48 km/h vs Threshold >= 40 km/h)`
  - `💧 [ADVISORY] Excessive Humidity Alert (94% vs Threshold >= 85%)`
  - `⚠️ [WARNING] Heavy Rain Forecast Ahead (95% likelihood on Day 1)`
- **Safety Action:** Municipal stormwater drainage inspection, halt outdoor construction cranes, avoid waterlogged roadways.

### Scenario 3: `Chicago` - Freezing Cold & Blizzard
- **Current Temperature:** `-8.5°C` (Feels like: `-16.2°C`)
- **Humidity:** `78%` | **Wind:** `52.0 km/h`
- **Triggered Alerts:**
  - `❄️ [CRITICAL] Freezing Condition Alert (-8.5°C vs Threshold <= 0°C)`
  - `💨 [CRITICAL] Gale Force Wind Alert (52.0 km/h)`
- **Safety Action:** Agricultural frost protection, thermal insulation, black ice travel advisory.

### Scenario 4: `London` - Mild Overcast Day
- **Current Temperature:** `16.4°C` | **Humidity:** `68%` | **Wind:** `16.0 km/h`
- **Triggered Alerts:** None (`[✓] CLEAR: All meteorological indicators normal`)
- **Safety Action:** Normal operations for aviation, shipping, and outdoor events.

### Scenario 5: `Tokyo` - Monsoon Outer Bands & High Humidity
- **Current Temperature:** `31.5°C` | **Humidity:** `89%` | **Wind:** `42.0 km/h`
- **Precipitation:** `14.2 mm/h`
- **Triggered Alerts:** Excessive Humidity Alert, Gale Wind Alert, Active Rain Warning.

---

## 3. How to Run Simulation Mode

### Via Command-Line Interface (CLI):
```bash
# Run specific scenario
python main.py --sim Phoenix
python main.py --sim Mumbai
python main.py --sim Chicago

# Or launch the interactive terminal menu
python main.py
# Select Option 3: Virtual Simulation Scenarios
```

### Via Streamlit Web Dashboard:
```bash
streamlit run app.py
```
1. Open the sidebar on the left.
2. Under **Data Source Mode**, select **🧪 Virtual Simulation Lab (Offline Test)**.
3. Choose your scenario from the dropdown (e.g. *Mumbai (Severe Monsoon Storm)*).
4. Watch the alert cards, metric badges, and forecast charts update instantaneously!

---

## 4. Portfolio & GitHub Evidence Checklist

When documenting this project for your GitHub portfolio or course submission:

### 📸 Screenshots to Capture:
1. **Streamlit Web Dashboard:** Live metrics, active alert banners (Critical red, Warning yellow), and Plotly forecast curves.
2. **Terminal CLI Execution:** Clean ANSI-colored terminal output showing `python main.py --sim Mumbai`.
3. **Generated Matplotlib Chart:** High-res image exported at `outputs/forecast_mumbai.png`.
4. **Generated CSV & JSON Reports:** Open `reports/forecast_mumbai_*.csv` in Excel or VS Code.

### 🛡️ What Sensitive Information Must NEVER Be Uploaded:
- ❌ **`.env` file containing your personal API keys** (ensure `.env` is listed in `.gitignore`).
- ❌ Private credentials, passwords, or personal email tokens.
- ❌ Python cache files (`__pycache__/`, `*.pyc`).
- ❌ Virtual environment directories (`venv/`, `.venv/`).

### ✅ What To Commit to GitHub:
- `src/` (all modular Python source code)
- `data/sample_weather.json` (simulation dataset)
- `images/` (app screenshots & preview charts)
- `docs/` (Architecture and interview documentation)
- `main.py` & `app.py`
- `requirements.txt`
- `.env.example` (clean template with placeholders)
- `.gitignore`
- `README.md`
