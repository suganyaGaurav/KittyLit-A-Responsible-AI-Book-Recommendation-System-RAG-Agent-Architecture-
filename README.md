# KittyLit – A Responsible AI Book Recommendation System

Deterministic Recommendation Pipeline + RAG-Based Chatbot

KittyLit is a production-oriented AI system for children’s book recommendations and guided reading assistance. It is engineered with governance, observability, fallback control, and evaluation embedded from the start.

This project demonstrates how a real-world Generative AI system should be built — prioritizing correctness, traceability, safety, and reliability over unchecked model creativity.

---

## Project Overview

KittyLit consists of two clearly separated subsystems:

1. Deterministic Recommendation Pipeline (Primary search experience)  
2. RAG-Based Chatbot System (Knowledge and guided interaction)

Both subsystems share governance rules and structured logging, but they operate independently by design.

This separation ensures:

- Predictable recommendation behavior  
- Controlled LLM usage  
- Cost awareness  
- Auditability  
- Clear evaluation boundaries  

---

## Problem Statement

Many AI-based recommendation or chatbot systems suffer from:

- Hallucinated or fabricated results  
- LLM treated as a source of truth  
- No fallback or abstention behavior  
- Poor observability  
- Governance added after deployment  
- No measurable evaluation framework  

In the context of children’s content, these risks are amplified due to safety, appropriateness, and trust requirements.

KittyLit addresses these challenges through explicit system design decisions.

---

# System Architecture

## Recommendation System (Deterministic Orchestrator)

This is the primary book search experience.

Pipeline:

User Query  
-> Governance Checks  
-> Cache Lookup  
-> Database Query  
-> Live External API (only if needed)  
-> Structured Logging  
-> Response  

Characteristics:

- No LLM usage  
- No RAG involvement  
- Fully deterministic routing  
- Cost-controlled  
- Predictable latency  
- Explicit failure handling  

---

### Data Lifecycle and Caching Strategy

The recommendation pipeline improves efficiency over time.

- If a book is fetched from the Live API, it is persisted into the local database.  
- Frequently accessed books are promoted into the cache layer.  
- Subsequent queries prioritize Cache -> Database before calling the external API.  

This ensures:

- Reduced external API calls  
- Lower operational cost  
- Faster response times on repeated queries  
- Progressive strengthening of the local knowledge base  

The system becomes more efficient as it is used.

---

### Failure Handling (Recommendation Pipeline)

- Cache miss -> Check database  
- Database miss -> Call Live API  
- Live API failure -> Return safe error response  
- All decisions are logged with latency and reason codes  

The system does not crash due to external API failure.

---

## Chatbot System (RAG + Controlled LLM)

The chatbot is designed for:

- Reading guidance  
- Book-related knowledge questions  
- Safe conversational interaction  

Pipeline:

User Query  
-> Intent Detection (greeting / redirect / knowledge / general)  
-> Governance Layer (PII checks and safety rules)  
-> RAG Retrieval (FAISS with metadata filters)  
-> Context Sufficiency Check  
-> LLM Generation (if allowed)  
-> Structured Logging  
-> Response  

Key Design Principles:

- Retrieval is treated as the grounding source  
- Similarity thresholds are enforced  
- System abstains if retrieval confidence is low  
- LLM output is constrained by retrieved context  
- API failures trigger graceful fallback  
- All decisions are logged and traceable  

The LLM is not treated as a source of truth. It generates responses only when retrieval and governance checks pass.

---

# Governance-First Design

Safety is enforced before generation.

Implemented safeguards include:

- PII detection and redaction  
- Child-safe and age-appropriate filtering  
- Intent classification  
- Confidence thresholds  
- Explicit fallback responses  
- Structured error handling  

The system prefers safe abstention over speculative output.

---

# Observability and Structured Logging

Both subsystems provide structured logs including:

- User query  
- Intent classification  
- Retrieval similarity scores  
- Retrieved chunks  
- Model name and parameters (chatbot only)  
- Governance decisions  
- Fallback activation  
- Error type (if any)  
- Latency breakdown per component  

A developer logs endpoint enables inspection of:

- Recommendation pipeline traces  
- Chatbot RAG traces  

This enables reproducibility, debugging, and audit readiness.

---

# Evaluation Framework

Evaluation is integrated into the design.

Retrieval Metrics (Chatbot):

- Recall@K  
- Mean Reciprocal Rank (MRR)  
- nDCG  
- Similarity distribution analysis  

Generation Evaluation:

- Groundedness checks  
- Citation precision  
- Hallucination detection  
- Abstention rate  

System Metrics:

- Latency (p50, p95)  
- Cost per query  
- Fallback activation rate  
- Error rate  

Metrics support continuous improvement and governance review.

---

# Technology Stack

- Backend: Python (Flask or FastAPI)  
- Embeddings: MiniLM Sentence Transformer  
- Vector Store: FAISS  
- LLM: OpenAI or AWS Bedrock (configurable)  
- Database: SQLite or JSON  
- Cache: In-memory caching layer  
- Memory: Short-term buffer and summary memory  
- Logging: Structured JSON logs  

---

# Repository Structure

app/  
- recommendation/        Cache -> DB -> Live API pipeline  
- chatbot/               RAG + LLM logic  
- governance/            Safety and filtering rules  
- logging/               Structured log utilities  
- routes/                API endpoints  

data/  
- books_dataset.json  
- faiss_index/  

templates/  
- index.html  
- developer_logs.html  

---

# Design Philosophy

KittyLit prioritizes:

- Determinism over randomness  
- Traceability over opacity  
- Safety over fluency  
- Cost control over unrestricted generation  
- Modular separation over monolithic AI pipelines  

The goal is not to build a feature-heavy demo, but to demonstrate how trustworthy, production-minded AI systems should be engineered.
