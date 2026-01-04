## Purpose

The `app` folder contains the **application wiring and service layer** for KittyLit.

This layer sits between:
- the **HTTP/UI layer** (Flask routes),
- the **agent orchestration layer** (`agents/`),
- and the **infrastructure components** (cache, database, configuration).

Its responsibility is to **initialize the application, normalize inputs, enforce governance checks, and delegate work** to the appropriate downstream components.  
No recommendation logic lives here — that is handled by the agent layer.

---

## Key Responsibilities

The `app` module is responsible for:

- Creating and configuring the Flask application
- Registering routes, middleware, and error handlers
- Managing cache and database initialization
- Normalizing UI inputs into system-ready filters
- Acting as a thin service layer between routes and agents
- Enforcing basic governance and safety checks
- Providing observability via correlation IDs and developer logs

---

## Files Overview

### `__init__.py`
Flask application factory.

    Responsibilities:
    - Create the Flask app instance
    - Attach middleware (correlation ID)
    - Register routes and error handlers
    - Initialize cache and database clients
    - Define template and static paths

This file contains **no business logic** and exists purely for clean application startup.

---

### `cache.py`
Unified cache abstraction for KittyLit.

    Responsibilities:
    - Use Redis when available
    - Automatically fall back to in-memory TTL cache
    - Provide a stable public API:
      - `get_cached`
      - `set_cached`
      - `delete_cached`
      - `get_cache_client`

Design principles:
- Infrastructure-agnostic
- Safe fallback behavior
- No field-level caching (hash-based only)

Used by agents, services, and preload scripts.

---

### `config.py`
Centralized, environment-driven configuration.

    Responsibilities:
    - Read configuration from environment variables
    - Define defaults for local/demo usage
    - Control feature flags, limits, and timeouts

Includes:
- Cache and API limits
- Database connection settings
- Feature toggles (live API, chatbot RAG)
- Logging configuration

No logic — configuration only.

---

### `data_loader.py`
Dataset loading and normalization utilities.

    Responsibilities:
    - Load the books dataset once per process
    - Normalize publication year into `year_category`
    - Produce dropdown values for UI filters

Key design choice:
- Replaced numeric years with **year_category buckets** for stability and consistency.

This file is shared by UI routes and downstream services.

---

### `db_utils.py`
SQLite database access layer.

    Responsibilities:
    - Initialize database schema on startup
    - Insert, query, update, and delete book records
    - Enforce strict, exact-match filtering
    - Track popularity and access metadata

Design principles:
- Explicit SQL
- No ORM magic
- Predictable, debuggable behavior

This is the **single source of truth** for DB interactions.

---

### `errors.py`
Global Flask error handlers.

    Responsibilities:
    - Catch unhandled exceptions
    - Mask internal details from users
    - Log full errors server-side
    - Push structured error events to developer logs
    - Preserve correlation IDs for tracing

Ensures failures are **safe, observable, and non-leaky**.

---

### `options.py`
Static UI constants and validation helpers.

    Responsibilities:
    - Define valid genres, languages, and age groups
    - Map raw dataset genres to standardized values
    - Fail fast if invalid mappings are introduced

This file keeps UI and dataset assumptions explicit.

---

### `routes.py`
HTTP routing layer for KittyLit.

    Responsibilities:
    - Define Flask routes for:
      - Home page
      - Health check
      - Form-based search
      - Dropdown values
      - Developer logs UI and API
    - Perform basic governance and safety checks
    - Delegate business logic to the service layer

This file is intentionally thin and contains no orchestration logic.

---

### `services.py`
Service layer between routes and agents.

    Responsibilities:
    - Normalize UI filters
    - Generate deterministic query hashes
    - Call the agent orchestrator
    - Apply post-filtering and soft matching
    - Enrich incomplete results
    - Return curated results with metadata

This layer ensures the UI never talks directly to agents.

---

### `utils.py`
Shared helper utilities.

    Responsibilities:
    - Generate and attach correlation IDs
    - Build deterministic query hashes
    - Shape final API responses safely

These utilities support observability, caching consistency, and traceability.

---

## What This Folder Does NOT Do

- No recommendation decision logic
- No ranking algorithms
- No RAG retrieval
- No autonomous behavior
- No model calls

All intelligence lives in the `agents/` and `rag_pipeline/` layers.

---

## Design Philosophy

- Thin layers with clear responsibilities
- Deterministic behavior over heuristics
- Governance and observability built-in
- Infrastructure flexibility without complexity

The `app` folder exists to **wire the system together cleanly and safely**.
