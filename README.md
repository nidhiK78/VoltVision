# VoltVision — Local Demand Forecast Backend

A local fallback for the HackSphere 3.0 demo. It trains a regression model from the provided hourly telemetry CSV and exposes a `/predict` API for a one-hour-ahead demand estimate.

## 1. Setup (Windows PowerShell)
Open this folder in VS Code, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python train_model.py
uvicorn app:app --reload
```

If PowerShell blocks activation, run this in the same terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Keep the server terminal open. Visit `http://127.0.0.1:8000/docs` to test the API.

## 2. API request
Use `POST /predict`. `recent_demand_kw` must contain exactly 24 consecutive hourly demand values in chronological order: oldest first, most recent last. Supply weather values for the forecast timestamp.

```json
{
  "timestamp": "2015-06-16T15:00:00",
  "ambient_temp_c": 31.5,
  "humidity_pct": 60,
  "solar_irradiance_wm2": 150,
  "recent_demand_kw": [103.68, 91.19, 92.60, 95.0, 98.0, 100.0, 105.0, 112.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0, 210.0, 220.0, 230.0, 240.0, 248.35, 244.46, 215.62]
}
```

Those 24 values are only an example payload, not a claim that they are the exact 24 preceding rows. For a proper test, use the last 24 `target_demand_kw` rows before the requested timestamp from the CSV.

## 3. Frontend teammate integration
- API base URL while both apps run on the same computer: `http://127.0.0.1:8000`
- Endpoint: `POST /predict`
- Interactive API docs: `http://127.0.0.1:8000/docs`
- For a frontend on another device, `127.0.0.1` will not work; use the backend machine's LAN IP and configure CORS / network access before connecting.

## Data and evaluation notes
- The included CSV has 4,000 rows and 5 columns; there are no missing values or duplicate full rows.
- The script sorts timestamps and evaluates on the latest 20% of time-ordered examples, then retrains the model on all eligible rows for the API.
- This is a demo model. Accuracy metrics are generated locally by `python train_model.py`; do not claim they are official grid forecasts.
