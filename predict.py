
import os
import numpy as np
import pandas as pd
import requests
import joblib
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.joblib"

load_dotenv(BASE_DIR / ".env")

QUICKML_ENDPOINT_URL = os.getenv("ZOHO_QUICKML_URL", "").strip()

ENDPOINT_KEY = (
    os.getenv("ENDPOINT_KEY")
    or os.getenv("ZOHO_QUICKML_ENDPOINT_KEY")
    or ""
).strip()

OAUTH_TOKEN = os.getenv("OAUTH_TOKEN", "").strip()
CATALYST_ORG = os.getenv("CATALYST_ORG", "").strip()
ENVIRONMENT = os.getenv("ZOHO_ENVIRONMENT", "Development").strip()

FEATURES = [
    "ambient_temp_c",
    "humidity_pct",
    "solar_irradiance_wm2",
]

_model = None


def predict(input_df: pd.DataFrame) -> np.ndarray:
    """Predict electricity demand in kW for each input row."""

    required = ["timestamp"] + FEATURES
    missing = [column for column in required if column not in input_df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if input_df.empty:
        return np.array([], dtype=float)

    # Try the published Zoho QuickML endpoint.
    if (
        QUICKML_ENDPOINT_URL
        and ENDPOINT_KEY
        and OAUTH_TOKEN
        and CATALYST_ORG
    ):
        try:
            predictions = []

            headers = {
                "Authorization": f"Zoho-oauthtoken {OAUTH_TOKEN}",
                "X-QUICKML-ENDPOINT-KEY": ENDPOINT_KEY,
                "CATALYST-ORG": CATALYST_ORG,
                "Environment": ENVIRONMENT,
                "Content-Type": "application/json",
            }

            for timestamp in input_df["timestamp"]:
                formatted_timestamp = pd.to_datetime(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                payload = {
                    "data": {
                        "timestamp": formatted_timestamp
                    }
                }

                response = requests.post(
                    QUICKML_ENDPOINT_URL,
                    json=payload,
                    headers=headers,
                    timeout=20,
                )

                response.raise_for_status()
                result = response.json().get("result", {})

                if not isinstance(result, dict) or not result:
                    raise ValueError(
                        f"Unexpected QuickML response: {response.text}"
                    )

                if formatted_timestamp in result:
                    value = result[formatted_timestamp]
                elif len(result) == 1:
                    value = next(iter(result.values()))
                else:
                    raise ValueError(
                        f"Unexpected QuickML result: {response.text}"
                    )

                predictions.append(float(value))

            predictions = np.asarray(predictions, dtype=float)

            if (
                len(predictions) == len(input_df)
                and np.isfinite(predictions).all()
            ):
                return predictions

            raise ValueError("QuickML returned invalid predictions.")

        except Exception as exc:
            print(
                "Warning: QuickML request failed; "
                f"using local model instead ({exc})."
            )

    # Local fallback: keeps the evaluator interface working.
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Local model not found: {MODEL_PATH}"
            )
        _model = joblib.load(MODEL_PATH)

    features = input_df[FEATURES].copy()
    predictions = np.asarray(_model.predict(features), dtype=float)

    if len(predictions) != len(input_df):
        raise ValueError("Model returned the wrong number of predictions.")

    if not np.isfinite(predictions).all():
        raise ValueError("Model returned NaN or infinite predictions.")

    return predictions


if __name__ == "__main__":
    sample_path = BASE_DIR / "sample_test_input.csv"
    sample_df = pd.read_csv(sample_path)

    predictions = predict(sample_df)

    print(f"Generated {len(predictions)} predictions.")
    print(f"First 5 predictions: {np.round(predictions[:5], 2)}")
