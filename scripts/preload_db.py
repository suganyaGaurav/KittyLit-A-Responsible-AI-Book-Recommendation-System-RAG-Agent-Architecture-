"""
scripts/preload_db.py
---------------------
Purpose:
    Preload the SQLite DB with a clean initial dataset BEFORE running the app.

What it does:
    ✓ Loads books dataset
    ✓ Normalizes fields for DB schema (genre/language/age/year_category)
    ✓ Creates synthetic ISBN if missing
    ✓ Inserts via db_utils.insert_book()

Author: **Suganya P**
Updated: 2025-12-09
CHANGE:
    - Migrated from numeric 'year' → 'year_category'
    - Added missing fields: genre, language, age_group
"""

# =====================================================
# 1. IMPORTS
# =====================================================
import json
import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db_utils import init_db, insert_book
from app.data_loader import map_year_to_category    # NEW


# =====================================================
# 2. CONSTANTS
# =====================================================
DATASET_PATH = "data/books_dataset.json"


# =====================================================
# 3. LOAD JSON DATASET
# =====================================================
def load_dataset():
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset not found at: {DATASET_PATH}")
        return []

    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            books = json.load(f)
            print(f"[INFO] Loaded {len(books)} books from dataset.")
            return books
    except Exception as e:
        print(f"[ERROR] Failed to read dataset: {e}")
        return []


# =====================================================
# 4. NORMALIZE BOOK FIELDS
# =====================================================
def normalize_book(raw_book):
    """
    Convert dataset fields into DB schema format.
    Adds:
        - year_category (mapped from publication_year)
        - synthetic ISBN if missing
        - genre, language, age_group
    """

    isbn_value = raw_book.get("isbn")
    if not isbn_value or str(isbn_value).strip() == "":
        isbn_value = "SYNTH-" + uuid.uuid4().hex[:12]

    # ------- NEW: Convert numeric year → category -------
    raw_year = raw_book.get("publication_year")
    year_category = map_year_to_category(raw_year)

    return {
        "title": raw_book.get("title", "Unknown Title"),
        "author": raw_book.get("author", "Unknown"),
        "description": raw_book.get("description", "No description available"),

        # DB-required fields
        "isbn": isbn_value,
        "genre": raw_book.get("genre"),
        "language": raw_book.get("language"),
        "age_group": raw_book.get("age") or raw_book.get("age_group"),
        "year_category": year_category,

        # Optional UI extras
        "thumbnail_url": raw_book.get("thumbnail_url", ""),
        "source": "dataset"
    }


# =====================================================
# 5. MAIN PRELOAD LOGIC
# =====================================================
def preload_database():
    print("\n[STEP] Initializing database…")
    init_db()

    books = load_dataset()
    if not books:
        print("[ERROR] No data found. Preload aborted.")
        return

    print("[STEP] Inserting books into DB…")
    inserted_count = 0

    for raw in books:
        formatted = normalize_book(raw)

        if insert_book(formatted):
            inserted_count += 1
            print(f"[OK] Inserted: {formatted['title']}  (ISBN={formatted['isbn']})")
        else:
            print(f"[SKIP] Duplicate / Failed: {formatted['title']}")

    print("\n-------------------------------------------")
    print("[SUCCESS] Preload complete.")
    print(f"Inserted: {inserted_count} / {len(books)} records")
    print("-------------------------------------------\n")


# =====================================================
# 6. ENTRY POINT
# =====================================================
if __name__ == "__main__":
    preload_database()
