
import os
from pathlib import Path

import requests
from dotenv import dotenv_values, set_key

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

values = dotenv_values(ENV_FILE)

accounts_url = values.get(
    "ZOHO_ACCOUNTS_URL",
    "https://accounts.zoho.in"
).rstrip("/")

refresh_token = values.get("ZOHO_REFRESH_TOKEN")
client_id = values.get("ZOHO_CLIENT_ID")
client_secret = values.get("ZOHO_CLIENT_SECRET")

if not all([refresh_token, client_id, client_secret]):
    print("ERROR: Missing OAuth configuration in .env")
    raise SystemExit(1)

try:
    response = requests.post(
        f"{accounts_url}/oauth/v2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=20,
    )

    data = response.json()

    if response.ok and data.get("access_token"):
        set_key(
            str(ENV_FILE),
            "ZOHO_OAUTH_TOKEN",
            data["access_token"],
        )
        print("SUCCESS: New access token saved to .env.")
        print("Token value was not displayed.")
    else:
        print("Token refresh failed.")
        print("HTTP status:", response.status_code)
        print("Zoho error:", data.get("error", "Unknown error"))

except requests.RequestException as exc:
    print("Network error:", type(exc).__name__)
