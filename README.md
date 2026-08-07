# Always-On Automation Runtime

A sanitized reference implementation of the reliability patterns behind a continuously running production automation system.

Most automation demos prove that a workflow can succeed once.

This repository focuses on the harder problem: making execution predictable when requests are duplicated, dependencies fail, processes restart, or an operator needs to intervene.

The production system this is derived from executes real external workflows. Proprietary domain logic and integrations are intentionally excluded here.

---

## What this demonstrates

- Authenticated webhook ingestion
- Payload validation
- Idempotent execution
- Durable state across restarts
- Fail-closed guardrails
- Pluggable external connectors
- Operator kill switch and mode controls
- Explicit failure handling
- Local execution without production dependencies

The demo is intentionally small enough to inspect end to end.

---

## Architecture

```text
External Signal
      |
      v
FastAPI Webhook
      |
      v
Authentication
      |
      v
Validation + Idempotency
      |
      v
Guardrails
      |
      v
Execution Connector
      |
      v
State Update
```

Supporting state and operator controls sit alongside the execution path:

```text
SQLite / Persistent State
Admin Status API
Kill Switch
Runtime Mode
```

The production implementation uses the same architectural boundaries with additional monitoring, retry, reconciliation, and external integration behavior.

---

## Reliability principles

### Idempotency by default

Every event has a stable identifier.

Once an event has executed, delivering it again does not execute it twice.

```text
first delivery  -> execute
second delivery -> duplicate / no-op
```

### Durable state

Execution history is persisted outside the application process.

Restarting the server does not erase completed work or make previously processed signals eligible to execute again.

The demo uses SQLite. The production system uses PostgreSQL.

### Fail-closed guardrails

Execution passes through explicit validation before reaching a connector.

Examples include:

- authentication
- payload validation
- allowlists
- duplicate detection
- operator kill switch

Invalid or ambiguous state stops execution rather than allowing it to continue implicitly.

### Pluggable connectors

External systems are accessed through a connector interface.

The core execution flow does not depend on a specific third-party API.

This makes it possible to use mock connectors in tests, sandbox or staging connectors, and production integrations without rewriting execution logic.

### Operator control

The runtime exposes a small administrative surface:

- current system status
- current operating mode
- processed-event count
- emergency kill switch

Operators do not need to modify server configuration to stop new execution.

---

## What exists in the production system

This repository is deliberately sanitized.

The larger production system adds several layers that are omitted here.

### Layered safety gates

Execution passes through ordered checks covering:

- authentication
- system health
- payload integrity
- idempotency
- stale-event detection
- operator mode
- degraded mode
- circuit-breaker state
- configurable risk constraints

Each gate returns a structured decision rather than silently allowing execution to fall through.

### Retry and recovery

Transient failures use a durable retry queue with bounded exponential backoff.

Permanent failures stop rather than retry indefinitely.

Retry state survives process restarts.

### External integrations

Production connectors include authenticated third-party APIs and token lifecycle management.

External integrations remain isolated behind protocol-style interfaces.

### Monitoring and reconciliation

Background workers handle monitoring, cleanup, retry processing, reconciliation, snapshots, and scheduled operational checks.

### Operator surface

The production system includes a web dashboard and REST administrative API for monitoring and bounded intervention.

### LLM integration

Claude is used for non-critical operational summaries and anomaly explanations.

LLM output never authorizes or performs execution.

If the model provider fails, the automation system continues operating.

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/admin/status` | Runtime mode and processed-event state |
| `POST` | `/admin/kill_switch?enabled=true\|false` | Enable or disable new execution |
| `POST` | `/webhook` | Ingest and process an event |

---

## Run locally

### macOS / Linux

```bash
bash run_local.sh
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

$env:API_KEY="demo-key"

uvicorn app.main:app --reload --port 8080
```

---

## Try the failure behavior

### Health check

```bash
curl http://127.0.0.1:8080/health
```

### Execute an event

```bash
curl -X POST http://127.0.0.1:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  --data-binary "@examples/sample_webhook.json"
```

### Send the same event again

```bash
curl -X POST http://127.0.0.1:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  --data-binary "@examples/sample_webhook.json"
```

The second request is recognized as a duplicate and does not execute again.

### Enable the kill switch

```bash
curl -X POST \
  "http://127.0.0.1:8080/admin/kill_switch?enabled=true"
```

Then submit another event.

New execution is blocked until the operator disables the kill switch.

---

## Why this exists

Automation becomes much more interesting once it can affect a real external system.

At that point, the important questions change from:

> Can the workflow run?

To:

> What happens if the request arrives twice?
>
> What survives a restart?
>
> What happens when an API fails halfway through?
>
> Can an operator stop it safely?
>
> Can someone determine afterward what happened and why?

This repository is a compact implementation of those concerns.

It is not intended to reproduce the proprietary production system.

It is intended to make its reliability model inspectable.
