# KittyLit – System Architecture Overview

KittyLit is a responsible AI system designed to provide parents with **safe, reliable, and age-appropriate children’s book recommendations**.

The system is built with a **design-first, governance-first philosophy**, prioritizing:
- determinism over creativity
- transparency over automation
- safety over scale

The core recommendation engine is intentionally **non-LLM and non-RAG**, ensuring predictable behavior and zero hallucination risk.

This document explains the architecture of:
1. The **Main Book Recommendation System** (deterministic)
2. The **Help Chatbot System** (RAG-based, isolated)

These two systems are **strictly separated** by design.

---

## 1. High-Level Architecture (Main Recommendation System)

**Flow**

User (Parent)  
→ UI  
→ Flask Routes  
→ Service Layer  
→ Agent Orchestrator  
→ Cache  
→ Database  
→ Safety & Governance Filters  
→ Final Ranked Output  

**Key Principle**

The **main recommendation system does NOT use LLMs or RAG**.  
All decisions are rule-based, deterministic, and explainable.

---

## 2. Core Components – Main System

### 2.1 UI Layer
- Collects parent-provided inputs (age, genre, language, year category)
- Displays structured, stable recommendations
- Designed for clarity, simplicity, and family-friendly interaction
- No business logic or decision-making

---

### 2.2 Backend Routing Layer (Flask)
- Thin HTTP transport layer
- Performs minimal request validation
- Forwards requests to the service layer
- Keeps routing concerns isolated from logic

---

### 2.3 Service Layer
- Normalizes and sanitizes inputs
- Applies basic rule checks
- Generates deterministic query hashes
- Invokes the Agent Orchestrator
- Returns standardized responses to the UI

Purpose:
- Keep routes clean
- Centralize request preparation
- Prevent UI-to-agent coupling

---

### 2.4 Agent Orchestrator (Central Decision Engine)

The Agent Orchestrator is the **decision brain** of KittyLit’s main system.

It determines:
- Whether data should be retrieved from cache or database
- How results should be merged and ranked
- Which deterministic rules apply (age, category, availability)
- When fallback logic is required
- How consistency and safety are maintained across requests

Characteristics:
- Rule-based
- Deterministic
- Fully traceable
- No LLM usage
- No autonomous behavior

This ensures **predictable, parent-trusted output**.

---

### 2.5 Cache Layer
- Preloaded at application startup
- Acts as the first retrieval layer
- Reduces database load
- Provides consistent low-latency responses

Cache is a performance optimization, not a source of truth.

---

### 2.6 Database Layer (SQLite)
- Stores curated book metadata
- Acts as the authoritative source of truth
- Easy to inspect, audit, and debug
- Works in sync with the cache

Designed for transparency over scale.

---

### 2.7 Safety & Governance Filters

Every recommendation passes through safety checks, including:
- Age-appropriateness validation
- Sensitive-topic filtering
- Stability and consistency rules
- PII and unsafe content guards
- Final response validation

These controls ensure KittyLit is suitable for:
- families
- schools
- parent-guided workflows

Safety is enforced **after retrieval and before response**.

---

### 2.8 Response Formatter
- Produces clean, structured JSON responses
- Attaches metadata and explanation fields
- Ensures UI consistency across requests
- Prevents leaking of internal system details

---

## 3. Help Chatbot Architecture (Separate System)

The Help Chatbot is **logically and operationally isolated** from the main recommendation engine.

**Flow**

User  
→ Chat UI  
→ Chat Route  
→ Chat Service  
→ Mini Orchestrator  
→ RAG Pipeline  
→ MiniLM  
→ Safety Filters  
→ Response  

---

### 3.1 RAG Pipeline (Chatbot Only)

RAG is used **exclusively** for:
- answering parenting questions
- explaining reading levels and categories
- providing system guidance

It uses:
- curated domain text
- embeddings for retrieval
- a small, fine-tuned MiniLM
- strict safety filters

**Important Rule**

RAG output **never influences book recommendations**.

---

## 4. End-to-End Flow Summary

### Main Recommendation Flow
1. Parent submits search criteria
2. Flask routes forward request to service layer
3. Service calls the Agent Orchestrator
4. Orchestrator checks cache, then database
5. Results are merged and ranked deterministically
6. Safety filters validate output
7. UI receives stable recommendations

---

### Help Chatbot Flow
1. User asks a help question
2. RAG retrieves relevant text chunks
3. MiniLM generates a short response
4. Safety filters sanitize output
5. UI displays guided answer

---

## 5. Why This Architecture Works

- Zero hallucination risk in main search
- Deterministic and predictable behavior
- Cache-first design for performance
- Safety enforced at multiple layers
- Clear separation of concerns
- RAG isolated to chatbot only
- Easy to audit, debug, and explain
- Traditional engineering discipline over complexity

---

## 6. Architecture Diagram

The diagram below illustrates the separation between:
- the deterministic recommendation system
- the probabilistic chatbot system



![KittyLit System Architecture](docs/assets/kittylit_architecture.png)
