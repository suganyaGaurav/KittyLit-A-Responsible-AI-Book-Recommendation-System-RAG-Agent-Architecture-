"""
===========================================================
 app/db_utils.py
-----------------------------------------------------------
Handles all SQLite database operations for the KittyLit app.

Includes:
- DB connection helper
- Creating tables on startup
- Insert / Query / Update / Delete functions
- Popularity update
- Logging for traceability

Author: **Suganya P**
Updated: 2025-12-09 (Year → Year Category migration)
===========================================================
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime

# ------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s][db_utils] %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Database Path (SQLite)
# ------------------------------------------------------------
DB_PATH = 'data/kittylit_books.db'


# ============================================================
# 1. DB INITIALIZATION
# ============================================================
def init_db():
    """
    Create the 'books' table if it does not already exist.

    UPDATED 2025-12-09:
        - Removed publication_year
        - Added year_category
    """
    logger.debug("Initializing SQLite database...")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        -- Core information
        title TEXT NOT NULL,
        author TEXT,
        description TEXT,
        isbn TEXT UNIQUE,

        -- UI & Agent Filters
        genre TEXT,
        language TEXT,
        age_group INTEGER,

        -- UPDATED FIELD (2025-12-09)
        year_category TEXT,

        -- Extra Metadata
        thumbnail_url TEXT,
        source TEXT,
        popularity INTEGER DEFAULT 0,

        -- Operational Tracking
        cached_at TEXT,
        agent_notes TEXT,

        -- Governance Timestamps
        created_at TEXT,
        updated_at TEXT
    );
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        conn.close()

        logger.debug("Database initialized successfully.")

    except Exception as e:
        logger.error(f"DB initialization failed: {e}")
        raise


# ============================================================
# 2. CONNECTION HANDLER
# ============================================================
def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        logger.debug("DB connection opened.")
        return conn
    except Exception as e:
        logger.error(f"Error opening DB connection: {e}")
        raise


# ============================================================
# 3. INSERT BOOK
# ============================================================
def insert_book(book: Dict) -> bool:
    """Insert a book into the database using INSERT OR IGNORE."""

    query = '''
        INSERT OR IGNORE INTO books
        (title, author, description, isbn,
         genre, language, age_group, year_category,
         thumbnail_url, source, popularity,
         cached_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        now = datetime.utcnow().isoformat()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (
            book['title'],
            book.get('author'),
            book.get('description'),
            book['isbn'],

            book.get('genre'),
            book.get('language'),
            book.get('age_group'),
            book.get('year_category'),

            book.get('thumbnail_url'),
            book.get('source'),
            book.get('popularity', 0),

            now, now, now
        ))

        conn.commit()
        inserted = cursor.rowcount > 0
        conn.close()

        logger.debug(f"Inserted ISBN={book.get('isbn')} → {inserted}")
        return inserted

    except Exception as e:
        logger.error(f"Insert error ISBN={book.get('isbn')}: {e}")
        return False


# ============================================================
# 4. QUERY BOOKS (UPDATED — THIS IS THE ONLY CHANGE)
# ============================================================
def query_books(filter_by: Optional[Dict] = None) -> List[Dict]:
    """
    Fetch books using EXACT MATCH filtering.

    Replaced old LIKE '%value%' logic because it caused:
        - language mismatch (English ≠ en)
        - loose/inaccurate genre matching
        - wrong filtering on year_category
        - incorrect numeric filtering for age_group
    """

    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if filter_by:

        # GENRE — strict match
        if filter_by.get("genre"):
            query += " AND genre = ?"
            params.append(filter_by["genre"])

        # LANGUAGE — convert English→en, Tamil→ta
        if filter_by.get("language"):
            lang_raw = filter_by["language"].strip().lower()
            lang_map = {"english": "en", "tamil": "ta", "hindi": "hi"}
            lang_code = lang_map.get(lang_raw, lang_raw)
            query += " AND language = ?"
            params.append(lang_code)

        # AGE GROUP — numeric equality
        if filter_by.get("age_group"):
            try:
                age_val = int(filter_by["age_group"])
                query += " AND age_group = ?"
                params.append(age_val)
            except:
                pass

        # YEAR CATEGORY — exact string match
        if filter_by.get("year_category"):
            query += " AND year_category = ?"
            params.append(filter_by["year_category"])

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        books = [dict(r) for r in rows]
        logger.debug(f"Query filters={filter_by} → {len(books)} books")
        return books

    except Exception as e:
        logger.error(f"Query error {filter_by}: {e}")
        return []


# ============================================================
# 5. UPDATE BOOK
# ============================================================
def update_book(isbn: str, update_fields: Dict) -> bool:
    """Update fields for a book identified by ISBN."""

    if not update_fields:
        return False

    update_fields["updated_at"] = datetime.utcnow().isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
    params = list(update_fields.values()) + [isbn]

    query = f"UPDATE books SET {set_clause} WHERE isbn = ?"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    except Exception as e:
        logger.error(f"Update error ISBN={isbn}: {e}")
        return False


# ============================================================
# 6. DELETE BOOK
# ============================================================
def delete_book(isbn: str) -> bool:
    """Delete book from DB."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE isbn = ?", (isbn,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception as e:
        logger.error(f"Delete error ISBN={isbn}: {e}")
        return False


# ============================================================
# 7. UPDATE POPULARITY
# ============================================================
def update_book_popularity(isbn: str, increment: int):
    """Increment book popularity score."""
    query = """
        UPDATE books
        SET popularity = COALESCE(popularity, 0) + ?
        WHERE isbn = ?
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (increment, isbn))
        conn.commit()
        conn.close()

    except Exception as e:
        logger.error(f"Popularity update error ISBN={isbn}: {e}")
