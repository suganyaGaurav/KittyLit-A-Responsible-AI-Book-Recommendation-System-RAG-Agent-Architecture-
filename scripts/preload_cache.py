"""
scripts/preload_cache.py
------------------------
Warm up the cache with DB books.
Uses the NEW unified cache layer (set_cached / get_cached).

Author: Ammu
"""

import os
import sys

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db_utils import query_books
from app.cache import init_cache_client, set_cached


# ============================
# MAIN CACHE PRELOAD
# ============================
def preload_cache():
    print("[STEP] Initializing cache layer…")
    init_cache_client()

    print("[STEP] Loading books from DB…")
    books = query_books()

    if not books:
        print("[ERROR] No books found in DB. Nothing to cache.")
        return

    print(f"[INFO] Found {len(books)} books in DB.")
    print("[STEP] Caching books…")

    cached = 0

    for book in books:
        isbn = book.get("isbn")

        if not isbn:
            print(f"[WARN] Skipping book without ISBN: {book.get('title')}")
            continue

        try:
            # NEW API
            set_cached(isbn, book)
            cached += 1
        except Exception as e:
            print(f"[ERROR] Failed caching ISBN={isbn}: {e}")

    print("-------------------------------------------")
    print(f"[SUCCESS] Cache warmup complete.")
    print(f"Cached books: {cached} / {len(books)}")
    print("-------------------------------------------")


if __name__ == "__main__":
    preload_cache()
