# ============================================================
# audit_logger.py
# Centralized JSON logging + request tracing for KittyLit
# - Consistent JSON logs across Flask, Agent, RAG, Security
# - request_id propagation using contextvars (thread/async-safe)
# - Rotating file handler + console handler
# - Convenience helpers: info/debug/warn/error + timing decorator
# ============================================================

import os
import json
import time
import logging
import uuid
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from contextvars import ContextVar

# -------------------------------
# [SECTION] Context (per-request)
# -------------------------------
_request_id: ContextVar[str] = ContextVar("_request_id", default="-")
_component: ContextVar[str] = ContextVar("_component", default="-")

def set_request_id(request_id: str | None = None) -> str:
    """Set/refresh the current request_id in context and return it."""
    rid = request_id or gen_request_id()
    _request_id.set(rid)
    return rid

def get_request_id() -> str:
    """Get the current request_id (or '-' if not set)."""
    return _request_id.get()

def set_component(component: str | None = None) -> None:
    """Set the current logical component (flask|agent|rag|security|chatbot|db|api)."""
    _component.set(component or "-")

def get_component() -> str:
    """Get the current component label (or '-')."""
    return _component.get()

def gen_request_id() -> str:
    """Generate a compact request id."""
    return uuid.uuid4().hex[:12]


# -------------------------------
# [SECTION] JSON Formatter
# -------------------------------
class JSONFormatter(logging.Formatter):
    """Emit log records as one-line JSON with consistent fields."""
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(record, "request_id", get_request_id()),
            "component": getattr(record, "component", get_component()),
            "event": getattr(record, "event", record.msg if isinstance(record.msg, str) else record.getMessage()),
        }

        # Merge extra fields (if any) safely
        extras = {}
        # record.__dict__ contains many internals; select safe extras only
        for k, v in getattr(record, "__dict__", {}).items():
            if k in base or k.startswith("_"):
                continue
            if k in ("msg", "args", "levelname", "levelno", "pathname", "filename",
                     "module", "exc_info", "exc_text", "stack_info", "lineno",
                     "funcName", "created", "msecs", "relativeCreated", "thread",
                     "threadName", "processName", "process"):
                continue
            extras[k] = v

        payload = {**base, **extras}

        # If event was given via logger call's "event" kwarg, avoid duplicating message text
        if "event" in extras:
            payload["event"] = extras["event"]

        # Serialize exceptions if any
        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str, ensure_ascii=False)


# -----------------------------------------
# [SECTION] Logger Construction (idempotent)
# -----------------------------------------
_BUILT = False

def _ensure_dir(path: str) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass  # If path has no directory component, ignore

def build_logger(
    name: str = "kittylit",
    log_level: str | None = None,
    log_file: str | None = None,
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 3
) -> logging.Logger:
    """
    Build the root logger for KittyLit once. Safe to call multiple times.
    Reads defaults from environment:
      LOG_LEVEL (default INFO)
      LOG_FILE  (default logs/app.log)
    """
    global _BUILT
    logger = logging.getLogger(name)
    if _BUILT and logger.handlers:
        return logger

    level = (log_level or os.getenv("LOG_LEVEL", "INFO")).upper()
    file_path = log_file or os.getenv("LOG_FILE", "logs/app.log")

    logger.setLevel(level)

    # JSON formatter for both console and file
    json_fmt = JSONFormatter()

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(json_fmt)
    logger.addHandler(ch)

    # Rotating file handler
    _ensure_dir(file_path)
    fh = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(json_fmt)
    logger.addHandler(fh)

    logger.propagate = False
    _BUILT = True
    # Initial marker
    logger.info("", extra={"event": "logger_initialized", "log_level": level, "log_file": file_path})
    return logger


# ----------------------------------------
# [SECTION] Convenience logging functions
# ----------------------------------------
def _emit(level: int, event: str, **fields):
    """
    Emit a JSON log with standard fields automatically injected:
    - request_id (from context)
    - component  (from context)
    - event      (required arg)
    """
    logger = logging.getLogger("kittylit")
    extra = {"event": event, "request_id": get_request_id(), "component": get_component(), **fields}
    logger.log(level, "", extra=extra)

def log_debug(event: str, **fields): _emit(logging.DEBUG, event, **fields)
def log_info(event: str,  **fields): _emit(logging.INFO,  event, **fields)
def log_warn(event: str,  **fields): _emit(logging.WARNING, event, **fields)
def log_error(event: str, **fields): _emit(logging.ERROR, event, **fields)


# ----------------------------------------
# [SECTION] Timing helper (decorator)
# ----------------------------------------
def log_timing(event: str, component: str | None = None):
    """
    Decorator to measure latency_ms of a function and log start/end events.
    Usage:
        @log_timing("rag_retrieve", component="rag")
        def retrieve(...): ...
    """
    def _wrap(fn):
        def _inner(*args, **kwargs):
            # Optionally override component within this scope
            prev_comp = get_component()
            if component:
                set_component(component)
            start = time.perf_counter()
            log_info(event + "_start")
            try:
                result = fn(*args, **kwargs)
                latency_ms = int((time.perf_counter() - start) * 1000)
                log_info(event + "_end", latency_ms=latency_ms, status="ok")
                return result
            except Exception as ex:
                latency_ms = int((time.perf_counter() - start) * 1000)
                log_error(event + "_end", latency_ms=latency_ms, status="error", exception=str(ex))
                raise
            finally:
                # restore previous component
                set_component(prev_comp)
        return _inner
    return _wrap


# -------------------------------------------------
# [SECTION] Example usage (COMMENTED OUT for import)
# -------------------------------------------------
# if __name__ == "__main__":
#     # 1) Build the logger once at app start (do this in app/__init__.py)
#     build_logger()
#
#     # 2) Set per-request context (do this in Flask before_request)
#     set_request_id()         # or set_request_id(incoming_id)
#     set_component("flask")   # component label for this scope
#
#     # 3) Emit logs
#     log_info("request_received", route="/recommend", method="POST", query_preview="adventure 8yo")
#
#     # 4) Time a function
#     @log_timing("sample_work", component="agent")
#     def work():
#         time.sleep(0.05)
#     work()
#
#     log_info("response_ready", status=200, result_count=5, total_latency_ms=123)
