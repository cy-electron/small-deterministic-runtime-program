from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable


class RuntimeErrorReason(ValueError):
    """Used when the event log cannot be applied safely."""


class NodeStatus(str, Enum):
    IDLE = "IDLE"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Action(str, Enum):
    START = "START"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


@dataclass(frozen=True)
class NodeState:
    node_id: str
    current_state: NodeStatus
    state_version: int
    event_counter: int

    @classmethod
    def initial(cls, node_id: str) -> "NodeState":
        return cls(
            node_id=node_id,
            current_state=NodeStatus.IDLE,
            state_version=0,
            event_counter=0,
        )

    def canonical(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "current_state": self.current_state.value,
            "state_version": self.state_version,
            "event_counter": self.event_counter,
        }

    def hash(self) -> str:
        return stable_hash(self.canonical())


@dataclass(frozen=True)
class ExecutionEvent:
    event_id: str
    node_id: str
    action: Action
    timestamp: int
    causal_id: int

    @classmethod
    def create(cls, node_id: str, action: Action | str, causal_id: int) -> "ExecutionEvent":
        action_value = Action(action)
        timestamp = deterministic_timestamp(causal_id)
        event_id = stable_hash(
            {
                "node_id": node_id,
                "action": action_value.value,
                "timestamp": timestamp,
                "causal_id": causal_id,
            }
        )
        return cls(
            event_id=event_id,
            node_id=node_id,
            action=action_value,
            timestamp=timestamp,
            causal_id=causal_id,
        )

    def canonical(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "node_id": self.node_id,
            "action": self.action.value,
            "timestamp": self.timestamp,
            "causal_id": self.causal_id,
        }


def deterministic_timestamp(causal_id: int) -> int:
    if causal_id <= 0:
        raise ValueError("causal_id must be positive")
    return 1_000_000 + causal_id


def stable_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def apply_event(event: ExecutionEvent, state: NodeState) -> NodeState:
    validate_event_identity(event)

    if event.node_id != state.node_id:
        raise RuntimeErrorReason(
            f"event node {event.node_id!r} does not match state node {state.node_id!r}"
        )

    expected_causal_id = state.event_counter + 1
    if event.causal_id < expected_causal_id:
        raise RuntimeErrorReason(
            f"duplicate causal_id {event.causal_id}; expected {expected_causal_id}"
        )
    if event.causal_id > expected_causal_id:
        raise RuntimeErrorReason(
            f"skipped causal sequence: received {event.causal_id}, expected {expected_causal_id}"
        )

    next_status = transition(state.current_state, event.action)
    return NodeState(
        node_id=state.node_id,
        current_state=next_status,
        state_version=state.state_version + 1,
        event_counter=event.causal_id,
    )


def validate_event_identity(event: ExecutionEvent) -> None:
    expected = ExecutionEvent.create(event.node_id, event.action, event.causal_id)
    if event.timestamp != expected.timestamp:
        raise RuntimeErrorReason(
            f"non-deterministic timestamp for causal_id {event.causal_id}"
        )
    if event.event_id != expected.event_id:
        raise RuntimeErrorReason(f"event_id mismatch for causal_id {event.causal_id}")


def transition(current: NodeStatus, action: Action) -> NodeStatus:
    allowed = {
        (NodeStatus.IDLE, Action.START): NodeStatus.PROCESSING,
        (NodeStatus.PROCESSING, Action.COMPLETE): NodeStatus.COMPLETED,
        (NodeStatus.PROCESSING, Action.FAIL): NodeStatus.FAILED,
    }
    try:
        return allowed[(current, action)]
    except KeyError as exc:
        raise RuntimeErrorReason(
            f"invalid transition: {current.value} + {action.value}"
        ) from exc


def execute_events(initial_state: NodeState, event_log: Iterable[ExecutionEvent]) -> NodeState:
    state = initial_state
    for event in event_log:
        state = apply_event(event, state)
    return state


def replay_events(event_log: Iterable[ExecutionEvent], node_id: str) -> NodeState:
    return execute_events(NodeState.initial(node_id), event_log)


def event_log_as_dicts(event_log: Iterable[ExecutionEvent]) -> list[dict[str, object]]:
    return [event.canonical() for event in event_log]


def state_as_dict(state: NodeState) -> dict[str, object]:
    data = asdict(state)
    data["current_state"] = state.current_state.value
    return data
