# Always-On Automation Runtime (Sanitized Demo)

A reliability-focused execution layer for continuously running automation systems and agent-style workflows. This is a sanitized demo of a production system - see **What the full system contains** below for scope.

---

## What this demonstrates

Most automation demos show a happy path working once. This focuses on what breaks in production and how to handle it safely:

- Webhook ingestion with authentication and payload validation
- Idempotent execution - duplicate events never re-run, state survives restarts
- Persistent state store with pluggable backends (SQLite in demo, Postgres in production)
- Guardrails engine - allowlists, payload validation, fail-closed defaults
- Modular connector layer - external integrations behind clean interfaces
- Operator controls - kill switch, status endpoint, mode toggling

---

## What the full production system contains

This public repo is intentionally stripped. The production system this is derived from includes:

**Layered safety gate chain**
Ordered checks before any execution covering auth, system health, signal integrity (idempotency, staleness, dedup), operator state (kill switch, degraded mode, circuit breaker), and configurable risk constraints.

**External integration layer**
Protocol-based interface with multiple implementations: mock for tests and staging, and live integrations with OAuth token management. Fail-safe defaults at every layer.

**Reliability patterns across the stack**
Idempotency keys, durable retry queue with exponential backoff, circuit breaker, kill switch, degraded mode flags, ASGI request size enforcement, constant-time auth, startup validation, concurrent execution control, and alert throttling.

**11 background loops**
Token management, cleanup, monitoring, retry worker, scheduled compliance checks, AI-powered recaps, snapshots, and pre-session briefing.

**Operator surface**
Web dashboard (Vite SPA served from FastAPI). Chat-based commands with signature verification and user allowlist. Admin REST API. Runtime config overrides without redeployment.

**LLM integration**
AI-generated recaps and anomaly explanations via Claude. Fail-silent - never on the critical execution path.

**Test coverage**
40+ test files covering failure modes, DB failover, idempotency, monitoring behavior, rate limiting, request size enforcement, retry queue, operator command interactions, and webhook gate chain behavior.

**Deployment**
Railway, Docker Compose for local, GitHub Actions CI, three-environment setup (test/staging/live) with isolated DBs and secrets.

---

## Architecture (demo)

```
Signal Source
-> Webhook ingestion (FastAPI)
-> Validation + auth + idempotency
-> Persistent state (SQLite in demo, Postgres in production)
-> Guardrails engine (allowlist, kill switch)
-> Execution layer (pluggable connectors)
-> State update + operator tooling (/admin/status, kill switch)
```

---

## Endpoints (demo)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `GET` | `/admin/status` | System mode + processed count |
| `POST` | `/admin/kill_switch?enabled=true\|false` | Operator kill switch |
| `POST` | `/webhook` | Ingest an event (idempotent + guardrails + execute) |

---

## Running locally

**Mac/Linux**
```bash
bash run_local.sh
```

**Windows PowerShell**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

$env:API_KEY="demo-key"
uvicorn app.main:app --reload --port 8080
```

---

## Smoke test

```bash
# Health check
curl http://127.0.0.1:8080/health

# Execute once
curl -X POST http://127.0.0.1:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  --data-binary "@examples/sample_webhook.json"

# Prove idempotency (same signal_id -> duplicate, not re-executed)
curl -X POST http://127.0.0.1:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  --data-binary "@examples/sample_webhook.json"

# Operator kill switch blocks new executions
curl -X POST "http://127.0.0.1:8080/admin/kill_switch?enabled=true"
curl -X POST http://127.0.0.1:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  --data-binary "@examples/sample_webhook.json"

# Re-enable
curl -X POST "http://127.0.0.1:8080/admin/kill_switch?enabled=false"

# Status
curl http://127.0.0.1:8080/admin/status
```

> To re-run with the same `signal_id`, delete `state.sqlite` or change the `signal_id` in `examples/sample_webhook.json`.

---

## Key concepts demonstrated

- **Idempotency:** duplicate webhook deliveries do not cause duplicate execution
- **Persistent state:** behavior is deterministic across restarts
- **Guardrails:** centralized policy checks before any external side-effects
- **Composable connectors:** external systems behind clean interfaces
- **Operator controls:** health/status + kill switch for safe intervention
- **Fail-closed defaults:** unknown states reject rather than proceed

---

## What is intentionally omitted

- Real credentials or account identifiers
- Proprietary business logic or domain-specific strategy
- Live integrations
- The operator dashboard and chat command layer

The goal is to demonstrate execution-layer patterns used for reliable automation and agent-style systems.

---

## License

MIT
