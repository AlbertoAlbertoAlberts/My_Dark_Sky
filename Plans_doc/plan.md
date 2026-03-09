# My Dark Sky — Implementation Plan

## Project Summary

Rebuild the Dark Sky weather app using **Python/Flask**, **SQLite/SQLAlchemy**, and **Tailwind CSS**. The app uses the **OpenWeather API** to display current weather, forecasts, and historical weather (time machine). Results are cached for 5 minutes. The final app is deployed to the cloud, and the URL is stored in `my_dark_sky_url.txt`.

---

## Phase 1: Project Setup & Structure ✅ DONE

- [x] Initialize project folder structure:
  ```
  My_dark_sky/
  ├── app.py                  # Flask application entry point
  ├── config.py               # Configuration (API keys, DB, etc.)
  ├── requirements.txt        # Python dependencies
  ├── my_dark_sky_url.txt     # Submit file (URL only)
  ├── .env                    # Environment variables (API key, secret key)
  ├── .gitignore
  ├── models.py               # SQLAlchemy models (cache table)
  ├── services/
  │   ├── __init__.py
  │   ├── weather_service.py  # OpenWeather API calls + cache logic
  │   └── geocoding_service.py # Location search / geocoding
  ├── templates/
  │   ├── base.html           # Base template with Tailwind
  │   ├── index.html          # Main page (current weather + forecast)
  │   ├── partials/
  │   │   ├── current_weather.html
  │   │   ├── hourly_forecast.html
  │   │   ├── daily_forecast.html
  │   │   ├── weather_details.html
  │   │   └── time_machine.html
  │   └── errors/
  │       └── 404.html
  └── static/
      ├── css/
      │   └── style.css       # Custom styles beyond Tailwind
      ├── js/
      │   └── app.js          # Frontend interactivity (search, geolocation, calendar)
      └── images/
          └── (weather icons if needed)
  ```
- [x] Create `requirements.txt`:
  - Flask
  - Flask-SQLAlchemy
  - requests
  - python-dotenv
  - gunicorn (for production deployment)
- [x] Create `.gitignore` (venv, .env, __pycache__, *.db, etc.)
- [x] Create `.env.example` with placeholder keys

---

## Phase 2: Database & Cache Layer ✅ DONE

- [x] Define SQLAlchemy model in `models.py`:
  - `WeatherCache` table with columns:
    - `id` (primary key)
    - `cache_key` (string, unique) — composed from lat/lon/date/type
    - `data` (text/JSON) — the cached API response
    - `created_at` (datetime) — timestamp for cache expiry
- [x] Implement cache logic in `services/weather_service.py`:
  - Before calling API → check cache for matching key where `created_at` is < 5 min ago
  - If cache hit → return cached data
  - If cache miss → call API, store result, return data
  - `cleanup_expired_cache()` function for periodic cleanup

---

## Phase 3: Weather Service / API Integration ✅ DONE

- [x] `services/weather_service.py`:
  - `get_current_weather(lat, lon)` — calls OpenWeather **Current Weather** API
    - Returns: temperature, feels like, high, low, humidity, wind speed, dew point, UV index, visibility, pressure, weather description, icon
  - `get_forecast(lat, lon)` — calls OpenWeather **5-day/3-hour forecast** API
    - Returns: hourly forecast entries for next 5 days
  - `get_onecall(lat, lon)` — calls OpenWeather **One Call API 3.0**
    - Returns: current + hourly (48h) + daily (8 days)
  - `get_historical_weather(lat, lon, dt)` — calls OpenWeather **Time Machine / Historical** API
    - Returns: weather data for the specified past date
  - `get_weather_data(lat, lon)` — tries One Call 3.0 first, falls back to current + forecast combo
  - All functions use the cache layer from Phase 2
- [x] `services/geocoding_service.py`:
  - `geocode(query)` — uses OpenWeather **Geocoding API** to convert city/address to lat/lon
  - `reverse_geocode(lat, lon)` — converts coordinates to a readable location name

---

## Phase 4: Flask Routes & Backend Logic ✅ DONE

- [x] `app.py` — main Flask app:
  - `GET /` — landing page, optionally detect user location via JS geolocation
  - `GET /weather?lat=...&lon=...&location=...` — main weather page (current + forecast)
  - `GET /api/weather?lat=...&lon=...` — JSON API for current weather (for AJAX)
  - `GET /api/timemachine?lat=...&lon=...&dt=...` — JSON API for historical weather
  - `GET /api/geocode?q=...` — JSON API for location search (for autocomplete)
  - Jinja template filters: `timestamp_to_hour`, `timestamp_to_day`, `timestamp_to_date`
- [x] `config.py`:
  - Load `.env` variables
  - Database URI (SQLite)
  - API key
  - Cache duration (300 seconds)

---

## Phase 5: Frontend — Templates & UI ✅ DONE

Goal: **Beautiful** UI matching the Dark Sky aesthetic (dark theme, clean typography, data-rich).

- [x] `templates/index.html` (combines base + layout):
  - Tailwind CSS via CDN
  - Dark theme (bg-dark-900, light text)
  - Navigation bar: logo, App, Maps, Help, About links
  - Search bar with autocomplete dropdown + geolocation button
  - Footer with links
  - Landing page with geolocation prompt
- [x] `templates/partials/current_weather.html`:
  - **Part 1 — Current Weather Section:**
    - Location name with pin icon
    - Weather stats bar: Wind, Humidity, Dew Pt, UV Index, Visibility, Pressure
    - Large temperature display + weather icon
    - "Feels Like", "Low", "High" sub-info
    - Weather description text
    - Hourly forecast strip (12 hours with icons + temps)
    - Full fallback for basic API (no One Call 3.0)
- [x] `templates/partials/daily_forecast.html`:
  - **Part 2 — Weekly Forecast Section:**
    - Summary text
    - 7-day forecast rows: day name, icon, low temp, gradient temperature bar, high temp, info button
    - Temperature bars dynamically sized based on actual min/max range
    - Fallback grouping for basic 3-hour forecast API
    - **TIME MACHINE** button
- [x] `templates/partials/time_machine.html`:
  - **Part 3 — Time Machine Section:**
    - Calendar date picker with month/year navigation
    - Past dates clickable, future dates disabled
    - Loading spinner + AJAX results display

---

## Phase 6: Frontend — JavaScript Interactivity ✅ DONE

- [x] `static/js/app.js`:
  - **Geolocation**: On page load buttons, request browser geolocation → redirect to weather page
  - **Search**: Debounced (300ms) autocomplete with geocoding API → dropdown suggestions, click-outside dismiss
  - **Time Machine**: Custom vanilla JS calendar with month/year navigation
    - Past dates clickable → AJAX call to `/api/timemachine` → renders hourly strip or snapshot
    - Future dates disabled, today highlighted with border
    - Selected date highlighted in teal
  - **Dynamic updates**: fetch() for all API calls, loading spinners, error display

---

## Phase 7: Styling Polish ✅ DONE

- [x] Fixed CSS — removed `@apply` (requires build step), replaced with plain CSS for Tailwind CDN compatibility
- [x] Dark theme throughout (bg-dark-900, custom color palette)
- [x] Weather icons — OpenWeather icon URLs with drop-shadow filter (`.weather-icon-lg`)
- [x] Temperature bars — gradient bars (blue→yellow→orange) with glow effect (`.temp-bar-fill`)
- [x] Responsive design — mobile-friendly with `.weather-hero` column layout on small screens
- [x] Custom scrollbar styling for dark theme
- [x] Hidden scrollbar on hourly forecast strip (`.hourly-scroll`)
- [x] Smooth fade-in animations on sections
- [x] Search dropdown rounded corners
- [x] Calendar day styling — hover, selected (teal), today (border), disabled states

---

## Phase 8: Testing & Refinement ✅ DONE

- [x] 32/32 automated tests passing (test_app.py)
- [x] Route tests: all 5 routes return correct status codes and content
- [x] Error handling: missing params return 400, missing location shows user-friendly error
- [x] API failure handling: try/except on weather fetch with friendly error message
- [x] Cache tests: fresh entries returned, expired entries purged, cleanup works
- [x] Static files: JS and CSS serve correctly with all expected content
- [x] Template tests: nav, footer, Tailwind CDN, dark theme, JS vars all present
- [x] Fixed deprecation warnings: `datetime.utcnow()` → `datetime.now(timezone.utc)`

---

## Phase 9: Deployment (Requires Your Action)

- [ ] Prepare for deployment:
  - Create `Procfile` (for Heroku) or deployment config
  - Ensure `gunicorn` in requirements
  - Set environment variables on the hosting platform
- [ ] Deploy to cloud platform

---

## Phase 10: Submission (Requires Your Action)

- [ ] Write the deployed URL into `my_dark_sky_url.txt`
- [ ] Push code to Gitea: `git@git.us.qwasar.io:my_dark_sky_20702`

---

# What I (Copilot) Will Do vs. What You Need To Do

## I will build (Phases 1–8):
1. Full project structure with all files
2. SQLAlchemy cache model
3. Weather service with OpenWeather API integration + 5-min cache
4. Geocoding service for location search
5. Flask routes (pages + JSON APIs)
6. Beautiful dark-themed Tailwind UI matching Dark Sky's style
7. JavaScript for geolocation, search, time machine calendar, and dynamic updates
8. All templates with current weather, weekly forecast, and time machine features

## What you need to do:

### Step 1: Get an OpenWeather API Key
1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Create a free account (or log in)
3. Go to "API keys" in your profile
4. Copy your API key
5. **Important**: For the "One Call API 3.0" (needed for daily forecast + historical data), you need to subscribe to it (there's a free tier with 1,000 calls/day). Go to [https://openweathermap.org/api/one-call-3](https://openweathermap.org/api/one-call-3) and subscribe.
6. Create a `.env` file in the project root with:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   FLASK_SECRET_KEY=any_random_string_here
   ```

### Step 2: Install Dependencies
```bash
cd /Users/apple/Documents/IT.Projects/STARTSCHOOL_QWASAR/My_dark_sky
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Run Locally & Test
```bash
source venv/bin/activate
python app.py
```
Open `http://localhost:5000` in your browser.

### Step 4: Deploy to Cloud
Choose one (I'll prepare the config for whichever you prefer):

**Option A — Render.com (easiest, free tier)**
1. Push code to GitHub/Gitea
2. Go to [render.com](https://render.com), connect your repo
3. Create a new "Web Service", select Python
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn app:app`
6. Add environment variables (`OPENWEATHER_API_KEY`, `FLASK_SECRET_KEY`)
7. Deploy → copy the URL

**Option B — Heroku**
1. Install Heroku CLI
2. `heroku create my-dark-sky-app`
3. `heroku config:set OPENWEATHER_API_KEY=... FLASK_SECRET_KEY=...`
4. `git push heroku main`
5. Copy the URL

**Option C — Railway.app (also easy, free tier)**
1. Go to [railway.app](https://railway.app), connect repo
2. Add environment variables
3. Deploy → copy URL

### Step 5: Submit
1. Paste your deployed URL into `my_dark_sky_url.txt` (just the URL, nothing else)
2. Push to Qwasar Gitea:
   ```bash
   git init
   git remote add origin git@git.us.qwasar.io:my_dark_sky_20702
   git add .
   git commit -m "My Dark Sky weather app"
   git push -u origin master
   ```

---

# API Endpoints Reference (OpenWeather)

| Feature | API Endpoint | Free Tier? |
|---------|-------------|------------|
| Current Weather | `/data/2.5/weather` | Yes |
| 5-Day Forecast | `/data/2.5/forecast` | Yes |
| One Call 3.0 (daily + hourly) | `/data/3.0/onecall` | Yes (1000/day) |
| Time Machine (historical) | `/data/3.0/onecall/timemachine` | Yes (1000/day) |
| Geocoding | `/geo/1.0/direct` | Yes |
| Reverse Geocoding | `/geo/1.0/reverse` | Yes |

> **Note**: If One Call 3.0 is not available, we can fall back to the free 5-day forecast API + current weather API as alternatives. Historical data would require One Call 3.0 subscription.



