# security/

## Purpose

The `security` folder contains **cross-cutting governance and observability components** for KittyLit.

This layer is responsible for **audit logging, request tracing, and system-level visibility** across all modules (Flask, agents, RAG, cache, DB, scripts).  
It does not implement authentication or authorization; instead, it ensures that **every action taken by the system is traceable and explainable**.

---

## Design Principles

- Centralized logging configuration
- Structured, machine-readable logs (JSON)
- Deterministic request tracing
- Component-level attribution
- Safe for threaded and async execution
- No business logic mixed with security concerns

This layer is intentionally independent of application logic.

---

## Files Overview

### `audit_logger.py`

Centralized JSON logging and request tracing utility for KittyLit.

#### Responsibilities

- Configure a **single root logger** for the entire system
- Emit logs in **one-line JSON format** for easy parsing and ingestion
- Propagate a **request_id** across threads and async contexts
- Attach a **component label** (flask, agent, rag, security, db, api, etc.)
- Write logs to:
  - Console
  - Rotating log file (`logs/app.log`)
- Provide convenience helpers for consistent log emission
- Measure and log function latency using decorators

---

#### Key Features

**Request Tracing**
- Uses `contextvars` to safely store `request_id` and `component`
- Supports propagation across async and multi-threaded code
- Allows incoming request IDs or auto-generation

**Structured JSON Logs**
Each log entry contains:
- timestamp (UTC)
- log level
- logger name
- request_id
- component
- event name
- optional structured fields
- serialized exception details (if any)

**Rotating File Logging**
- Prevents unbounded log growth
- Configurable size and retention
- Safe defaults for local and demo environments

**Timing Decorator**
- Measures execution latency in milliseconds
- Emits start / end events
- Captures failure state automatically

---

## How This Module Is Used

- Initialized once during application startup
- Request context set in Flask `before_request`
- Used uniformly by:
  - `app/`
  - `agents/`
  - `rag_pipeline/`
  - `scripts/`
- Never instantiated ad hoc in business logic

---

## What This Folder Does NOT Do

- No authentication or authorization
- No user identity management
- No encryption or secrets handling
- No request blocking or filtering

Its sole responsibility is **visibility, traceability, and auditability**.

---

## Governance Rationale

This logging layer ensures that:
- Every recommendation can be traced to its source
- Data sources used are observable
- Latency and failures are measurable
- The system can be audited without model introspection

This is a foundational requirement for **responsible and explainable AI systems**.
