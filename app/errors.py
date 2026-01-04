"""
app/errors.py
---------------
Centralized error handlers for KittyLit.

Purpose:
    - Catch unhandled exceptions
    - Mask internal details from users
    - Log full errors on server side
    - Support correlation_id for observability
    - Push developer logs for debugging

Author: **Suganya P**
"""

# ============================================================
# =                         IMPORTS                           =
# ============================================================

import logging
from flask import jsonify, request

# Developer logs (for /developer page)
from .gateways.developer_logs import push_log_event


# ============================================================
# =                           LOGGER                          =
# ============================================================

logger = logging.getLogger("kittylit.errors")


# ============================================================
# =                   REGISTER ERROR HANDLERS                =
# ============================================================

def register_error_handlers(app):
    """
    Attach global HTTP error handlers.
    Ensures:
        - No internal details leak to frontend
        - All issues logged server-side
        - Developer Logs capture error events
    """

    # --------------------------------------------------------
    # 500 – Internal Server Error
    # --------------------------------------------------------
    @app.errorhandler(500)
    def handle_500(err):
        """
        Triggered when an unhandled exception occurs.
        Returns masked UI-safe JSON.
        """
        cid = getattr(request, "correlation_id", None)

        # Full server-side traceback
        logger.exception(f"[500] Unhandled error cid={cid}: {err}")

        # Developer Logs entry
        push_log_event("error_500", {"correlation_id": cid, "detail": str(err)})

        return jsonify({
            "error": "internal_server_error",
            "message": "Something went wrong on our side.",
            "correlation_id": cid
        }), 500

    # --------------------------------------------------------
    # 404 – Resource Not Found
    # --------------------------------------------------------
    @app.errorhandler(404)
    def handle_404(err):
        """
        Something was not found — path or endpoint.
        """
        push_log_event("error_404", {"path": request.path})
        return jsonify({
            "error": "not_found",
            "message": "Requested resource does not exist."
        }), 404

    # --------------------------------------------------------
    # 400 – Bad Request
    # --------------------------------------------------------
    @app.errorhandler(400)
    def handle_400(err):
        """
        Validation or malformed request.
        """
        push_log_event("error_400", {"path": request.path, "detail": str(err)})
        return jsonify({
            "error": "bad_request",
            "message": "The request was invalid or incomplete."
        }), 400
