from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sample_telemetry.csv"
MODEL_FILE = BASE_DIR / "model.joblib"
METRICS_FILE = BASE_DIR / "metrics.json"

FEATURES = [
    "ambient_temp_c",
    "humidity_pct",
    "solar_irradiance_wm2",
]

TARGET = "target_demand_kw"


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)

    required = FEATURES + [TARGET]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing dataset columns: {missing}")

    df = df[required].apply(pd.to_numeric, errors="coerce").dropna()

    if len(df) < 20:
        raise ValueError(
            f"Only {len(df)} usable rows found. At least 20 are recommended."
        )

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        min_samples_leaf=2,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    metrics = {
        "model": "RandomForestRegressor",
        "rows_used": int(len(df)),
        "mae_kw": round(float(mean_absolute_error(y_test, predictions)), 3),
        "rmse_kw": round(
            float(mean_squared_error(y_test, predictions) ** 0.5), 3
        ),
        "features": FEATURES,
        "target": TARGET,
        "note": (
            "Metrics use a random holdout split. This is a demonstration "
            "model, not a validated operational grid forecast."
        ),
    }

    joblib.dump(model, MODEL_FILE)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("VoltVision local model trained successfully!")
    print(f"Rows used: {len(df)}")
    print(f"Model saved to: {MODEL_FILE}")
    print(f"Metrics saved to: {METRICS_FILE}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()