from __future__ import annotations

from dataclasses import dataclass

from events.log import LoggedEvent
from hashing import stable_hash
from runtime import RuntimeErrorReason, RuntimeNode

from .message import RuntimeMessage


@dataclass(frozen=True)
class DeliveryRecord:
    delivery_index: int
    message: RuntimeMessage
    state_hash: str

    def canonical(self) -> dict[str, object]:
        return {
            "delivery_index": self.delivery_index,
            "message": self.message.canonical(),
            "state_hash": self.state_hash,
        }


@dataclass(frozen=True)
class CoordinationResult:
    deliveries: tuple[DeliveryRecord, ...]
    coordinated_state_hash: str


class DeterministicCoordinator:
    """Bounded, local-only message coordinator with no concurrent execution."""

    def __init__(self, node_ids: tuple[str, ...], max_messages: int = 32) -> None:
        if not 3 <= len(node_ids) <= 5:
            raise ValueError("node_ids must contain between 3 and 5 unique nodes")
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("node_ids must be unique")
        if max_messages <= 0:
            raise ValueError("max_messages must be positive")
        self.nodes = {node_id: RuntimeNode(node_id) for node_id in sorted(node_ids)}
        self.max_messages = max_messages
        self._queue: list[RuntimeMessage] = []
        self.delivery_history: list[DeliveryRecord] = []

    def enqueue(self, message: RuntimeMessage) -> None:
        if message.source_node_id not in self.nodes or message.target_node_id not in self.nodes:
            raise RuntimeErrorReason("message references an unknown node")
        if len(self._queue) >= self.max_messages:
            raise RuntimeErrorReason("message queue capacity exceeded")
        if message.message_id in {queued.message_id for queued in self._queue}:
            raise RuntimeErrorReason("duplicate message_id")
        self._queue.append(message)

    def deliver_all(self) -> CoordinationResult:
        if len(self._queue) > self.max_messages:
            raise RuntimeErrorReason("message queue capacity exceeded")
        for message in sorted(self._queue, key=RuntimeMessage.ordering_key):
            target = self.nodes[message.target_node_id]
            entry = LoggedEvent(sequence=len(target.execution_history) + 1, event=message.event())
            snapshot = target.accept(entry)
            self.delivery_history.append(
                DeliveryRecord(len(self.delivery_history) + 1, message, snapshot.state_hash)
            )
        self._queue.clear()
        return CoordinationResult(tuple(self.delivery_history), self.coordinated_state_hash())

    def coordinated_state_hash(self) -> str:
        return stable_hash({node_id: self.nodes[node_id].summary() for node_id in sorted(self.nodes)})
