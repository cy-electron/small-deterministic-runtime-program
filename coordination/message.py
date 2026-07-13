from __future__ import annotations

from dataclasses import dataclass

from events import ExecutionEvent
from hashing import stable_hash
from runtime import Action


@dataclass(frozen=True)
class RuntimeMessage:
    """Immutable local message delivered in a canonical total order."""

    message_id: str
    source_node_id: str
    target_node_id: str
    action: Action
    causal_id: int
    logical_clock: int

    @classmethod
    def create(
        cls,
        source_node_id: str,
        target_node_id: str,
        action: Action | str,
        causal_id: int,
        logical_clock: int,
    ) -> "RuntimeMessage":
        action_value = Action(action)
        identifier_data = {
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "action": action_value.value,
            "causal_id": causal_id,
            "logical_clock": logical_clock,
        }
        return cls(
            message_id=stable_hash(identifier_data),
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            action=action_value,
            causal_id=causal_id,
            logical_clock=logical_clock,
        )

    def ordering_key(self) -> tuple[int, str, str, str]:
        return (self.logical_clock, self.source_node_id, self.target_node_id, self.message_id)

    def canonical(self) -> dict[str, object]:
        return {
            "message_id": self.message_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "action": self.action.value,
            "causal_id": self.causal_id,
            "logical_clock": self.logical_clock,
        }

    def event(self) -> ExecutionEvent:
        return ExecutionEvent.create(self.target_node_id, self.action, self.causal_id)
