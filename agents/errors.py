"""
errors.py
---------
Centralized error classes for the Agentic AI system.

This module defines custom exceptions to keep error handling clean and consistent
across live data fetching, RAG pipeline processing, and decision logic.

Author: **Suganya P**
Date: 2025-08-12
"""

# ==============================
# Custom Exception Classes
# ==============================

class LiveDataFetchError(Exception):
    """
    Exception raised when fetching live data (e.g., from Google Books API) fails.

    This helps differentiate network or API-related errors from other failures.
    """
    pass  # No additional functionality needed; serves as a named exception


class RAGProcessingError(Exception):
    """
    Exception raised during errors in the Retrieval-Augmented Generation (RAG) pipeline.

    Useful for catching and handling issues specific to document retrieval and
    generation steps separately from live API or general errors.
    """
    pass


class DecisionRuleError(Exception):
    """
    Exception raised when the decision-making logic for choosing data source fails.

    Could be due to invalid inputs or unexpected states in decision_rules.py.
    """
    pass
