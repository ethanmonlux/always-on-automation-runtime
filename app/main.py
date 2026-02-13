from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Optional

import os

from .state_store import StateStore
from .connectors.mock_connector import MockConnector

app = FastAPI(title="Always-On Automation Runtime (Sanitized Demo)")

@app.get("/health")
def health():
    return {"ok": True}


store = StateStore("state.sqlite")
connector = MockConnector()
from .guardrails import should_execute

API_KEY = os.getenv("API_KEY", "demo-key")  # overridden via .env in real systems


class WebhookEvent(BaseModel):
    signal_id: str = Field(..., description="Idempotency key")
    source: str
    action: str
    entity: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    event_time: datetime


@app.get("/admin/status")
def status():
    return {
        "ok": True,
        "mode": store.get_mode(),
        "processed_count": store.count_processed(),
    }


@app.post("/admin/kill_switch")
def kill_switch(enabled: bool):
    store.set_mode("blocked" if enabled else "enabled")
    return {"ok": True, "mode": store.get_mode()}


@app.post("/webhook")
def webhook(evt: WebhookEvent, x_api_key: str = Header(..., alias="X-API-Key")):
    # Basic auth gate (demo)
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Kill switch / operator control
    if store.get_mode() != "enabled":
        return {"ok": True, "status": "rejected", "reason": "kill_switch_enabled"}


    # Guardrails (demo): keep execution deterministic and safe
    decision = should_execute(
        mode=store.get_mode(),
        action=evt.action,
        entity=evt.entity,
        payload=evt.payload,
        allowlist={
            "lead": ("create_task", "enrich"),
            "doc": ("write", "summarize"),
            "system": ("ping",),
        },
    )
    if not decision.allowed:
        return {"ok": True, "status": "rejected", "reason": decision.reason, "details": decision.details}

    # Idempotency
    if store.seen(evt.signal_id):
        return {"ok": True, "status": "duplicate", "signal_id": evt.signal_id}

    store.mark_seen(evt.signal_id)

    # Guardrail example: require action/entity to be present (already validated by schema)
    # Execute through modular connector (mock)
    result = connector.execute(action=evt.action, entity=evt.entity, payload=evt.payload)

    return {"ok": True, "status": "executed", "signal_id": evt.signal_id, "result": result}
