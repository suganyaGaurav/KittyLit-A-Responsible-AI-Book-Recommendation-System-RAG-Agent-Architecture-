"""
app.utils.py
------------
Helpers: correlation id middleware, deterministic query hashing, response shaping.

Functions:
    - generate_correlation_id(): creates UUID for tracking
    - attach_correlation_id(app): middleware to inject CID into flask.g
    - build_query_hash(params): creates deterministic hash for cache + orchestrator
    - build_response(items, meta): shapes final response with safe defaults

Author: **Suganya P**
Updated: 2025-12-09
CHANGE:
    - Replaced 'year' with 'year_category' in build_query_hash
"""

import hashlib
import uuid
import logging
from flask import g, request

logger = logging.getLogger("kittylit.utils")


# ============================================================
# CORRELATION ID MIDDLEWARE
# ============================================================
def generate_correlation_id():
    return str(uuid.uuid4())


def attach_correlation_id(app):
    """
    Middleware to attach X-Correlation-Id to request context (flask.g).
    """
    @app.before_request
    def _attach_cid():
        cid = request.headers.get("X-Correlation-Id") or generate_correlation_id()
        g.correlation_id = cid
        request.correlation_id = cid


# ============================================================
# QUERY HASH BUILDER (UPDATED)
# ============================================================
def build_query_hash(params: dict) -> str:
    """
    Create deterministic string from a fixed set of fields then hash it.

    UPDATED 2025-12-09:
        - Replaced 'year' with 'year_category'
        - Ensures cache keys stay consistent with new filtering system
    """
    keys = ["age", "genre", "language", "year_category", "title"]

    normalized = {k: str(params.get(k, "")).strip().lower() for k in keys}
    canonical = "|".join(f"{k}={normalized[k]}" for k in keys)

    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    logger.debug("build_query_hash: canonical=%s hash=%s", canonical, h)
    return h


# ============================================================
# RESPONSE SHAPER
# ============================================================
def build_response(items, meta: dict):
    """
    Ensure the response meta contains required fields and return final payload.
    """
    meta = dict(meta or {})
    meta.setdefault("source_tried", [])
    meta.setdefault("source_used", None)
    meta.setdefault("latencies_ms", {})
    meta.setdefault("counts", {})
    return {"items": items or [], "meta": meta}
