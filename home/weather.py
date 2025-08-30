# services/weather.py
import requests
from django.conf import settings
from datetime import datetime, timezone

OPENWEATHER_API_KEY = getattr(settings, "OPENWEATHER_API_KEY", None)
BASE_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
BASE_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"

def humanize_timedelta(delta_seconds):
    """Convert seconds into human-readable 'in 2 days' / '3 hours ago'."""
    delta = abs(int(delta_seconds))
    days, remainder = divmod(delta, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{days} day{'s' if days > 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return "just now"

def get_weather(lat, lon):
    """
    Free plan weather fetcher:
    - current temp, humidity, wind
    - last rain (how long ago)
    - next expected rain (how long from now)
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "Missing API key"}

    try:
        # --- Current Weather ---
        current_url = f"{BASE_CURRENT}?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        current_resp = requests.get(current_url)
        current_resp.raise_for_status()
        current = current_resp.json()

        temp = current["main"]["temp"]
        humidity = current["main"]["humidity"]
        pressure = current["main"]["pressure"]
        wind_speed = current["wind"]["speed"]

        # Check if it rained recently
        rain_last_hour = current.get("rain", {}).get("1h", 0)
        last_rain = None
        if rain_last_hour > 0:
            # use dt (current time from API)
            ts = current["dt"]
            dt_obj = datetime.fromtimestamp(ts, tz=timezone.utc)
            diff_seconds = (datetime.now(timezone.utc) - dt_obj).total_seconds()
            last_rain = f"{humanize_timedelta(diff_seconds)} ago"

        # --- Forecast (next expected rain) ---
        forecast_url = f"{BASE_FORECAST}?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_resp = requests.get(forecast_url)
        forecast_resp.raise_for_status()
        forecast = forecast_resp.json()

        next_rain = None
        for entry in forecast["list"]:
            if "rain" in entry and entry["rain"].get("3h", 0) > 0:
                ts = entry["dt"]
                dt_obj = datetime.fromtimestamp(ts, tz=timezone.utc)
                diff_seconds = (dt_obj - datetime.now(timezone.utc)).total_seconds()
                if diff_seconds > 0:
                    next_rain = f"in {humanize_timedelta(diff_seconds)}"
                    break

        return {
            "temperature": temp,
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "last_rain": last_rain,
            "next_rain": next_rain,
        }

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
