from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from events.event import ExecutionEvent
from events.log import LoggedEvent
from runtime.state import NodeState
from runtime.transitions import transition
from validation import (
    RuntimeInvariantContext,
    RuntimeValidationContext,
    validate_before_execution,
    validate_invariants,
)


@dataclass(frozen=True)
class ExecutionSnapshot:
    sequence: int
    event_id: str
    state_hash: str
    state: NodeState


def apply_event(event: ExecutionEvent, state: NodeState) -> NodeState:
    next_status = transition(state.current_state, event.action)
    return NodeState(
        node_id=state.node_id,
        current_state=next_status,
        state_version=state.state_version + 1,
        event_counter=event.causal_id,
    )


def execute_events(
    initial_state: NodeState,
    event_log: Iterable[ExecutionEvent | LoggedEvent],
) -> NodeState:
    return execute_with_trace(initial_state, event_log)[0]


def execute_with_trace(
    initial_state: NodeState,
    event_log: Iterable[ExecutionEvent | LoggedEvent],
) -> tuple[NodeState, tuple[ExecutionSnapshot, ...]]:
    state = initial_state
    snapshots: list[ExecutionSnapshot] = []
    validation_context = RuntimeValidationContext()
    invariant_context = RuntimeInvariantContext()

    for item in event_log:
        previous_state = state
        event = validate_before_execution(item, state, validation_context)
        state = apply_event(event, state)
        sequence = (
            item.sequence
            if isinstance(item, LoggedEvent)
            else validation_context.expected_sequence - 1
        )
        validate_invariants(previous_state, state, event, sequence, invariant_context)
        snapshots.append(
            ExecutionSnapshot(
                sequence=sequence,
                event_id=event.event_id,
                state_hash=state.hash(),
                state=state,
            )
        )
    return state, tuple(snapshots)
