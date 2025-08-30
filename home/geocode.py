import requests
from django.conf import settings

GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"

def geocode_location(location: str):
    """
    Takes a city/location name, returns (lat, lon) as floats.
    """
    params = {
        "q": location,
        "limit": 1,
        "appid": settings.OPENWEATHER_API_KEY,
    }
    resp = requests.get(GEOCODE_URL, params=params, timeout=10).json()
    if resp and isinstance(resp, list) and "lat" in resp[0]:
        print(resp)
        return resp[0]["lat"], resp[0]["lon"]
    return None, None
