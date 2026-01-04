"""
scripts/refresh_weekly.py
-------------------------
Purpose:
    Weekly maintenance script for refreshing DB + Cache.
    Updated to support new `year_category` schema.

Author: **Suganya P**
Updated: 2025-12-09
"""

# ===========================================
# Imports
# ===========================================
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db_utils import insert_book, update_book, query_books
from app import cache as app_cache
from app.data_loader import map_year_to_category   # NEW


# ===========================================
# 1. Mock LiveAPI fetch (Replace in Phase 2)
# ===========================================
def fetch_from_live_api():
    """
    Simulate a real external book API call.
    """
    print("[LIVE-API] Fetching latest book updates...")

    return [
        {
            "title": "New Adventures in the Sky",
            "author": "Ammu K",
            "publication_year": 2024,
            "description": "A fresh tale of courage.",
            "isbn": "LIVE-2024-001",
            "thumbnail_url": "",
        },
        {
            "title": "Mystery of the Whispering Woods",
            "author": "Sugan K",
            "publication_year": 2023,
            "description": "A spooky yet fun mystery.",
            "isbn": "LIVE-2023-007",
            "thumbnail_url": "",
        }
    ]


# ===========================================
# Normalize book input for DB schema
# ===========================================
def normalize(book):
    """
    Convert mock API → DB schema:
        - Converts year → year_category
        - Adds genre/language/age_group (None for now)
    """

    raw_year = book.get("publication_year")
    year_category = map_year_to_category(raw_year)

    return {
        "title": book.get("title", "Unknown"),
        "author": book.get("author", "Unknown"),
        "description": book.get("description", ""),
        "isbn": book.get("isbn", ""),
        "thumbnail_url": book.get("thumbnail_url", ""),
        "source": "live_api",

        # NEW required fields
        "genre": None,
        "language": None,
        "age_group": None,
        "year_category": year_category,
    }


# ===========================================
# 2. Insert/update DB records
# ===========================================
def refresh_database(new_books):
    inserted = 0
    updated = 0

    print("[STEP] Refreshing SQLite DB with new LiveAPI data...")

    for raw in new_books:
        book = normalize(raw)

        isbn = book["isbn"]
        if not isbn:
            print(f"[WARN] Skipping book with no ISBN: {book['title']}")
            continue

        if insert_book(book):
            print(f"[DB-INSERT] Added new book: {book['title']} (ISBN={isbn})")
            inserted += 1
        else:
            # Update existing book
            changes = {
                "title": book["title"],
                "author": book["author"],
                "description": book["description"],
                "year_category": book["year_category"],
            }
            update_book(isbn, changes)
            print(f"[DB-UPDATE] Updated book: {book['title']} (ISBN={isbn})")
            updated += 1

    return inserted, updated


# ===========================================
# 3. Refresh cache
# ===========================================
def refresh_cache():
    print("[STEP] Refreshing cache from DB…")

    client = app_cache.get_cache_client()
    all_books = query_books()

    cached = 0
    for b in all_books:
        key = f"book:{b['isbn']}"
        try:
            client.set(key, dict(b))
            cached += 1
        except Exception as e:
            print(f"[ERROR] Cache write failed for {key}: {e}")

    return cached


# ===========================================
# MAIN PIPELINE
# ===========================================
def weekly_refresh():
    print("===========================================")
    print(" 🔄 WEEKLY REFRESH PIPELINE STARTED ")
    print("===========================================")

    new_books = fetch_from_live_api()
    inserted, updated = refresh_database(new_books)
    cached = refresh_cache()

    print("\n--------------- SUMMARY ----------------")
    print(f"[NEW BOOKS INSERTED]   {inserted}")
    print(f"[BOOKS UPDATED]        {updated}")
    print(f"[CACHE REFRESHED]      {cached} entries")
    print("----------------------------------------")
    print("✔ WEEKLY REFRESH COMPLETE")
    print("----------------------------------------")


if __name__ == "__main__":
    weekly_refresh()
