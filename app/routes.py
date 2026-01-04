"""
app/routes.py
---------------
HTTP routing layer for KittyLit.
Thin transport layer → delegates business logic to services and agents.

Author: **Suganya P**
Date: 2025-11-29

UPDATED: 2025-12-09
CHANGE:
    - Replaced `year` with `year_category` for form search.
    - Reason: numeric publication years were inconsistent in DB/API.
              Year buckets give parents more stable results.
"""
# ============================================================
# =                         IMPORTS                           =
# ============================================================

from flask import Blueprint, jsonify, request, render_template
import logging
import re

# Service layer (form search pipeline → orchestrator)
from .services import search_service

# Correct developer-log writer
from app.gateways.developer_logs import push_log_event


# ============================================================
# =                         LOGGER                            =
# ============================================================

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("kittylit.routes")


# ============================================================
# =               GOVERNANCE / SAFETY FILTERS                 =
# ============================================================

BLACKLIST_PATTERNS = [
    r"\b(piracy|torrent|crack|download\s+pdf)\b",
    r"\b(illegal|copyright)\b"
]


def safe_values(value: str):
    """Validate dropdown values for basic governance compliance."""
    if not value:
        return True, "ok"

    for pattern in BLACKLIST_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return False, "disallowed_content"

    if len(value) > 200:
        return False, "value_too_long"

    return True, "ok"


# ============================================================
# =                  ROUTE REGISTRATION ENTRY                 =
# ============================================================

def register_routes(app):

    bp = Blueprint("main", __name__)

    # --------------------------------------------------------
    # HOME PAGE
    # --------------------------------------------------------
    @bp.route("/", methods=["GET"])
    def home():
        return render_template("index.html")

    # --------------------------------------------------------
    # HEALTH CHECK
    # --------------------------------------------------------
    @bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    # --------------------------------------------------------
    # FORM SEARCH  (UPDATED: year_category support)
    # --------------------------------------------------------
    @bp.route("/search", methods=["POST"])
    def search():
        body = request.get_json() or {}

        # ======================================================
        # UPDATED 2025-12-09
        # Reason:
        #   - UI now sends `year_category` instead of `year`
        #   - No other payload changes
        # ======================================================
        logger.debug(f"[ROUTE] /search payload: {body}")
        push_log_event("route_search_received", {"payload": body})

        # Governance validation
        for key, val in body.items():
            ok, reason = safe_values(str(val))
            if not ok:
                logger.warning(f"[GOV] Blocked /search {key}={val} → {reason}")
                push_log_event("blocked_query", {
                    "field": key,
                    "value": val,
                    "reason": reason
                })
                return jsonify({"error": "blocked_query", "reason": reason}), 400

        # --------------------------------------------------------
        # Pass payload to service → orchestrator
        # --------------------------------------------------------
        try:
            resp = search_service(body)

            push_log_event("route_search_success", {
                "returned_items": len(resp.get("items", []))
            })

            return jsonify(resp), 200

        except Exception as e:
            logger.exception("route_search_error")
            push_log_event("route_search_error", {"error": str(e)})
            return jsonify({"error": "internal_server_error", "detail": str(e)}), 500

    # --------------------------------------------------------
    # DROPDOWN OPTIONS
    # --------------------------------------------------------
    @bp.route("/dropdowns", methods=["GET"])
    def dropdowns():
        try:
            from .data_loader import get_dropdown_values
            values = get_dropdown_values()
            return jsonify(values), 200
        except Exception as e:
            logger.exception("dropdown_error")
            push_log_event("dropdown_error", {"error": str(e)})
            return jsonify({"error": "internal_server_error"}), 500

    # --------------------------------------------------------
    # DEVELOPER LOGS PAGE
    # --------------------------------------------------------
    @bp.route("/developer", methods=["GET"])
    def developer_page():
        return render_template("developer_logs.html")

    # --------------------------------------------------------
    # DEVELOPER LOGS FEED
    # --------------------------------------------------------
    @bp.route("/developer/logs", methods=["GET"])
    def developer_logs_api():
        from .gateways.developer_logs import fetch_recent_logs
        logs = fetch_recent_logs(limit=50)
        return jsonify(logs), 200

    app.register_blueprint(bp)
