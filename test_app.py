"""Phase 8: Testing & Refinement"""
from app import app
from models import db, WeatherCache
from datetime import datetime, timedelta, timezone
import json

def run_tests():
    with app.app_context():
        client = app.test_client()
        passed = 0
        failed = 0

        def check(name, condition):
            nonlocal passed, failed
            if condition:
                print(f"  [PASS] {name}")
                passed += 1
            else:
                print(f"  [FAIL] {name}")
                failed += 1

        # === Route Tests ===
        print("\n--- Route Tests ---")

        r = client.get('/')
        check("GET / returns 200", r.status_code == 200)
        check("Landing has Dark Sky branding", b'Dark Sky' in r.data)
        check("Landing has search input", b'search-input' in r.data)
        check("Landing has geolocation button", b'landing-geo-btn' in r.data)

        r = client.get('/weather')
        check("GET /weather (no params) returns 200", r.status_code == 200)
        check("Shows error for missing location", b'Please provide a location' in r.data)

        r = client.get('/api/geocode')
        check("GET /api/geocode (empty) returns []", r.status_code == 200 and r.json == [])

        r = client.get('/api/geocode?q=%20%20')
        check("GET /api/geocode (whitespace) returns []", r.status_code == 200 and r.json == [])

        r = client.get('/api/weather')
        check("GET /api/weather (no params) returns 400", r.status_code == 400)

        r = client.get('/api/weather?lat=40')
        check("GET /api/weather (missing lon) returns 400", r.status_code == 400)

        r = client.get('/api/timemachine')
        check("GET /api/timemachine (no params) returns 400", r.status_code == 400)

        r = client.get('/api/timemachine?lat=40&lon=-74')
        check("GET /api/timemachine (missing dt) returns 400", r.status_code == 400)

        # === Static Files ===
        print("\n--- Static File Tests ---")

        r = client.get('/static/js/app.js')
        check("JS file serves", r.status_code == 200)
        js = r.data.decode()
        check("JS has geolocate function", 'function geolocate' in js)
        check("JS has renderCalendar", 'function renderCalendar' in js)
        check("JS has loadTimeMachine", 'async function loadTimeMachine' in js)
        check("JS has search autocomplete", 'searchTimeout' in js)

        r = client.get('/static/css/style.css')
        check("CSS file serves", r.status_code == 200)
        css = r.data.decode()
        check("CSS has no @apply", '@apply' not in css)
        check("CSS has cal-day styling", '.cal-day' in css)
        check("CSS has responsive media query", '@media' in css)

        # === Cache Tests ===
        print("\n--- Cache Tests ---")

        # Clean up any existing test entries
        WeatherCache.query.filter(WeatherCache.cache_key.like('test:%')).delete()
        db.session.commit()

        # Insert a fresh cache entry
        entry = WeatherCache(
            cache_key='test:cache:fresh',
            data=json.dumps({"temp": 72, "desc": "sunny"}),
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(entry)
        db.session.commit()

        # Verify fresh entry is found
        found = WeatherCache.query.filter_by(cache_key='test:cache:fresh').first()
        check("Cache: fresh entry stored", found is not None)
        check("Cache: data is correct", json.loads(found.data)["temp"] == 72)

        # Insert an expired entry (6 min old)
        expired = WeatherCache(
            cache_key='test:cache:expired',
            data=json.dumps({"temp": 50}),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=6)
        )
        db.session.add(expired)
        db.session.commit()

        # Test cleanup function
        from services.weather_service import cleanup_expired_cache, _get_cached
        
        # _get_cached should return None for expired
        result = _get_cached('test:cache:expired')
        check("Cache: expired entry returns None", result is None)

        # _get_cached should return data for fresh
        result = _get_cached('test:cache:fresh')
        check("Cache: fresh entry returns data", result is not None and result["temp"] == 72)

        # Bulk cleanup
        expired2 = WeatherCache(
            cache_key='test:cache:expired2',
            data=json.dumps({"temp": 40}),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=10)
        )
        db.session.add(expired2)
        db.session.commit()
        cleanup_expired_cache()
        remaining = WeatherCache.query.filter(WeatherCache.cache_key.like('test:%')).all()
        keys = [r.cache_key for r in remaining]
        check("Cache: cleanup removes expired entries", 'test:cache:expired2' not in keys)
        check("Cache: cleanup keeps fresh entries", 'test:cache:fresh' in keys)

        # Cleanup test data
        WeatherCache.query.filter(WeatherCache.cache_key.like('test:%')).delete()
        db.session.commit()

        # === Template Content Tests ===
        print("\n--- Template Content Tests ---")

        r = client.get('/')
        html = r.data.decode()
        check("Has navigation bar", 'nav' in html.lower())
        check("Has footer", 'footer' in html.lower())
        check("Has Tailwind CDN", 'cdn.tailwindcss.com' in html)
        check("Has dark theme colors", 'bg-dark-900' in html or '#0a0f1a' in html)
        check("Has APP_LAT/APP_LON JS vars", 'APP_LAT' in html and 'APP_LON' in html)

        # === Summary ===
        print(f"\n{'='*40}")
        print(f"Results: {passed} passed, {failed} failed out of {passed+failed} tests")
        if failed == 0:
            print("ALL TESTS PASSED!")
        return failed == 0

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
