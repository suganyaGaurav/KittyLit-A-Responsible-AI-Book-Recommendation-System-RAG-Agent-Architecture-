# agents/

## Purpose

The `agents` folder contains the **core decision-making and orchestration layer** of KittyLit.  
This layer is responsible for determining **how book recommendations are fetched, merged, ranked, and returned** in a controlled, explainable, and governance-aware manner.

This is **not a UI layer** and **not a data storage layer**.  
It acts as the **brain of the system**, coordinating cache usage, database access, live API calls, and optional RAG retrieval using deterministic rules.

---

## Key Responsibilities

        The `agents` module is responsible for:
        
        - Deciding **which data source** to use (cache, DB, live API, or RAG)
        - Orchestrating the **end-to-end recommendation pipeline**
        - Enforcing **priority order and fallbacks**
        - Normalizing and merging results from multiple sources
        - Ranking results deterministically
        - Tracking metadata for **explainability and developer logs**
        - Exposing a **scoped agent API** via Flask Blueprint

---

## Files Overview

### `__init__.py`
Package initializer for the `agents` module.

- Makes the `AgentOrchestrator` class directly importable
- Defines `agents` as a reusable package

---

### `agent_tools.py`
Helper utilities used by the agent layer.

        Responsibilities:
        - Fetching live book data from Google Books API
        - Enforcing daily API quota limits
        - Tracking API usage (`data/api_usage.json`)
        - Maintaining a lightweight in-memory cache
        - Normalizing external API responses into KittyLit’s internal schema
        - Mapping publication years into `year_category` buckets

Key concepts:
- Explicit quota control
- Defensive API access
- Normalized, schema-safe outputs

---

### `decision_rules.py`
Deterministic decision logic for selecting the data source.

        Responsibilities:
        - Decide whether to use cache, live API, or RAG
        - Enforce cache freshness rules
        - Prevent API overuse by respecting daily limits

Decision priority:
1. Cache (if fresh)
2. Live API (if quota available)
3. RAG fallback

This file ensures **predictable behavior** and avoids arbitrary model decisions.

---

### `errors.py`
Centralized custom exception definitions for the agent layer.

Defined errors:
- `LiveDataFetchError`
- `RAGProcessingError`
- `DecisionRuleError`

Purpose:
- Keep error handling explicit
- Separate agent-level failures from UI or infrastructure errors
- Improve observability and debugging clarity

---

### `merge_and_rank.py`
Logic for combining and ranking results from multiple sources.

        Responsibilities:
        - Merge live API results and RAG results
        - Remove duplicates using normalized book titles
        - Rank books using popularity or relevance signals
        - Optionally update book popularity metrics in the database

This module ensures **consistent result ordering** across runs.

---

### `orchestrator.py`
The **core orchestration engine** of KittyLit.

        Responsibilities:
        - Execute the full recommendation pipeline:
          - Cache → DB → Live API → RAG
        - Generate query hashes for cache reuse
        - Merge and rank results
        - Track latency, counts, and decision traces
        - Update database metadata (e.g., last accessed)
        - Push structured developer logs
        - Return results with explainability metadata

Design principles:
- Deterministic execution
- Explicit fallbacks
- No autonomous behavior
- Full traceability

This is the **single source of truth** for how recommendations are produced.

---

### `routes.py`
Flask Blueprint exposing agent-level API endpoints.

        Responsibilities:
        - Define `/agent/recommend` endpoint
        - Validate incoming request payloads
        - Invoke `AgentOrchestrator`
        - Return structured JSON responses
        - Handle errors safely

This file connects the agent system to the web layer **without leaking internal logic**.

---

## What This Folder Does NOT Do

- No HTML rendering
- No direct UI logic
- No training or fine-tuning
- No autonomous agent loops
- No uncontrolled LLM calls

All behavior is **rule-driven, observable, and bounded**.

---

## Design Philosophy

- Determinism over creativity
- Governance before optimization
- Explainability as a first-class concern
- Clear separation of responsibilities

This folder represents the **decision intelligence layer** of KittyLit.
