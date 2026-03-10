import math
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, jsonify
from config import FLASK_SECRET_KEY, SQLALCHEMY_DATABASE_URI
from models import db
from services import weather_service, geocoding_service

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# Countries that primarily use 12-hour AM/PM clock
AMPM_COUNTRIES = {'US', 'AU', 'CA', 'PH', 'MY', 'BD', 'EG', 'SA', 'CO'}


def _local_dt(ts, tz_offset=0):
    """Convert unix timestamp to datetime in the location's timezone."""
    return datetime(1970, 1, 1) + timedelta(seconds=ts + tz_offset)


# Jinja template filters
@app.template_filter("timestamp_to_hour")
def timestamp_to_hour(ts, country=None, tz_offset=0):
    dt = _local_dt(ts, tz_offset)
    if country and country.upper() in AMPM_COUNTRIES:
        return dt.strftime("%-I %p")
    return dt.strftime("%H")


@app.template_filter("timestamp_to_time")
def timestamp_to_time(ts, country=None, tz_offset=0):
    dt = _local_dt(ts, tz_offset)
    if country and country.upper() in AMPM_COUNTRIES:
        return dt.strftime("%-I:%M %p")
    return dt.strftime("%H:%M")


@app.template_filter("timestamp_to_day")
def timestamp_to_day(ts, tz_offset=0):
    return _local_dt(ts, tz_offset).strftime("%a")


@app.template_filter("timestamp_to_date")
def timestamp_to_date(ts, tz_offset=0):
    return _local_dt(ts, tz_offset).strftime("%Y-%m-%d")


def _moon_phase(ts):
    """Return (phase_name, phase_fraction, emoji) for a unix timestamp."""
    dt = datetime.fromtimestamp(ts)
    # Conway's algorithm for moon phase approximation
    year = dt.year
    month = dt.month
    day = dt.day
    if month <= 2:
        year -= 1
        month += 12
    a = math.floor(year / 100)
    b = math.floor(a / 4)
    c = 2 - a + b
    e = math.floor(365.25 * (year + 4716))
    f = math.floor(30.6001 * (month + 1))
    jd = c + day + e + f - 1524.5
    days_since_new = (jd - 2451550.1) % 29.530588853
    phase_frac = days_since_new / 29.530588853  # 0..1
    phases = [
        (0.0, "New Moon", "\U0001F311"),
        (0.125, "Waxing Crescent", "\U0001F312"),
        (0.25, "First Quarter", "\U0001F313"),
        (0.375, "Waxing Gibbous", "\U0001F314"),
        (0.5, "Full Moon", "\U0001F315"),
        (0.625, "Waning Gibbous", "\U0001F316"),
        (0.75, "Last Quarter", "\U0001F317"),
        (0.875, "Waning Crescent", "\U0001F318"),
        (1.0, "New Moon", "\U0001F311"),
    ]
    name, emoji = "New Moon", "\U0001F311"
    for i in range(len(phases) - 1):
        lo = phases[i][0]
        hi = phases[i + 1][0]
        if lo <= phase_frac < hi:
            mid = (lo + hi) / 2
            if phase_frac < mid:
                name, emoji = phases[i][1], phases[i][2]
            else:
                name, emoji = phases[i + 1][1], phases[i + 1][2]
            break
    illumination = round((1 - math.cos(2 * math.pi * phase_frac)) / 2 * 100)
    return {"name": name, "emoji": emoji, "illumination": illumination}


@app.template_filter("moon_phase")
def moon_phase_filter(ts):
    return _moon_phase(ts)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/weather")
def weather():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    location = request.args.get("location", "")
    country = ""

    try:
        if lat is None or lon is None:
            if location:
                results = geocoding_service.geocode(location, limit=1)
                if results:
                    lat = results[0]["lat"]
                    lon = results[0]["lon"]
                    country = results[0].get("country", "")
                    location, _ = geocoding_service.reverse_geocode(lat, lon)
                else:
                    return render_template("index.html", error="Location not found.")
            else:
                return render_template("index.html", error="Please provide a location.")
        else:
            if not location:
                location, country = geocoding_service.reverse_geocode(lat, lon)
            else:
                _, country = geocoding_service.reverse_geocode(lat, lon)

        weather_data = weather_service.get_weather_data(lat, lon)
    except Exception:
        return render_template("index.html", error="Could not fetch weather data. Please check your API key or try again later.")
    # Extract timezone offset (seconds from UTC) from weather data
    if weather_data["source"] == "onecall":
        tz_offset = weather_data["data"].get("timezone_offset", 0)
    else:
        tz_offset = weather_data["current"].get("timezone", 0)

    return render_template("index.html",
                           weather=weather_data,
                           location=location,
                           country=country,
                           lat=lat, lon=lon,
                           tz_offset=tz_offset)


# --- JSON API endpoints ---

@app.route("/api/geocode")
def api_geocode():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    try:
        results = geocoding_service.geocode(q)
        return jsonify(results)
    except Exception:
        return jsonify([])  


@app.route("/api/weather")
def api_weather():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400
    try:
        data = weather_service.get_weather_data(lat, lon)
        return jsonify(data)
    except Exception:
        return jsonify({"error": "Could not fetch weather data"}), 502


@app.route("/api/timemachine")
def api_timemachine():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    dt = request.args.get("dt", type=int)
    if lat is None or lon is None or dt is None:
        return jsonify({"error": "lat, lon, and dt (unix timestamp) required"}), 400
    try:
        data = weather_service.get_historical_weather(lat, lon, dt)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
