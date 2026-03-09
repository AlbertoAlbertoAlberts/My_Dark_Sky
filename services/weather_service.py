import json
import requests
from datetime import datetime, timedelta, timezone
from models import db, WeatherCache
from config import OPENWEATHER_API_KEY, CACHE_DURATION

BASE_URL = "https://api.openweathermap.org"


def cleanup_expired_cache():
    """Remove all cache entries older than CACHE_DURATION."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=CACHE_DURATION)
    WeatherCache.query.filter(WeatherCache.created_at < cutoff).delete()
    db.session.commit()


def _get_cached(key):
    """Return cached data if it exists and is fresh (< 5 min old)."""
    entry = WeatherCache.query.filter_by(cache_key=key).first()
    if entry:
        age = (datetime.now(timezone.utc) - entry.created_at.replace(tzinfo=timezone.utc)).total_seconds()
        if age < CACHE_DURATION:
            return json.loads(entry.data)
        db.session.delete(entry)
        db.session.commit()
    return None


def _set_cache(key, data):
    """Store data in cache, replacing any existing entry for this key."""
    entry = WeatherCache.query.filter_by(cache_key=key).first()
    if entry:
        entry.data = json.dumps(data)
        entry.created_at = datetime.now(timezone.utc)
    else:
        entry = WeatherCache(cache_key=key, data=json.dumps(data))
        db.session.add(entry)
    db.session.commit()


def get_current_weather(lat, lon):
    """Get current weather for coordinates."""
    key = f"current:{round(lat,4)}:{round(lon,4)}"
    cached = _get_cached(key)
    if cached:
        return cached

    resp = requests.get(f"{BASE_URL}/data/2.5/weather", params={
        "lat": lat, "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    _set_cache(key, data)
    return data


def get_forecast(lat, lon):
    """Get 5-day / 3-hour forecast."""
    key = f"forecast:{round(lat,4)}:{round(lon,4)}"
    cached = _get_cached(key)
    if cached:
        return cached

    resp = requests.get(f"{BASE_URL}/data/2.5/forecast", params={
        "lat": lat, "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    _set_cache(key, data)
    return data


def get_onecall(lat, lon):
    """Get One Call 3.0 data (current + hourly + daily)."""
    key = f"onecall:{round(lat,4)}:{round(lon,4)}"
    cached = _get_cached(key)
    if cached:
        return cached

    resp = requests.get(f"{BASE_URL}/data/3.0/onecall", params={
        "lat": lat, "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "exclude": "minutely,alerts"
    }, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    _set_cache(key, data)
    return data


def get_historical_weather(lat, lon, dt):
    """Get historical weather via Open-Meteo Archive API (free, no key needed).
    dt: unix timestamp for the requested date.
    Returns hourly data with temperature, weather codes, humidity, wind, etc.
    """
    date_str = datetime.fromtimestamp(dt, tz=timezone.utc).strftime("%Y-%m-%d")
    key = f"history:{round(lat,4)}:{round(lon,4)}:{date_str}"
    cached = _get_cached(key)
    if cached:
        return cached

    resp = requests.get("https://archive-api.open-meteo.com/v1/archive", params={
        "latitude": lat,
        "longitude": lon,
        "start_date": date_str,
        "end_date": date_str,
        "hourly": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "temperature_unit": "celsius",
        "wind_speed_unit": "ms",
        "timezone": "auto"
    }, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    _set_cache(key, data)
    return data


def get_weather_data(lat, lon):
    """Try One Call 3.0 first; fall back to current + forecast combo."""
    try:
        data = get_onecall(lat, lon)
        return {"source": "onecall", "data": data}
    except Exception:
        pass

    # Fallback: use free basic APIs
    current = get_current_weather(lat, lon)
    forecast = get_forecast(lat, lon)
    return {"source": "basic", "current": current, "forecast": forecast}
