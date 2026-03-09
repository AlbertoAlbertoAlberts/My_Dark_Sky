import requests
from config import OPENWEATHER_API_KEY

BASE_URL = "https://api.openweathermap.org"


def geocode(query, limit=5):
    """Convert location name to coordinates."""
    resp = requests.get(f"{BASE_URL}/geo/1.0/direct", params={
        "q": query,
        "limit": limit,
        "appid": OPENWEATHER_API_KEY
    }, timeout=10)
    resp.raise_for_status()
    return resp.json()


def reverse_geocode(lat, lon):
    """Convert coordinates to (location_name, country_code)."""
    resp = requests.get(f"{BASE_URL}/geo/1.0/reverse", params={
        "lat": lat, "lon": lon,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY
    }, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    if results:
        r = results[0]
        parts = [r.get("name", "")]
        if r.get("state"):
            parts.append(r["state"])
        if r.get("country"):
            parts.append(r["country"])
        return ", ".join(parts), r.get("country", "")
    return f"{lat}, {lon}", ""
