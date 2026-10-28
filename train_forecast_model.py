from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sample_telemetry.csv"
MODEL_FILE = BASE_DIR / "forecast_model.joblib"
METRICS_FILE = BASE_DIR / "forecast_metrics.json"

WEATHER = [
    "ambient_temp_c",
    "humidity_pct",
    "solar_irradiance_wm2",
]

FEATURES = WEATHER + [
    "hour",
    "day_of_week",
    "day_of_year",
    "previous_demand_kw",
    "demand_24h_ago_kw",
]

TARGET = "target_demand_kw"


def make_features(df):
    result = df.copy()
    ts = pd.to_datetime(result["timestamp"])

    result["hour"] = ts.dt.hour
    result["day_of_week"] = ts.dt.dayofweek
    result["day_of_year"] = ts.dt.dayofyear

    result["previous_demand_kw"] = result[TARGET].shift(1)
    result["demand_24h_ago_kw"] = result[TARGET].shift(24)

    return result


def main():
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    required = ["timestamp"] + WEATHER + [TARGET]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for col in WEATHER + [TARGET]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=required).reset_index(drop=True)
    featured = make_features(df).dropna(subset=FEATURES + [TARGET])

    # Chronological holdout: the final 20% is never used for fitting.
    split = int(len(featured) * 0.8)
    train = featured.iloc[:split]
    test = featured.iloc[split:]

    X_train = train[FEATURES]
    y_train = train[TARGET]
    X_test = test[FEATURES]
    y_test = test[TARGET]

    model = RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    metrics = {
        "model": "RandomForestRegressor",
        "rows_used": int(len(featured)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "mae_kw": round(float(mean_absolute_error(y_test, predictions)), 3),
        "rmse_kw": round(
            float(mean_squared_error(y_test, predictions) ** 0.5), 3
        ),
        "features": FEATURES,
        "target": TARGET,
        "split": "chronological final 20% holdout",
        "note": (
            "Historical demonstration model. Forecast quality must be "
            "validated before any operational use."
        ),
    }

    joblib.dump(model, MODEL_FILE)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("24-hour forecasting model trained successfully.")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()