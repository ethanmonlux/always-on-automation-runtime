from typing import Any, Dict
import time


class MockConnector:
    def execute(self, action: str, entity: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate work + return deterministic output
        time.sleep(0.05)
        return {
            "connector": "mock",
            "action": action,
            "entity": entity,
            "payload_keys": sorted(list(payload.keys())),
            "status": "ok",
        }
