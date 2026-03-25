"""Guardrails for safe, deterministic execution (sanitized demo).

This module centralizes operator controls and simple policy checks.
In a production system, you'd expand this with richer policy, rate limits,
audit logging, and environment-specific rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    reason: str
    details: Dict[str, Any]


def should_execute(
    *,
    mode: str,
    action: str,
    entity: str,
    payload: Dict[str, Any],
    allowlist: Optional[Dict[str, Tuple[str, ...]]] = None,
) -> GuardrailDecision:
    """Return whether execution is allowed given current operator mode and basic rules.

    Parameters
    ----------
    mode:
        Operator mode string, e.g. "enabled" or "blocked".
    action/entity/payload:
        Event fields (already schema-validated in main).
    allowlist:
        Optional map of entity -> allowed actions. Example:
            {"lead": ("create_task", "enrich"), "doc": ("write",)}
        If provided, actions not in the allowlist are rejected.
    """
    # 1) Global kill switch / safe mode
    if mode != "enabled":
        return GuardrailDecision(
            allowed=False,
            reason="kill_switch_enabled",
            details={"mode": mode},
        )

    # 2) Optional allowlist policy (keeps demo deterministic and safe)
    if allowlist is not None:
        allowed_actions = allowlist.get(entity)
        if allowed_actions is None or action not in allowed_actions:
            return GuardrailDecision(
                allowed=False,
                reason="action_not_allowed",
                details={"entity": entity, "action": action, "allowed": list(allowed_actions or ())},
            )

    # 3) Example content-size guardrail (avoid huge payloads)
    #    NOTE: this is a demo heuristic; production would use request size limits at the server layer.
    if len(str(payload)) > 50_000:
        return GuardrailDecision(
            allowed=False,
            reason="payload_too_large",
            details={"approx_chars": len(str(payload))},
        )

    return GuardrailDecision(
        allowed=True,
        reason="ok",
        details={},
    )
