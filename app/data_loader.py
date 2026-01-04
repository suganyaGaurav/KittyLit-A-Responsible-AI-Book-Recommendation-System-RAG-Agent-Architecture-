"""
app.data_loader.py
------------------
Load and normalize books dataset; produce dropdown values for UI.

Author: **Suganya P**
Updated: 2025-12-09
CHANGE:
    - Removed numeric 'years'
    - Added derived 'year_category' buckets:
        before_2000, 2000_2010, 2010_2020, 2020_present
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("kittylit.data_loader")

_CACHE = []


# ============================================================
# YEAR CATEGORY MAPPER (Core of the new logic)
# ============================================================
def map_year_to_category(pub_year):
    """
    Convert numeric publication year → year_category bucket.

    Returns:
        - "before_2000"
        - "2000_2010"
        - "2010_2020"
        - "2020_present"
        - None (if invalid)
    """
    if not pub_year:
        return None

    try:
        year = int(str(pub_year).split("-")[0])
    except Exception:
        return None

    if year < 2000:
        return "before_2000"
    elif 2000 <= year <= 2010:
        return "2000_2010"
    elif 2010 < year <= 2020:
        return "2010_2020"
    else:
        return "2020_present"



# ============================================================
# LOAD BOOK DATASET
# ============================================================
def load_books_dataset(path: str = "data/books_dataset.json"):
    """
    Load dataset once & cache in process memory.
    
    UPDATED 2025-12-09:
        - Normalizes year → year_category
        - Removes old numeric pub_year
    """
    global _CACHE
    if _CACHE:
        logger.debug("load_books_dataset: returning cached dataset (len=%s)", len(_CACHE))
        return _CACHE

    p = Path(path)
    if not p.exists():
        logger.warning("load_books_dataset: file not found: %s", path)
        _CACHE = []
        return _CACHE

    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            logger.warning("load_books_dataset: expected list at top-level")
            raw = []

        normalized = []
        for item in raw:

            # Extract raw pub_year
            raw_year = item.get("pub_year") or item.get("year")

            normalized.append({
                "title": item.get("title"),
                "authors": item.get("authors") or [],
                "isbn": item.get("isbn"),

                "language": item.get("language"),
                "genre": item.get("genre"),

                # Age normalization
                "age": item.get("age") or item.get("age_group"),

                # NEW FIELD: year_category
                "year_category": map_year_to_category(raw_year),

                "raw": item
            })

        _CACHE = normalized
        logger.info("load_books_dataset: loaded %s records from %s", len(_CACHE), path)

    except Exception as e:
        logger.exception("load_books_dataset: failed to load dataset: %s", e)
        _CACHE = []

    return _CACHE



# ============================================================
# DROPDOWN VALUES
# ============================================================
def get_dropdown_values(dataset=None):
    """
    Return deduped, sorted dropdown values.

    UPDATED 2025-12-09:
        - Removed old numeric years
        - Added year_category buckets
    """
    ds = dataset or load_books_dataset()

    genres = set()
    languages = set()
    ages = set()
    year_categories = set()

    for it in ds:
        if it.get("genre"):
            genres.add(str(it["genre"]).strip())

        if it.get("language"):
            languages.add(str(it["language"]).strip())

        if it.get("age"):
            ages.add(str(it["age"]).strip())

        if it.get("year_category"):
            year_categories.add(it["year_category"])

    return {
        "genres": sorted(genres),
        "languages": sorted(languages),
        "ages": sorted(ages),
        "year_categories": sorted(year_categories)
    }
