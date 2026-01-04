# KittyLit – A Responsible AI Book Recommendation System  
(RAG + Agent-Oriented Architecture)

KittyLit is a production-minded MVP designed with reliability, governance, and evaluation embedded from the beginning. This project demonstrates how a real-world Generative AI system should be engineered —
prioritizing correctness, safety, explainability, fallback logic, and observability over unchecked model creativity.

---

## Project Overview

KittyLit is an AI-driven children’s book recommendation system built using a custom Retrieval-Augmented Generation (RAG) pipeline combined with a deterministic agent-based orchestrator. The objective was not to build a large or feature-heavy application,
but to demonstrate how a real-world GenAI system should be designed and operated in a responsible, controlled, and auditable manner. This repository reflects a practical, systems-level understanding of how trustworthy and scalable AI systems are built.

---

## Problem Statement

Most AI-based recommendation or chatbot systems suffer from the following issues:

- Hallucinated or fabricated recommendations  
- Lack of grounding in verified data sources  
- No clear fallback behavior when confidence is low  
- Poor observability and debugging capability  
- Governance and safety added as an afterthought  
- No clear evaluation of retrieval or generation quality  

In the context of children’s content, these issues become even more critical due to safety, trust, and appropriateness requirements.

---

## How the Problem Was Solved

KittyLit addresses these challenges through explicit system design choices:

- Retrieval is treated as the source of truth, not the LLM  
- Similarity thresholds and context sufficiency checks are enforced  
- The system explicitly abstains when confidence is low  
- Governance checks are applied before generation  
- Every decision path is logged and traceable  
- Evaluation metrics are designed into the system from day one  

The result is a system that prefers safe, correct behavior over fluent but unreliable output.

---

## What Makes This Project Unique

- Governance-first design rather than prompt-only safety  
- Deterministic agent orchestration instead of implicit LLM reasoning  
- Explicit fallback-first architecture to reduce hallucinations and cost  
- Evaluation and observability treated as core features, not add-ons  
- Clear separation of responsibilities across retrieval, routing, and generation  
- Designed to be auditable, explainable, and reproducible  

This project emphasizes engineering discipline over demo-driven design.

---

## Key System Features

### Responsible AI Principles Built Into the Design

- PII detection and redaction  
- Child-safe and age-appropriate content rules  
- Transparent outputs with citations  
- Confidence scoring and fallback reasoning  
- Intent classification to prevent unsafe actions  

Safety checks are enforced before generation, not patched afterward.

---

### Custom RAG Pipeline

- Cleaned and validated book dataset  
- MiniLM sentence embedding model  
- FAISS vector index using exact search  
- Hybrid retrieval using semantic similarity and metadata filters  
- Reranking for improved relevance  
- Context sufficiency checks before allowing generation  

The LLM is never treated as a source of truth.

---

### Agent Orchestrator With Deterministic Control

- Rule-based routing across system components:
  - Cache
  - Database
  - RAG pipeline
  - LLM (used only as a fallback)
- Custom fallback logic
- Short-term conversational memory
- Summary-based long-term memory
- Complete traceability through structured logs  

This ensures predictable, debuggable system behavior.

---

### Fallback-First Architecture

To minimize hallucinations and control cost, the system follows a strict priority order:

Cache → Database → RAG → External API → LLM

Each step includes:

- Explicit decision criteria  
- Clear failure handling  
- Logged reasoning paths  

---

## Evaluation Framework

Evaluation is integrated into the system design, not added later.

Metrics tracked include:

- Recall@K  
- Mean Reciprocal Rank (MRR)  
- nDCG  
- Groundedness checks  
- Hallucination detection  
- Citation precision  
- Latency distribution (p50, p95)  
- Cost per query  
- Fallback activation rate  

These metrics support offline analysis, debugging, and continuous improvement.

---

## Monitoring and Observability

KittyLit provides full system observability through:

- Structured logs at every pipeline stage  
- Retrieval similarity and ranking logs  
- Error and fallback tracing  
- Latency breakdown per component  
- Confidence and risk indicators  

Every response is traceable and reproducible.

---

## Tech Stack

- Backend: Python, Flask or FastAPI  
- Embeddings: MiniLM Sentence Transformer  
- Vector Store: FAISS  
- LLM: OpenAI or AWS Bedrock (configurable)  
- Database: SQLite or JSON  
- Memory: Buffer memory and summary memory  
- Monitoring: Custom structured logging  

---

## Architecture Summary

User Query  
↓  
Governance Layer (PII checks, safety rules, intent detection)  
↓  
Routing Logic  
- Cache Lookup  
- Database Query  
- RAG Retrieval (FAISS)  
- LLM Generation (fallback only)  
↓  
Explainability Layer (sources, confidence, fallback reason)  
↓  
Final Answer  

---

## Repository Structure

