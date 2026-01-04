"""
app.config.py
-------------
Centralized environment-driven configuration for demo and deployment.

Quick test:
>>> import config
>>> print(config.DAILY_API_CALL_LIMIT)
Author: **Suganya P**
"""

import os

# App / Flask
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() in ("1", "true", "yes")

# Cache / Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# DB (demo uses SQLite by default)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/kittylit_demo.db")

# External API keys
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

# Business rules (configurable by env)
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 24 * 3600))  # 1 day
CACHE_EXPIRY_DAYS = int(os.getenv("CACHE_EXPIRY_DAYS", 5))
DAILY_API_CALL_LIMIT = int(os.getenv("DAILY_API_CALL_LIMIT", 600))
MIN_RESULTS_THRESHOLD = int(os.getenv("MIN_RESULTS_THRESHOLD", 5))

# Timeouts & retries for live API calls
LIVE_API_TIMEOUT_S = float(os.getenv("LIVE_API_TIMEOUT_S", 2.0))
LIVE_API_MAX_RETRIES = int(os.getenv("LIVE_API_MAX_RETRIES", 1))

# Feature flags
ENABLE_LIVE_API = os.getenv("ENABLE_LIVE_API", "true").lower() in ("1", "true", "yes")
ENABLE_CHATBOT_RAG = os.getenv("ENABLE_CHATBOT_RAG", "true").lower() in ("1", "true", "yes")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
