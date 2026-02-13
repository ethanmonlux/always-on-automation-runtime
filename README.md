# Always-On Automation Runtime (Sanitized Demo)

Reliability-first execution layer for always-on automation and autonomous workflows.

## What this demonstrates (10-second version)

This demo shows the core reliability patterns used in a continuously running automation system:

- Always-on webhook ingestion with authentication + validation  
- Idempotent execution (duplicate events never re-run)  
- Persistent state for deterministic behavior across restarts  
- Guardrails + kill-switch for safe autonomous operation  
- Modular connector layer for external API execution  
- Operator visibility via health + status endpoints  

Designed to operate continuously without supervision and remain predictable even when external systems fail or retry.

This repository is a **sanitized demonstration** of an automation runtime that ingests webhook events, enforces **idempotency** and **guardrails**, executes actions through **modular connectors**, and exposes **operator controls** so it can run continuously without babysitting.

It’s designed to be a reusable backbone for API-driven automation (and AI-assisted systems) where the hard part isn’t “making it work once” — it’s making it **safe, deterministic, and operable** in production.

---

## What this is

A continuously running execution service designed for reliable autonomous workflows:
- Ingests structured webhook events (`POST /webhook`)
- Authenticates requests via an API key header
- Enforces **idempotent processing** using persistent state
- Applies **guardrails** (safe defaults / allowlist / payload sanity)
- Executes actions via a **connector interface** (mocked in this demo)
- Exposes operator endpoints for health/status and safe intervention

> Note: This repo is intentionally **sanitized**. It contains no proprietary strategy logic, real credentials, or production integrations.

---

## Architecture (high level)

Signal Source  
→ Webhook ingestion (FastAPI)  
→ Validation + auth + idempotency  
→ Persistent state (SQLite in demo)  
→ Guardrails engine  
→ Execution layer (pluggable connectors)  
→ State + operator tooling (`/admin/status`, kill switch)

See `docs/architecture.md` for the full overview.

---

## Endpoints (demo)

- `GET /health` — liveness check  
- `GET /admin/status` — system mode + processed count  
- `POST /admin/kill_switch?enabled=true|false` — operator kill switch  
- `POST /webhook` — ingest an event (idempotent + guardrails + execute)

---

## Running locally

### Prereqs
- Python 3.11+

### Quick start (Mac/Linux)
```bash
bash run_local.sh
```

### Manual setup (Mac/Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export API_KEY="demo-key"
uvicorn app.main:app --reload --port 8080
```

### Manual setup (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:API_KEY="demo-key"
uvicorn app.main:app --reload --port 8080
```

---

## Demo (proves behavior)

These commands demonstrate:
- service liveness  
- execution  
- **idempotency** (duplicate event is not re-executed)  
- **operator control** (kill switch blocks execution)  
- observable status  

```bash
# 0) Health check
curl http://127.0.0.1:8080/health

# 1) Execute once
curl -X POST "http://127.0.0.1:8080/webhook" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d @examples/sample_webhook.json

# 2) Prove idempotency (send same event again -> duplicate)
curl -X POST "http://127.0.0.1:8080/webhook" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d @examples/sample_webhook.json

# 3) Prove operator control (kill switch -> reject)
curl -X POST "http://127.0.0.1:8080/admin/kill_switch?enabled=true"
curl -X POST "http://127.0.0.1:8080/webhook" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d @examples/sample_webhook.json

# 4) Status (mode + processed count)
curl http://127.0.0.1:8080/admin/status
```

---

## Key concepts demonstrated

- **Idempotency:** duplicate webhook deliveries do not cause duplicate execution  
- **Persistent state:** system behavior remains deterministic across restarts  
- **Guardrails:** centralized policy checks before any external side-effects  
- **Composable design:** connectors abstract external systems behind clean interfaces  
- **Operator controls:** health/status + kill switch for safe intervention  

---

## What’s intentionally omitted

To keep this public and safe, this repo excludes:
- real credentials or account identifiers  
- proprietary business logic / strategies  
- live integrations with external services  

The goal is to demonstrate the **execution layer patterns** used for production automation/agent systems.

---

## License
MIT
