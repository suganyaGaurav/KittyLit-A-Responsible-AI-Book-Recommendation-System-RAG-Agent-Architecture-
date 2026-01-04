"""
agents/agent_tools.py
---------------------
Helper functions for:
- Fetching live book data from Google Books API,
- Managing in-memory cache,
- Tracking daily API usage quota,
- Normalizing API responses to our internal book schema.

Author: **Suganya P**
Updated: 2025-12-09
CHANGE:
    - Replace old year filtering with year_category buckets
    - Normalize Google Books API results into year_category
"""

import requests
import json
import os
import logging
from datetime import datetime
from .errors import LiveDataFetchError

# Import the same year-category bucket mapper from data_loader
from app.data_loader import map_year_to_category

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s][agent_tools] %(message)s')
logger = logging.getLogger(__name__)

CACHE = {}
USAGE_FILE = "data/api_usage.json"
DAILY_LIMIT = 600


# ============================================================
# API QUOTA CHECK
# ============================================================
def can_make_api_call() -> bool:
    today_str = datetime.now().strftime("%Y-%m-%d")
    usage = {"date": today_str, "count": 0}

    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage = json.load(f)

    if usage.get("date") != today_str:
        usage = {"date": today_str, "count": 0}

    can_call = usage.get("count", 0) < DAILY_LIMIT
    return can_call


def increment_api_call_count():
    today_str = datetime.now().strftime("%Y-%m-%d")
    usage = {"date": today_str, "count": 0}

    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage = json.load(f)

    if usage.get("date") != today_str:
        usage = {"date": today_str, "count": 0}

    usage["count"] += 1

    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f)


def get_daily_api_call_count() -> int:
    today_str = datetime.now().strftime("%Y-%m-%d")
    usage = {"date": today_str, "count": 0}

    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage = json.load(f)

    if usage.get("date") != today_str:
        return 0

    return usage.get("count", 0)


# ============================================================
# LIVE API FETCH
# ============================================================
def fetch_live_data(query_params):
    """
    Fetch book info from Google Books API based on filters.

    UPDATED:
        - Removed old numeric year filtering
        - Live API results now mapped into year_category buckets
    """
    if not can_make_api_call():
        raise LiveDataFetchError("Daily API call limit reached")

    try:
        url = "https://www.googleapis.com/books/v1/volumes"

        q_parts = []
        if query_params.get("title"):
            q_parts.append(f'intitle:{query_params["title"]}')
        if query_params.get("genre"):
            q_parts.append(f'subject:{query_params["genre"]}')

        q = " ".join(q_parts) if q_parts else "children"

        params = {"q": q, "maxResults": 40}

        if query_params.get("language"):
            params["langRestrict"] = query_params["language"]

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            raise LiveDataFetchError(f"Google API returned status {response.status_code}")

        increment_api_call_count()

        # NOTICE: we no longer pass filter_year (numeric); we use year_category downstream
        data = response.json()
        normalized_books = normalize_google_books_response(data)

        return normalized_books

    except Exception as e:
        logger.error(f"Error during live data fetch: {e}")
        raise LiveDataFetchError(str(e))


# ============================================================
# NORMALIZATION
# ============================================================
def normalize_google_books_response(api_response):
    """
    Convert Google Books API raw data → internal schema with year_category.

    Returns:
        list of books with: title, author, year_category, description, isbn, thumbnail_url, source
    """
    normalized = []
    items = api_response.get("items", [])

    for item in items:
        volume = item.get("volumeInfo", {})

        pub_date = volume.get("publishedDate", "")
        raw_year = pub_date.split("-")[0] if pub_date else None

        # MAP numeric year → year_category
        year_category = map_year_to_category(raw_year)

        # Extract ISBN
        isbn = None
        for identifier in volume.get("industryIdentifiers", []):
            if identifier.get("type") == "ISBN_13":
                isbn = identifier.get("identifier")
                break
        if not isbn and volume.get("industryIdentifiers"):
            isbn = volume["industryIdentifiers"][0].get("identifier")

        normalized.append({
            "title": volume.get("title", "Unknown Title"),
            "author": ", ".join(volume.get("authors", [])) if volume.get("authors") else "Unknown Author",

            # UPDATED FIELD
            "year_category": year_category,

            "description": volume.get("description", ""),
            "isbn": isbn,
            "thumbnail_url": volume.get("imageLinks", {}).get("thumbnail"),
            "source": "google_books",
        })

    return normalized


# ============================================================
# CACHE WRAPPERS
# ============================================================
def get_cached_results(query_hash):
    result = CACHE.get(query_hash)
    return result


def set_cache_results(query_hash, results):
    CACHE[query_hash] = {
        "timestamp": datetime.now(),
        "data": results
    }
