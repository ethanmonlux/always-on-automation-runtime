# Always-On Automation Runtime — Architecture

This repository is a **generic execution layer** for API-driven automation. It ingests **structured webhook signals**, applies **validation + idempotency**, enforces **guardrails**, and executes **actions** through modular external-service connectors.

> Note: This is a **sanitized** reference implementation meant to demonstrate architecture patterns (reliability, operator controls, safe execution). It intentionally omits production secrets, proprietary logic, and any broker-specific credentials.

---

## Goals

- **Always-on execution**: runs continuously and handles intermittent failures gracefully.
- **Deterministic behavior**: same input → same outcome (or explicit, observable failure).
- **Idempotent processing**: safe to retry without duplicating side effects.
- **Operator-friendly**: clear status, intervention controls, and safe test modes.
- **Composable integrations**: external APIs are wrapped behind clean connector interfaces.

---

## High-level flow

```mermaid
flowchart TD
  A[Signal Source<br/>External system] --> B[Webhook Ingestion<br/>FastAPI endpoint]
  B --> C[Validation + Auth<br/>Schema checks / API key]
  C --> D[Idempotency Check<br/>Seen signal?]
  D -->|new| E[Persistent State<br/>SQLite/Postgres]
  D -->|duplicate| Z[Return 200 OK<br/>no-op]
  E --> F[Guardrails / Policy Layer<br/>limits, kill-switch]
  F --> G[Execution Layer<br/>connector(s)]
  G --> H[External Service API]
  H --> I[State Update<br/>store result]
  I --> J[Notifications<br/>logs / alerts]
  J --> K[Operator Controls<br/>status, intervention]
```

---

## Components

### 1) Webhook Ingestion (FastAPI)
- Receives POST requests with a **structured payload** (signal id, type, parameters).
- Performs **schema validation** and basic auth (e.g., shared secret header).
- Returns **200 OK** for duplicates and for safe-degraded failures (so the sender doesn't spam retries).

### 2) Idempotency + Persistent State
- Uses a durable store (SQLite locally; Postgres in production) to record:
  - processed signal ids (idempotency keys)
  - execution attempts + outcomes
  - minimal operational metadata (timestamps, last known state)
- Enables **at-least-once delivery** from upstream while preventing duplicate side effects.

### 3) Guardrails / Policy Layer
A deterministic decision gate applied **before** any side effects:
- kill-switch / pause trading / “exit-only” mode
- leverage / exposure caps
- position limits, max order notional, etc. (domain-specific rules)

### 4) Execution Layer (Connectors)
- External APIs are accessed through connector interfaces:
  - `place_action(...)`
  - `get_state(...)`
  - `cancel_action(...)` (where supported)
- Connector boundaries allow you to add new integrations without rewriting the core runtime.

### 5) Reliability Patterns
- **Retry-safe execution**:
  - only retry operations that are safe to retry
  - record attempts + outcomes
- **Backoff**:
  - controlled retry schedule rather than hot-looping
- **Circuit breaker**:
  - stop new actions after repeated failures and require operator intervention
- **Degraded mode**:
  - if the DB is unavailable, do not crash the server—return safe responses and surface the degraded state in status.

### 6) Operator Controls
- `/admin/status` (or equivalent) for:
  - current mode (enabled/paused/exit-only)
  - last signal processed
  - degraded states / warnings
  - recent errors
- Optional mock/sim modes for **off-hours testing**.

---

## Local vs Production

### Local (developer workflow)
- SQLite for persistence
- mock connector(s)
- verbose logs

### Production (deployment)
- Postgres for persistence
- real connector(s) with secure secrets storage
- alerts/notifications enabled
- strict auth + rate limits

---

## What this demonstrates
- A production-minded execution runtime (not a notebook/demo)
- Idempotency, persistence, and operator control patterns
- Clean separations between ingestion, policy, execution, and observability
