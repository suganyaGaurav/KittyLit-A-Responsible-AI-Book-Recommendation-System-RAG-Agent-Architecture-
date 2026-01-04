"""
app/services.py
---------------
Form-based search pipeline:
 → Normalizes UI filters
 → Generates deterministic query hash
 → Calls Orchestrator
 → Applies post-filtering (genre + SOFT year_category)
 → Performs final data enrichment
 → Returns curated items + metadata

Author: Suganya P
Updated: 2025-12-09
"""

import logging
from flask import g

from agents.orchestrator import decide_and_fetch
from .utils import build_query_hash

logger = logging.getLogger("kittylit.services")


# ============================================================
# =                PARAM NORMALIZATION                       =
# ============================================================
def normalize_language(raw_value):
    """
    UI sends: English / Tamil
    System stores: en / ta
    """
    if not raw_value:
        return None

    val = raw_value.strip().lower()

    if val == "english":
        return "en"
    if val == "tamil":
        return "ta"

    # fallback → return original
    return raw_value


def normalize_filters(raw: dict):
    """Convert UI filters into orchestrator-ready dict."""
    return {
        "age_group": raw.get("age"),                 # unchanged
        "genre": raw.get("genre"),
        "language": normalize_language(raw.get("language")),
        "year_category": raw.get("year_category"),
    }


# ============================================================
# =                POST-FILTERING HELPERS                   =
# ============================================================
def match_genre(book, requested_genre):
    if not requested_genre:
        return True

    book_genre = str(book.get("genre", "")).strip().lower()
    return book_genre == requested_genre.strip().lower()


def soft_match_year_category(book, selected_year_cat):
    """
    SOFT YEAR MATCHING (Option B)
    Accepts mismatches but marks them internally.
    Never return 0 results unless no books exist at all.
    """
    if not selected_year_cat:
        return True

    book_cat = book.get("year_category")

    if not book_cat:
        return True  # unknown accepted

    if book_cat == selected_year_cat:
        return True  # perfect match

    book["_soft_year_mismatch"] = True
    return True


# ============================================================
# =                MAIN SEARCH SERVICE                        =
# ============================================================
def search_service(raw_params: dict):

    correlation_id = getattr(g, "correlation_id", None)

    filters = normalize_filters(raw_params)
    qh = build_query_hash(filters)

    logger.info(f"[SERVICE] Filters cid={correlation_id}, qh={qh[:8]} → {filters}")

    try:
        # ----------------------------------------------------
        # ORCHESTRATOR CALL
        # ----------------------------------------------------
        books, metadata = decide_and_fetch(
            qh=qh,
            qp=filters,
            ctx={"correlation_id": correlation_id},
        )

        metadata["correlation_id"] = correlation_id

        logger.info(
            "[SERVICE] Orchestrator returned %d raw books (cid=%s)",
            len(books), correlation_id
        )

        # ============================================================
        # FINAL FILTERING + ENRICHMENT
        # ============================================================
        final_items = []

        selected_genre = filters.get("genre")
        selected_language = filters.get("language")
        selected_year_cat = filters.get("year_category")

        for book in books:

            # ---- FILTER 1: GENRE ----
            if selected_genre and not match_genre(book, selected_genre):
                continue

            # ---- FILTER 2: YEAR CATEGORY (SOFT) ----
            if not soft_match_year_category(book, selected_year_cat):
                continue

            # ---- ENRICH MISSING GENRE ----
            if not book.get("genre") and selected_genre:
                book["genre"] = selected_genre

            # ---- ENRICH MISSING LANGUAGE ----
            if not book.get("language") and selected_language:
                book["language"] = selected_language

            final_items.append(book)

        logger.info(
            "[SERVICE] Final filtered → %d books",
            len(final_items)
        )

        return {"items": final_items, "metadata": metadata}

    except Exception as e:
        logger.exception("[SERVICE] Orchestrator failed: %s", e)

        return {
            "items": [],
            "metadata": {
                "correlation_id": correlation_id,
                "error": "orchestrator_failed",
                "detail": str(e),
            },
        }
