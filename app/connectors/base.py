from typing import Any, Dict, Protocol


class Connector(Protocol):
    def execute(self, action: str, entity: str, payload: Dict[str, Any]) -> Dict[str, Any]:
