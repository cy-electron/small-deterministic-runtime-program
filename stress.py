from __future__ import annotations

from dataclasses import replace

from events import ExecutionEvent, ExecutionLog
from replay import replay_events, replay_verified
from runtime import Action, NodeState, RuntimeErrorReason
from runtime.executor import ExecutionSnapshot, execute_with_trace


def build_valid_stress_logs() -> list[tuple[str, ExecutionLog]]:
    logs: list[tuple[str, ExecutionLog]] = []
    for index in range(1, 11):
        node_id = f"stress-valid-node-{index:02d}"
        final_action = Action.COMPLETE if index % 2 else Action.FAIL
        log = ExecutionLog()
        log.append(ExecutionEvent.create(node_id, Action.START, 1))
        log.append(ExecutionEvent.create(node_id, final_action, 2))
        log.seal()
        logs.append((node_id, log))
    return logs


def build_invalid_stress_cases() -> list[tuple[str, str, list[ExecutionEvent]]]:
    base = "stress-invalid-node"
    valid_start = ExecutionEvent.create(base, Action.START, 1)
    valid_complete = ExecutionEvent.create(base, Action.COMPLETE, 2)
    tampered_timestamp = replace(valid_start, timestamp=42)
    tampered_event_id = replace(valid_start, event_id="bad-event-id")

    return [
        ("duplicate_event", base, [valid_start, valid_start]),
        ("duplicate_causal_id", base, [valid_start, ExecutionEvent.create(base, Action.COMPLETE, 1)]),
        ("ordering_failure", base, [valid_complete, valid_start]),
        ("illegal_transition", base, [ExecutionEvent.create(base, Action.COMPLETE, 1)]),
        ("invalid_node", base, [ExecutionEvent.create("wrong-node", Action.START, 1)]),
        ("missing_event", base, [valid_start, ExecutionEvent.create(base, Action.FAIL, 3)]),
        ("timestamp_tamper", base, [tampered_timestamp]),
        ("event_id_tamper", base, [tampered_event_id]),
        ("terminal_reentry", base, [valid_start, valid_complete, ExecutionEvent.create(base, Action.START, 3)]),
        ("terminal_failover", base, [valid_start, ExecutionEvent.create(base, Action.FAIL, 2), ExecutionEvent.create(base, Action.COMPLETE, 3)]),
    ]


def run_stress_validation() -> list[dict[str, object]]:
    results: list[dict[str, object]] = []

    for node_id, log in build_valid_stress_logs():
        state = replay_events(log.entries(), node_id)
        results.append(
            {
                "case": node_id,
                "valid": True,
                "final_state": state.current_state.value,
                "hash": state.hash(),
            }
        )

    for name, node_id, events in build_invalid_stress_cases():
        try:
            replay_events(events, node_id)
        except RuntimeErrorReason as exc:
            results.append(
                {
                    "case": name,
                    "valid": False,
                    "halted": True,
                    "reason": str(exc),
                }
            )
        else:
            results.append(
                {
                    "case": name,
                    "valid": False,
                    "halted": False,
                    "reason": "invalid execution was accepted",
                }
            )

    results.append(run_replay_mismatch_stress_case())
    return results


def run_replay_mismatch_stress_case() -> dict[str, object]:
    node_id = "stress-replay-mismatch-node"
    log = ExecutionLog()
    log.append(ExecutionEvent.create(node_id, Action.START, 1))
    log.append(ExecutionEvent.create(node_id, Action.COMPLETE, 2))
    log.seal()

    _, trace = execute_with_trace(NodeState.initial(node_id), log.entries())
    bad_trace = (
        ExecutionSnapshot(
            sequence=trace[0].sequence,
            event_id=trace[0].event_id,
            state_hash="f" * 64,
            state=trace[0].state,
        ),
        *trace[1:],
    )
    try:
        replay_verified(log.entries(), node_id, bad_trace)
    except RuntimeErrorReason as exc:
        return {
            "case": "replay_mismatch",
            "valid": False,
            "halted": True,
            "reason": str(exc),
        }
    return {
        "case": "replay_mismatch",
        "valid": False,
        "halted": False,
        "reason": "replay mismatch was accepted",
    }
