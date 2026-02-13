# Always-On Automation Runtime (Sanitized Demo)

A small, production-style **execution layer** demo: accepts authenticated webhook events, validates + de-dupes them (idempotency), persists state, and calls a pluggable connector (stub by default).

## Quick start (local)

### 1) Create a virtualenv + install deps
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Set an API key for the webhook
```bash
export API_KEY="demo-key"  # Windows PowerShell: $env:API_KEY="demo-key"
```

### 3) Run the server
```bash
uvicorn app.main:app --reload --port 8080
```

### 4) Send a test webhook
```bash
curl -X POST "http://127.0.0.1:8080/webhook" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{"signal_id":"demo-1","source":"demo","action":"ping","entity":"system","event_time":"2026-01-01T00:00:00Z","payload":{"hello":"world"}}'
```

## Notes
- State is stored in `state.sqlite` (ignored by git via `.gitignore`).
- The connector layer is designed to be swapped for real integrations.
- See `docs/architecture.md` for the architecture overview.
