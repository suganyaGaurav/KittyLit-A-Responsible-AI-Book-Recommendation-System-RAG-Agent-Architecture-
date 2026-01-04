# scripts/

## Purpose

The `scripts` folder contains **operational and maintenance scripts** used to prepare, refresh, and support the KittyLit system outside the request/response lifecycle.

These scripts are **not part of the live application runtime**.  
They are executed manually or on a schedule to:

- preload databases
- warm caches
- fetch live external data
- refresh system state safely and deterministically

All scripts assume the application code (`app/`) is already present and correctly configured.

---

## Design Principles

- Scripts are **explicit and one-directional**
- No script contains UI logic
- No script runs automatically on app startup
- Data mutations are intentional and logged
- Schema changes are handled centrally (e.g., `year_category`)

Scripts may be slow, verbose, and conservative by design.

---

## Files Overview

### `fetch_live_books.py`

Purpose:
- Fetch **real books** from Google Books API
- Normalize results to KittyLit’s DB schema
- Insert validated records into the SQLite database

Key characteristics:
- Dynamic query expansion per genre
- Language normalization (English / Tamil)
- Genre → age group mapping
- ISBN extraction with safe fallbacks
- Strict quota pacing and defensive API usage

This script is intended for **controlled dataset expansion**, not real-time serving.

---

### `preload_db.py`

Purpose:
- Preload the SQLite database with a **clean baseline dataset** before running the application

What it does:
- Loads the books dataset JSON
- Normalizes all required DB fields
- Converts numeric publication year → `year_category`
- Generates synthetic ISBNs if missing
- Inserts records using `db_utils.insert_book()`

This script should be run **once per environment** (or when resetting data).

---

### `preload_cache.py`

Purpose:
- Warm the cache with books already present in the database

What it does:
- Initializes the unified cache layer
- Reads all books from the DB
- Stores them in cache using ISBN as key
- Provides visibility into cache coverage

This script improves **first-request latency** and avoids cold starts.

---

### `refresh_weekly.py`

Purpose:
- Perform **periodic system maintenance**

What it does:
- Simulates fetching updated books from a live API
- Normalizes incoming records to current DB schema
- Inserts new books or updates existing ones
- Refreshes cache entries from the updated DB state

This script represents the **maintenance lifecycle**, not production automation.

---

## What This Folder Does NOT Do

- No Flask app startup
- No HTTP routing
- No recommendation logic
- No RAG indexing or embeddings
- No autonomous scheduling

All scripts must be invoked intentionally.

---

## When These Scripts Are Used

- Local development setup
- Demo environment preparation
- Controlled data refresh
- Pre-deployment validation

Final data layout and scheduling strategy are defined **during deployment**, not here.
