"""
scripts/fetch_live_books.py
---------------------------
Purpose:
    Fetch REAL books from Google Books API and insert into SQLite DB
    using dynamic query expansion (Option B), expanded genres (Option 3),
    and improved fallback logic for weak genres.

Author: Suganya P
Updated: 2025-12-09

CHANGES:
    ✓ Corrected language mapping so DB stores: English / Tamil
    ✓ Preserved year_category mapping
    ✓ Preserved expanded genres + dynamic queries
    ✓ No other working logic was changed
"""

import os
import sys
import time
import requests
import math

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db_utils import init_db, insert_book
from app.data_loader import map_year_to_category


# =====================================================
# CONFIG
# =====================================================

GOOGLE_API_BASE = "https://www.googleapis.com/books/v1/volumes"
MAX_RESULTS_PER_CALL = 40
TARGET_PER_GENRE = 50
MAX_PAGES_PER_QUERY = 4
REQUEST_SLEEP = 0.12
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# IMPORTANT FIX (2025-12-09)
LANGUAGES = [
    ("en", "English"),
    ("ta", "Tamil"),
]

# Expanded Genre List
GENRES = [
    "Adventure",
    "Fantasy",
    "Educational",
    "Animals",
    "Mystery",
    "Fairy tales",
    "Science",
    "History",
    "Bedtime",
    "Moral stories",
    "Story Books",
    "Comics",
    "Early Learning",
]

# Age group midpoint mapping
GENRE_AGE_MAP = {
    "Adventure": (7, 12),
    "Fantasy": (7, 12),
    "Educational": (5, 12),
    "Animals": (3, 8),
    "Mystery": (8, 14),
    "Fairy tales": (3, 6),
    "Science": (6, 14),
    "History": (7, 14),
    "Bedtime": (3, 6),
    "Moral stories": (4, 10),
    "Story Books": (4, 10),
    "Comics": (7, 14),
    "Early Learning": (3, 6),
}

# Dynamic query patterns
QUERY_PATTERNS = [
    "{genre}",
    "{genre} children",
    "{genre} kids",
    "subject:{genre}",
    "subject:{genre} children",
    "{genre} books",
    "{genre} story",
    "{genre} stories",
]


# =====================================================
# HELPERS
# =====================================================

def expand_queries_for_genre(genre):
    """Generate query variations."""
    base = genre.lower().strip()
    return [pattern.format(genre=base) for pattern in QUERY_PATTERNS]


def build_query_params(query_string, language_code, start_index):
    """Build final API parameters."""
    params = {
        "q": query_string,
        "maxResults": MAX_RESULTS_PER_CALL,
        "startIndex": start_index,
    }
    if language_code:
        params["langRestrict"] = language_code
    if GOOGLE_API_KEY:
        params["key"] = GOOGLE_API_KEY
    return params


def extract_isbn(volume_info, fallback_id):
    """Extract ISBN13 → ISBN10 → fallback."""
    for ident in volume_info.get("industryIdentifiers", []) or []:
        if ident.get("type") == "ISBN_13":
            return ident["identifier"]
    for ident in volume_info.get("industryIdentifiers", []) or []:
        if ident.get("type") == "ISBN_10":
            return ident["identifier"]
    return f"GB-{fallback_id}"


def assign_age_group(genre):
    """Midpoint age based on genre."""
    low, high = GENRE_AGE_MAP.get(genre, (6, 10))
    mid = int((low + high) // 2)
    return max(3, min(14, mid))


def normalize_item(item, genre, lang_code):
    """
    Convert Google Books → DB schema.
    Only required fields updated.
    """
    volume = item.get("volumeInfo", {})
    gid = item.get("id", "NOID")
    isbn = extract_isbn(volume, gid)

    # Raw year extraction
    pub_date = volume.get("publishedDate", "")
    raw_year = pub_date.split("-")[0] if pub_date else None
    year_category = map_year_to_category(raw_year)

    # FIXED LANGUAGE LABEL (2025-12-09)
    language_label = "English" if lang_code == "en" else "Tamil"

    return {
        "title": volume.get("title", "Unknown Title"),
        "author": ", ".join(volume.get("authors", [])) if volume.get("authors") else "Unknown",
        "description": volume.get("description", "") or "",
        "isbn": isbn,
        "genre": genre,
        "language": language_label,        # FIXED
        "age_group": assign_age_group(genre),
        "year_category": year_category,
        "thumbnail_url": (volume.get("imageLinks") or {}).get("thumbnail"),
        "source": "google_books",
    }


# =====================================================
# MAIN FETCH PIPELINE
# =====================================================

def fetch_many_and_insert():
    print("\n=======================================")
    print("        LIVE BOOKS FETCH STARTED        ")
    print("=======================================\n")

    init_db()

    inserted_total = 0
    isbn_seen = set()
    per_genre_counts = {g: 0 for g in GENRES}

    for genre in GENRES:
        print(f"\n========== GENRE: {genre} ==========")
        query_list = expand_queries_for_genre(genre)

        for query_string in query_list:
            if per_genre_counts[genre] >= TARGET_PER_GENRE:
                break

            for lang_code, lang_label in LANGUAGES:
                if per_genre_counts[genre] >= TARGET_PER_GENRE:
                    break

                print(f"\n[QUERY] {query_string} | {lang_label}")

                for page in range(MAX_PAGES_PER_QUERY):
                    start_index = page * MAX_RESULTS_PER_CALL
                    params = build_query_params(query_string, lang_code, start_index)

                    try:
                        resp = requests.get(GOOGLE_API_BASE, params=params, timeout=12)
                    except Exception as e:
                        print(f"[ERROR] Request failed: {e}")
                        break

                    if resp.status_code != 200:
                        print(f"[WARN] {resp.status_code} — skipping")
                        break

                    items = resp.json().get("items", []) or []
                    if not items:
                        break

                    for it in items:
                        record = normalize_item(it, genre, lang_code)
                        key = record["isbn"]

                        if key in isbn_seen:
                            continue

                        if insert_book(record):
                            isbn_seen.add(key)
                            per_genre_counts[genre] += 1
                            inserted_total += 1

                            print(f"[INSERT] {record['title']} | {lang_label} | ISBN={record['isbn']}")

                            if per_genre_counts[genre] >= TARGET_PER_GENRE:
                                break

                    time.sleep(REQUEST_SLEEP)

        print(f"[SUMMARY] {genre}: {per_genre_counts[genre]} inserted")

    print("\n=======================================")
    print("             FETCH COMPLETE             ")
    print("=======================================")
    print(f"Total inserted: {inserted_total}\n")
    for g in GENRES:
        print(f"- {g}: {per_genre_counts[g]}")
    print("=======================================\n")


# =====================================================
# CLI
# =====================================================

if __name__ == "__main__":
    fetch_many_and_insert()
