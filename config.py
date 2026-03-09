import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
SQLALCHEMY_DATABASE_URI = "sqlite:///weather_cache.db"
CACHE_DURATION = 300  # 5 minutes in seconds
