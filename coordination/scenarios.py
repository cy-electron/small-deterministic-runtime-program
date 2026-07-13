from __future__ import annotations

from dataclasses import dataclass

from runtime import Action, RuntimeErrorReason

from .coordinator import CoordinationResult, DeterministicCoordinator
from .message import RuntimeMessage


DEMO_NODE_IDS = ("node-alpha", "node-bravo", "node-charlie", "node-delta")


@dataclass(frozen=True)
class CoordinationVerification:
    result: CoordinationResult
    replay_verified: bool
    node_replay_hashes: dict[str, str]
    node_summaries: dict[str, dict[str, object]]


def build_demo_messages() -> tuple[RuntimeMessage, ...]:
    """A deliberately unsorted node-to-node ring; delivery order is canonical."""
    return (
        RuntimeMessage.create("node-alpha", "node-bravo", Action.START, 1, 4),
        RuntimeMessage.create("node-bravo", "node-charlie", Action.START, 1, 1),
        RuntimeMessage.create("node-charlie", "node-delta", Action.START, 1, 3),
        RuntimeMessage.create("node-delta", "node-alpha", Action.START, 1, 2),
    )


def execute_coordination(
    messages: tuple[RuntimeMessage, ...] = build_demo_messages(),
) -> tuple[DeterministicCoordinator, CoordinationResult]:
    coordinator = DeterministicCoordinator(DEMO_NODE_IDS, max_messages=8)
    for message in messages:
        coordinator.enqueue(message)
    return coordinator, coordinator.deliver_all()


def verify_coordination_replay(
    messages: tuple[RuntimeMessage, ...] = build_demo_messages(),
) -> CoordinationVerification:
    coordinator, original = execute_coordination(messages)
    replay_coordinator, replayed = execute_coordination(tuple(reversed(messages)))

    original_records = tuple(record.canonical() for record in original.deliveries)
    replay_records = tuple(record.canonical() for record in replayed.deliveries)
    if original_records != replay_records:
        raise RuntimeErrorReason("coordination replay delivery history mismatch")
    if original.coordinated_state_hash != replayed.coordinated_state_hash:
        raise RuntimeErrorReason("coordination replay state hash mismatch")

    node_replay_hashes: dict[str, str] = {}
    for node_id, node in coordinator.nodes.items():
        replayed_node = node.replay()
        if replayed_node.hash() != node.state_hash:
            raise RuntimeErrorReason(f"node replay state mismatch for {node_id}")
        node_replay_hashes[node_id] = replayed_node.hash()

    # Exercise the second independent reconstruction as well.
    for node in replay_coordinator.nodes.values():
        node.replay()

    return CoordinationVerification(
        original,
        True,
        node_replay_hashes,
        {node_id: node.summary() for node_id, node in coordinator.nodes.items()},
    )
