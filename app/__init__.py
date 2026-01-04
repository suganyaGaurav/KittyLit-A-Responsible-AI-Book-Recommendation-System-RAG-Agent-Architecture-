"""
app.__init__.py
---------------
Flask application factory for KittyLit.
Builds the app, registers routes, attaches middleware,
initializes cache + SQLite DB, and loads error handlers.

This file stays clean — no business logic here.
Author : **Suganya P**
"""

# ============================================================
# =                      IMPORTS                             =
# ============================================================

import logging
from flask import Flask

# Internal modules
from .routes import register_routes
from .errors import register_error_handlers
from .utils import attach_correlation_id
from . import cache as app_cache
from . import db_utils


# ============================================================
# =                     APP FACTORY                           =
# ============================================================

def create_app():
    """
    Build and configure Flask app instance.
    Clean, minimal, and production friendly.
    """
    # ----------------------------------------
    # Flask Init (with explicit template/static paths)
    # ----------------------------------------
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    # ----------------------------------------
    # Logging Setup
    # ----------------------------------------
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("kittylit.app")
    logger.info("create_app: starting application")

    # ----------------------------------------
    # Middleware
    # (Adds a correlation-id to every request)
    # ----------------------------------------
    attach_correlation_id(app)

    # ----------------------------------------
    # Register Routes
    # ----------------------------------------
    register_routes(app)

    # ----------------------------------------
    # Error Handlers
    # ----------------------------------------
    register_error_handlers(app)

    # ----------------------------------------
    # Initialize Optional Clients
    # Cache + SQLite DB
    # ----------------------------------------
    try:
        app_cache.init_cache_client()   # Prepares Redis / in-memory fallback
        db_utils.init_db()              # Creates SQLite tables if missing
        logger.info("create_app: cache + DB initialized successfully")
    except Exception as e:
        logger.exception(
            f"create_app: client initialization failed (running in degraded mode): {e}"
        )

    # ----------------------------------------
    # Return Fully Configured App
    # ----------------------------------------
    return app
