from forecast import forecast_next_24_hours
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.joblib"
METRICS_PATH = BASE_DIR / "metrics.json"

app = FastAPI(
    title="VoltVision API",
    description="Electricity demand forecasting using a local trained model",
    version="2.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
# Load the trained model once when the API starts.
try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    raise RuntimeError(
        f"Could not load model at {MODEL_PATH}. Run python train_model.py first."
    ) from exc

FEATURES = [
    "ambient_temp_c",
    "humidity_pct",
    "solar_irradiance_wm2",
]


class ForecastRequest(BaseModel):
    timestamp: datetime
    ambient_temp_c: float = 25
    humidity_pct: float = 60
    solar_irradiance_wm2: float = 300
    recent_demand_kw: list[float] = Field(default_factory=list)


@app.get("/")
def home():
    return {
        "project": "VoltVision",
        "status": "running",
        "model": "Local Random Forest",
    }


@app.get("/metrics")
def metrics():
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Metrics file not found. Run python train_model.py first.",
        )

    with METRICS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.post("/predict")
def predict(request: ForecastRequest):
    features = pd.DataFrame(
        [
            {
                "ambient_temp_c": request.ambient_temp_c,
                "humidity_pct": request.humidity_pct,
                "solar_irradiance_wm2": request.solar_irradiance_wm2,
            }
        ],
        columns=FEATURES,
    )

    try:
        prediction = float(model.predict(features)[0])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Local model prediction failed. Check the trained model.",
        ) from exc

    # Hackathon transition rules
    hour = request.timestamp.hour
    renewable_hours = 18 <= hour <= 22

    if prediction > 160 or renewable_hours:
        grid_mode = "Renewable Storage Mode"
    else:
        grid_mode = "Main Grid Mode"

    critical_overload = prediction >= 200

    return {
        "timestamp": request.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "predicted_demand_kw": round(prediction, 2),
        "unit": "kW",
        "model": "Local Random Forest",
        "forecast_horizon": "Single timestamp prediction",
        "grid_mode": grid_mode,
        "critical_overload_alert": critical_overload,
        "alert_message": (
            "CRITICAL OVERLOAD ALERT"
            if critical_overload
            else "Normal operating range"
        ),
        "disclaimer": (
            "Demonstration forecast, not validated for safety-critical "
            "grid control."
        ),
    }
@app.get("/forecast/24h")
def forecast_24_hours():
    try:
        forecasts = forecast_next_24_hours()

        return {
            "project": "VoltVision",
            "forecast_horizon_hours": 24,
            "forecast_count": len(forecasts),
            "assumption": (
                "Latest observed weather held constant. "
                "Historical demonstration forecast only."
            ),
            "forecasts": forecasts,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"24-hour forecast failed: {exc}",
        ) from exc