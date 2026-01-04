"""
app/cache.py
------------
Unified cache layer for KittyLit.

✓ Uses Redis if available
✓ Automatically falls back to in-memory TTL cache
✓ Provides stable public API for:
    - set_cached()
    - get_cached()
    - delete_cached()
    - get_cache_client()
✓ Used by:
    - preload_cache.py
    - agents/orchestrator
    - search service
    - future chatbot RAG layer

Author: **Suganya P**
Updated: 2025-12-09
Note:
    - No changes required for year → year_category migration.
    - Cache stores only hashed payloads, not field-based lookups.
"""

import json
import logging
import time
from datetime import datetime
from app.config import REDIS_URL, CACHE_TTL_SECONDS


logger = logging.getLogger("kittylit.cache")

# --------------------------------------------------------------------
# REDIS INITIALIZATION
# --------------------------------------------------------------------
try:
    import redis
    _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    _redis_available = True
except Exception:
    _redis_client = None
    _redis_available = False
    logger.info("cache: Redis not available, using in-memory cache.")


# --------------------------------------------------------------------
# IN-MEMORY FALLBACK STORE
# key → (payload_dict, expiry_epoch)
# --------------------------------------------------------------------
_mem_store = {}



# --------------------------------------------------------------------
# STARTUP INITIALIZER (called once from app factory)
# --------------------------------------------------------------------
def init_cache_client():
    """
    Verifies Redis is reachable; falls back to memory if not.
    """
    global _redis_available

    if not _redis_client:
        logger.info("cache.init_cache_client: no Redis client detected.")
        return

    try:
        _redis_client.ping()
        _redis_available = True
        logger.info("cache.init_cache_client: Redis connection OK.")
    except Exception:
        _redis_available = False
        logger.exception("cache.init_cache_client: Redis ping failed → fallback to memory.")



# --------------------------------------------------------------------
# SCRIPT/AGENT ACCESSOR
# --------------------------------------------------------------------
def get_cache_client():
    """
    Returns the underlying storage client.
    - Redis client (if available)
    - In-memory dict (fallback)

    Note:
    Scripts should STILL use set_cached/get_cached
    and NOT use the raw client directly.
    """
    return _redis_client if _redis_available else _mem_store



# --------------------------------------------------------------------
# INTERNAL UTILITY
# --------------------------------------------------------------------
def _now_iso():
    return datetime.utcnow().isoformat()



# --------------------------------------------------------------------
# PUBLIC API: GET
# --------------------------------------------------------------------
def get_cached(query_hash: str):
    """
    Retrieve cached item using hash key.

    Returns:
        {
            "items": [...],
            "timestamp": "<ISO-UTC>"
        } 
    OR None if missing/expired.

    NOTE:
    - No change needed for year_category migration.
      Cache works off hashed key, not filter fields.
    """
    key = f"cache:{query_hash}"

    # ---- Redis mode ----
    if _redis_available:
        raw = _redis_client.get(key)
        if not raw:
            return None

        try:
            return json.loads(raw)
        except Exception:
            logger.exception("cache.get_cached: failed to decode redis payload.")
            return None

    # ---- In-memory mode ----
    entry = _mem_store.get(key)
    if not entry:
        return None

    payload, expiry = entry
    if time.time() > expiry:
        del _mem_store[key]
        return None

    return payload



# --------------------------------------------------------------------
# PUBLIC API: SET
# --------------------------------------------------------------------
def set_cached(query_hash: str, items, ttl_seconds: int = CACHE_TTL_SECONDS):
    """
    Store cached results in Redis or memory.

    No logic change for year_category migration.
    """
    key = f"cache:{query_hash}"
    payload = {
        "items": items,
        "timestamp": _now_iso()
    }

    # ---- Redis mode ----
    if _redis_available:
        _redis_client.setex(key, int(ttl_seconds), json.dumps(payload))
    else:
        _mem_store[key] = (payload, time.time() + int(ttl_seconds))

    logger.debug(
        "cache.set_cached: key=%s items=%s ttl=%s",
        query_hash[:12],
        len(items) if items else 0,
        ttl_seconds
    )



# --------------------------------------------------------------------
# PUBLIC API: DELETE
# --------------------------------------------------------------------
def delete_cached(query_hash: str):
    """
    Remove key from Redis or memory.
    """
    key = f"cache:{query_hash}"

    if _redis_available:
        _redis_client.delete(key)
    else:
        _mem_store.pop(key, None)

    logger.debug("cache.delete_cached: key=%s", query_hash[:12])
