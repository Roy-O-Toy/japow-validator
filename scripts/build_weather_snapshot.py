import json
import requests
from datetime import datetime, timezone
from pathlib import Path

LOCATIONS_FILE = "resorts_locations.json"
SNAPSHOT_DIR = Path("snapshots/weather")
PUBLIC_DIR = Path("public/japow-weather")

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,wind_speed_10m",
        "daily": "snowfall_sum",
        "past_days": 1,
        "timezone": "UTC"
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()

def main():
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")

    with open(LOCATIONS_FILE, "r") as f:
        resorts = json.load(f)

    output = {
        "meta": {
            "schema_version": "1.0",
            "snapshot_date_utc": now.strftime("%Y-%m-%d"),
            "generated_at_utc": now.isoformat(),
            "source": "Open-Meteo",
            "notes": "Snapshot of recent conditions. Not live."
        },
        "resorts": []
    }

    for r in resorts:
        data = fetch_weather(r["lat"], r["lon"])

        snowfall = data.get("daily", {}).get("snowfall_sum", [0])[0]
        temps = data.get("hourly", {}).get("temperature_2m", [])
        winds = data.get("hourly", {}).get("wind_speed_10m", [])

        output["resorts"].append({
            "resort_name": r["resort_name"],
            "region": r["region"],
            "last_verified_utc": now.isoformat(),
            "conditions": {
                "new_snow_24h_cm": round(snowfall),
                "temperature_c": round(sum(temps) / len(temps), 1) if temps else None,
                "wind_kph": round(sum(winds) / len(winds), 1) if winds else None,
                "summary": "Recent conditions snapshot"
            }
        })

    snapshot_path = SNAPSHOT_DIR / f"Japow-weather_{date_str}.json"
    latest_path = PUBLIC_DIR / "latest.json"

    with open(snapshot_path, "w") as f:
        json.dump(output, f, indent=2)

    with open(latest_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Weather snapshot written: {snapshot_path}")

if __name__ == "__main__":
    main()
