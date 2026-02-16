# Always-On Automation Runtime (Sanitized Demo)

Built as a reliability-focused execution layer for continuously running automation systems and AI-assisted workflows.

## What this demonstrates (10-second version)

This demo shows the core reliability patterns used in a continuously running automation system:

- Always-on webhook ingestion with authentication + validation
- Idempotent execution (duplicate events never re-run)
- Persistent state for deterministic behavior across restarts
- Guardrails + kill-switch for safe autonomous operation
- Modular connector layer for external API execution
- Operator visibility via health + status endpoints


## Murphy Door fit (internal AI sandbox)

Murphy Door is building an internal AI sandbox to ship agents, copilots, RAG, and automation quickly **without** breaking operations.
This repo demonstrates the execution-layer patterns that make that possible:

- **Permissioned connectors** for CRM/ERP/MES/support tools (tool access is explicit and auditable)
- **Centralized policy + guardrails** (allowlists, approvals, rate limits, kill switch)
- **Deterministic state + idempotency** so retries and duplicate events never cause duplicate side-effects
- **Operator controls** (status, health, safe intervention) so non-technical teams can trust it

On top of this foundation, you add:

- **RAG knowledge layer** (document ingestion, embeddings + vector DB, retrieval policies)
- **Agent orchestration** (task routing, tool calling, human-in-the-loop for high-impact actions)

Most automation demos focus on making something work once. This focuses on making it safe and predictable in always-on environments where external systems fail or retry.

This repository is a **sanitized demonstration** of an automation runtime that ingests webhook events, enforces idempotency and guardrails, executes actions through modular connectors, and exposes operator controls.

It is designed to be a reusable backbone for API-driven automation where the hard part is not "making it work once" - it is making it safe, deterministic, and operable.

---

## What this is

A continuously running execution service designed for reliable autonomous workflows:

- Ingests structured webhook events (`POST /webhook`)
- Authenticates requests via an API key header
- Enforces idempotent processing using persistent state
- Applies guardrails (safe defaults / allowlist / payload sanity)
- Executes actions via a connector interface (mocked in this demo)
- Exposes operator endpoints for health/status and safe intervention

**Note:** This repo is intentionally sanitized. It contains no proprietary strategy logic, real credentials, or production integrations.

---

## Architecture (high level)
## Extending this to agents + RAG (production pattern)

To turn this runtime into an internal AI sandbox:

1) **Knowledge / RAG layer**
   - Ingest product docs, CAD/BOM metadata, SOPs, ticket history, and quoting rules
   - Chunk + embed into a vector store
   - Add retrieval policies so each copilot/agent only sees approved data

2) **Agent layer**
   - Use an orchestration framework (framework-agnostic: LangGraph, OpenClaw, etc.)
   - Route tasks to tools through the same connector interface (with guardrails)
   - Gate high-impact actions behind approvals + audit logs

3) **Evaluation + monitoring**
   - Golden sets for retrieval + prompt regression
   - Track latency/cost, failure rates, and “time saved” metrics



Signal Source  
-> Webhook ingestion (FastAPI)  
-> Validation + auth + idempotency  
-> Persistent state (SQLite in demo)  
-> Guardrails engine  
-> Execution layer (pluggable connectors)  
-> State + operator tooling (`/admin/status`, kill switch)

See `docs/architecture.md` for the full overview.

---

## Endpoints (demo)

- `GET /health` - liveness check
- `GET /admin/status` - system mode + processed count
- `POST /admin/kill_switch?enabled=true|false` - operator kill switch
- `POST /webhook` - ingest an event (idempotent + guardrails + execute)

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
- idempotency (duplicate event is not re-executed)
- operator control (kill switch blocks execution)
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

Note:
This demo persists processed events in a local SQLite file (state.sqlite).
If you want to re-run the sample with the same signal_id, either:
- delete state.sqlite, or
- change the signal_id in examples/sample_webhook.json

---

## Key concepts demonstrated

- **Idempotency:** duplicate webhook deliveries do not cause duplicate execution
- **Persistent state:** system behavior remains deterministic across restarts
- **Guardrails:** centralized policy checks before any external side-effects
- **Composable design:** connectors abstract external systems behind clean interfaces
- **Operator controls:** health/status + kill switch for safe intervention

---

## What is intentionally omitted

To keep this public and safe, this repo excludes:
- real credentials or account identifiers
- proprietary business logic or strategies
- live integrations with external services

The goal is to demonstrate execution-layer patterns used for reliable automation and agent-style systems.

---


## TL;DR for hiring managers

This is not a chatbot demo. It is a **reliable execution layer** for always-on automations and agent-style systems:

- Webhooks -> validation/auth -> idempotency -> persistent state -> guardrails -> connector execution
- Operator controls (status/health/kill switch) for safe production operation
- Designed to be extended with RAG + agent orchestration for real internal copilots

## License
MIT
