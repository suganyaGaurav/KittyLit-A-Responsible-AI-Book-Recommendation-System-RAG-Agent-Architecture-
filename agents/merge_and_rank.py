"""
merge_and_rank.py
-----------------
Functions to merge results from multiple data sources and rank them.
Includes potential hooks for database updates related to ranking or analytics.

Author: **Suganya P**
Date: 2025-08-12
"""

import logging
from app.db_utils import update_book_popularity  # DB helper for updating popularity

# Configure logger for this module
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s][merge_and_rank] %(message)s')
logger = logging.getLogger(__name__)


def merge_results(live_data, rag_data):
    """
    Merge live API data and RAG retrieval results, removing duplicates by book title.

    Args:
        live_data (list[dict]): List of book dicts from live API.
        rag_data (list[dict]): List of book dicts from RAG (Retrieval Augmented Generation) system.

    Returns:
        list[dict]: Combined list of books without duplicates.
    """
    # Combine both live API and RAG results into a single list
    combined = live_data + rag_data
    
    # Dictionary to hold unique books keyed by normalized title
    unique = {}

    # Iterate over all books in combined list
    for item in combined:
        # Normalize title to lowercase and strip whitespace for consistency
        title_key = item['title'].strip().lower()

        # If book title not seen before OR current item has higher popularity,
        # update the dictionary with this book
        if title_key not in unique or item.get('popularity', 0) > unique[title_key].get('popularity', 0):
            unique[title_key] = item

    # Log how many unique books remain after merging duplicates
    logger.debug(f"Merged results count: {len(unique)} unique books after removing duplicates.")

    # Return the list of unique book dictionaries
    return list(unique.values())


def rank_results(results):
    """
    Rank books by a relevance or popularity score.
    Also update the database with the popularity count for analytics purposes.

    Args:
        results (list[dict]): List of book dictionaries to be ranked.

    Returns:
        list[dict]: Sorted list of books by descending popularity or relevance.
    """
    # Sort the books by 'popularity' key in descending order; default to 0 if missing
    ranked = sorted(results, key=lambda x: x.get('popularity', 0), reverse=True)
    
    # Log the total number of books being ranked
    logger.debug(f"Ranking {len(ranked)} books by popularity.")

    # Iterate through ranked books to update popularity count in DB
    for book in ranked:
        # Only proceed if book has an ISBN and a popularity metric
        if 'isbn' in book and book.get('popularity'):
            try:
                # Update the popularity count for the book in the database
                update_book_popularity(book['isbn'], book['popularity'])
                # Log success of DB update for this book
                logger.debug(f"Updated popularity for ISBN {book['isbn']} by {book['popularity']}.")
            except Exception as e:
                # Log a warning if DB update fails, but continue processing other books
                logger.warning(f"Failed to update popularity for ISBN {book['isbn']}: {e}")

    # Return the final ranked list of books
    return ranked
