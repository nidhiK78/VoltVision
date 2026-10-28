from pathlib import Path

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "forecast_model.joblib"
DATA_PATH = BASE_DIR / "data" / "sample_telemetry.csv"

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


def load_history():
    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    if len(df) < 25:
        raise ValueError("At least 25 historical hourly records are required.")

    return df


def forecast_next_24_hours(weather_forecast=None):
    """
    Generate a 24-hour demonstration forecast.

    weather_forecast:
        Optional list of 24 dictionaries, each containing:
        ambient_temp_c, humidity_pct, solar_irradiance_wm2.

    If omitted, the latest observed weather is held constant.
    These fallback weather values are assumptions, not actual future weather.
    """
    model = joblib.load(MODEL_PATH)
    history = load_history()

    history = history.tail(24).copy()
    previous_demands = history["target_demand_kw"].astype(float).tolist()

    last_timestamp = pd.Timestamp(history["timestamp"].iloc[-1])

    if weather_forecast is not None and len(weather_forecast) != 24:
        raise ValueError("weather_forecast must contain exactly 24 entries.")

    latest_weather = history.iloc[-1][WEATHER].to_dict()
    results = []

    for step in range(1, 25):
        timestamp = last_timestamp + pd.Timedelta(hours=step)

        if weather_forecast is None:
            weather = latest_weather.copy()
        else:
            weather = weather_forecast[step - 1]

        row = {
            **weather,
            "hour": timestamp.hour,
            "day_of_week": timestamp.dayofweek,
            "day_of_year": timestamp.dayofyear,
            "previous_demand_kw": previous_demands[-1],
            "demand_24h_ago_kw": previous_demands[-24],
        }

        X = pd.DataFrame([row], columns=FEATURES)
        prediction = max(0.0, float(model.predict(X)[0]))

        previous_demands.append(prediction)

        hour = timestamp.hour
        grid_mode = (
            "Renewable Storage Mode"
            if prediction > 160 or 18 <= hour <= 22
            else "Main Grid Mode"
        )

        results.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "predicted_demand_kw": round(prediction, 2),
            "grid_mode": grid_mode,
            "critical_overload_alert": prediction >= 200,
        })

    return results


if __name__ == "__main__":
    forecast = forecast_next_24_hours()

    print("24-hour demonstration forecast")
    print("Assumption: latest observed weather held constant.")
    print(pd.DataFrame(forecast).to_string(index=False))