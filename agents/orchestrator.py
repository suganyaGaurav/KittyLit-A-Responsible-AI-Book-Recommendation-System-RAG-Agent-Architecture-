'''
orchestrator.py
---------------
Production Orchestrator for KittyLit (Form-Based Pipeline)

Purpose:
    - Cache → DB → Live API fallback chain
    - Optional RAG
    - Merge + Rank + (No enforced Top-K now)
    - Metrics & developer logs
    - Explainability & governance

Author: **Suganya P**
Date: 2025-11-30

UPDATED: 2025-12-09
CHANGES:
    - Removed fixed Top-K = 5 cutoff.
    - Now returns ALL ranked results.
    - Added safe Top-K logic (TOP_K=None means full list).
    - Replaced `publication_year` with `year_category`.
'''

# ============================================================
# =                        IMPORTS                           =
# ============================================================

import logging
import hashlib
import json
import time
from datetime import datetime
from collections import deque
from threading import Lock

# Cache + DB + Live API
from .agent_tools import get_cached_results, set_cache_results, fetch_live_data
from .decision_rules import decide_data_source
from .merge_and_rank import merge_results, rank_results
from rag_pipeline.retriever import search_books

# Correct DB import
from app.db_utils import query_books, update_book

# Gateway developer log writer
from app.gateways.developer_logs import push_log_event


# ============================================================
# =                       LOGGER                              =
# ============================================================

logger = logging.getLogger("kittylit.orchestrator")


# ============================================================
# =                       CONSTANTS                           =
# ============================================================

# TOP_K is optional now — None = return ALL results
TOP_K = None


# ============================================================
# =                   ORCHESTRATOR CLASS                     =
# ============================================================

class AgentOrchestrator:
    """Main orchestration engine for form-based search."""

    def __init__(self):
        logger.info("AgentOrchestrator initialized.")

    def _ts(self):
        """Return timestamp in ms."""
        return time.perf_counter() * 1000

    # --------------------------------------------------------
    # Main Pipeline
    # --------------------------------------------------------
    def handle_query(self, qp: dict, ctx: dict = None):
        """
        Core pipeline:
            - Normalize filters
            - Query hash
            - Decide source
            - Cache → DB → Live API
            - Optional RAG
            - Merge + Rank + (Full results)
            - DB last_accessed update
            - Push developer logs
        """
        ctx = ctx or {}
        cid = ctx.get("correlation_id")
        start = self._ts()

        # ----------------------------------------------------
        # Normalize UI input
        # ----------------------------------------------------
        normalized = {
            "age_group": qp.get("age"),
            "genre": qp.get("genre"),
            "language": qp.get("language"),
            "year_category": qp.get("year_category"),
        }

        # ----------------------------------------------------
        # Query hash
        # ----------------------------------------------------
        try:
            qjson = json.dumps(normalized, sort_keys=True)
            qh = hashlib.md5(qjson.encode()).hexdigest()
        except:
            qh = hashlib.md5(str(time.time()).encode()).hexdigest()

        metadata = {
            "query_hash": qh,
            "correlation_id": cid,
            "decision_trace": [],
            "latencies_ms": {},
            "counts": {},
        }

        logger.info(f"[Orch] Query {qh[:8]} cid={cid} params={normalized}")

        # ----------------------------------------------------
        # Decide data source
        # ----------------------------------------------------
        t0 = self._ts()
        try:
            source = decide_data_source(qh, normalized)
        except Exception:
            source = "db"
        metadata["latencies_ms"]["decision_ms"] = round(self._ts() - t0, 2)
        metadata["decision_trace"].append({"step": "decide", "source": source})

        # ----------------------------------------------------
        # Tier 1: Cache
        # ----------------------------------------------------
        t0 = self._ts()
        cache_hits = []
        if source == "cache":
            try:
                resp = get_cached_results(qh)
                if resp and "data" in resp:
                    cache_hits = resp["data"]
            except Exception:
                pass
        metadata["latencies_ms"]["cache_ms"] = round(self._ts() - t0, 2)
        metadata["counts"]["cache"] = len(cache_hits)

        # ----------------------------------------------------
        # Tier 2: DB
        # ----------------------------------------------------
        t0 = self._ts()
        db_hits = []
        if not cache_hits:
            try:
                db_hits = query_books(normalized) or []
            except Exception:
                pass
        metadata["latencies_ms"]["db_ms"] = round(self._ts() - t0, 2)
        metadata["counts"]["db"] = len(db_hits)

        # ----------------------------------------------------
        # Tier 3: Live API fallback
        # ----------------------------------------------------
        t0 = self._ts()
        live_hits = []
        if not cache_hits and not db_hits:
            try:
                live_hits = fetch_live_data(normalized) or []
                set_cache_results(qh, live_hits)
            except Exception:
                pass
        metadata["latencies_ms"]["live_ms"] = round(self._ts() - t0, 2)
        metadata["counts"]["live"] = len(live_hits)

        # ----------------------------------------------------
        # Optional RAG
        # ----------------------------------------------------
        t0 = self._ts()
        try:
            rag_hits = search_books(normalized) or []
        except Exception:
            rag_hits = []
        metadata["latencies_ms"]["rag_ms"] = round(self._ts() - t0, 2)
        metadata["counts"]["rag"] = len(rag_hits)

        # ----------------------------------------------------
        # Merge + Rank (NO Top-K cutoff now)
        # ----------------------------------------------------
        combined = cache_hits + db_hits + live_hits

        try:
            merged = merge_results(combined, rag_hits)
        except:
            merged = combined + rag_hits

        try:
            ranked = rank_results(merged)
        except:
            ranked = merged

        # NEW LOGIC — return FULL list
        if TOP_K and isinstance(TOP_K, int):
            top_k = ranked[:TOP_K]
        else:
            top_k = ranked

        metadata["counts"]["top_k"] = len(top_k)

        # ----------------------------------------------------
        # Update DB last_accessed
        # ----------------------------------------------------
        for book in (top_k or []):
            isbn = book.get("isbn")
            if isbn:
                try:
                    update_book(isbn, {
                        "last_accessed": datetime.utcnow().isoformat()
                    })
                except Exception:
                    pass

        # ----------------------------------------------------
        # Final metadata
        # ----------------------------------------------------
        metadata["latencies_ms"]["total_ms"] = round(self._ts() - start, 2)
        metadata["source_selected"] = source

        # ----------------------------------------------------
        # Developer logs
        # ----------------------------------------------------
        try:
            push_log_event("orchestrator_event", {
                "timestamp": datetime.utcnow().isoformat(),
                "query_hash": qh,
                "correlation_id": cid,
                "decision_summary": {
                    "source": source,
                    "counts": metadata["counts"],
                    "latencies_ms": metadata["latencies_ms"],
                },
                "decision_trace": metadata["decision_trace"],
            })
        except:
            pass

        return {
            "books": top_k,
            "chatbot_reply": "Chatbot not used for form search.",
            "metadata": metadata,
        }


# ============================================================
# =                   WRAPPER FOR services.py                =
# ============================================================

agent_orchestrator = AgentOrchestrator()

def decide_and_fetch(qh, qp, ctx=None):
    """Wrapper for services.py compatibility."""
    result = agent_orchestrator.handle_query(qp, ctx)
    return result["books"], result["metadata"]
