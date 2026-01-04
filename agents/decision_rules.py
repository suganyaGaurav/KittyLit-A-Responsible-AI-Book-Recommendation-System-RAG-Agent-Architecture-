"""
decision_rules.py
-----------------
Decision logic to select data source: cache, live API, or RAG.

Author: ** Suganya P**
Date: 2025-08-12
"""

# Import datetime and timedelta classes for date/time calculations
from datetime import datetime, timedelta

# Import helper functions to get cached results and daily API call count
from .agent_tools import get_cached_results, get_daily_api_call_count

# Constants for cache expiry and daily API limits
CACHE_EXPIRY_DAYS = 5                # Number of days before cached data is considered stale
DAILY_API_CALL_LIMIT = 600           # Maximum allowed live API calls per day


def should_use_cache(query_hash):
    """
    Determine if cached results should be used.

    Conditions:
    - Cache exists for the query.
    - Cache is not older than CACHE_EXPIRY_DAYS.

    Args:
        query_hash (str): Unique key identifying the query cache.

    Returns:
        bool: True if valid cache is available and fresh; False otherwise.
    """
    # Fetch cached results from cache using query_hash key
    cached = get_cached_results(query_hash)

    # If no cached data found, return False (cannot use cache)
    if not cached:
        return False

    # Calculate age of cached data by subtracting cached timestamp from current time
    age = datetime.now() - cached["timestamp"]

    # Return True only if age is less than CACHE_EXPIRY_DAYS; else False
    return age < timedelta(days=CACHE_EXPIRY_DAYS)


def decide_data_source(query_hash, query_params):
    """
    Decide which data source to use for fetching book data.

    Priority order:
    1. Use cache if fresh and available.
    2. Use live API if daily quota not exceeded.
    3. Fallback to RAG (local retrieval) if no cache and API quota exceeded.

    Args:
        query_hash (str): Unique cache key for the query.
        query_params (dict): Parameters for the query like title, genre, year, language.

    Returns:
        str: One of 'cache', 'live', or 'rag' indicating which source to use.
    """

    # Check if cached data is available and still fresh
    if should_use_cache(query_hash):
        return "cache"  # Use cached results if valid

    # Get how many API calls have been made today
    api_calls_today = get_daily_api_call_count()

    # If API calls today are less than daily allowed limit, use live API
    if api_calls_today < DAILY_API_CALL_LIMIT:
        return "live"  # Allowed to make live API call

    # If cache is stale or missing, and API quota exceeded, fallback to RAG retrieval
    return "rag"
