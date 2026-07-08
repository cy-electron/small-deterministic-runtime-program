from __future__ import annotations

from runtime import (
    Action,
    ExecutionEvent,
    NodeState,
    RuntimeErrorReason,
    event_log_as_dicts,
    execute_events,
    replay_events,
    state_as_dict,
)


NODE_ID = "quantum-runtime-node-01"


def build_valid_event_log() -> list[ExecutionEvent]:
    return [
        ExecutionEvent.create(NODE_ID, Action.START, 1),
        ExecutionEvent.create(NODE_ID, Action.COMPLETE, 2),
    ]


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def print_mapping(mapping: dict[str, object]) -> None:
    for key, value in mapping.items():
        print(f"{key}: {value}")


def run_original_execution(event_log: list[ExecutionEvent]) -> NodeState:
    print_section("Original Execution")
    state = execute_events(NodeState.initial(NODE_ID), event_log)
    print_mapping(state_as_dict(state))
    print(f"state_hash: {state.hash()}")
    return state


def run_replay(event_log: list[ExecutionEvent], original_hash: str) -> NodeState:
    print_section("Replay Proof")
    replayed = replay_events(event_log, NODE_ID)
    print_mapping(state_as_dict(replayed))
    print(f"replay_hash: {replayed.hash()}")
    print(f"matches_original: {replayed.hash() == original_hash}")
    return replayed


def run_divergence_case(name: str, event_log: list[ExecutionEvent]) -> None:
    print_section(f"Divergence Case: {name}")
    try:
        replay_events(event_log, NODE_ID)
    except RuntimeErrorReason as exc:
        print("halted: True")
        print(f"reason: {exc}")
        return
    print("halted: False")
    print("reason: divergence was not detected")


def run_divergence_tests(valid_log: list[ExecutionEvent]) -> None:
    duplicate = [valid_log[0], valid_log[0]]
    out_of_order = [valid_log[1], valid_log[0]]
    missing = [
        valid_log[0],
        ExecutionEvent.create(NODE_ID, Action.FAIL, 3),
    ]

    run_divergence_case("duplicate event", duplicate)
    run_divergence_case("out-of-order event", out_of_order)
    run_divergence_case("missing event", missing)


def run_determinism_proof(event_log: list[ExecutionEvent]) -> None:
    print_section("Determinism Proof")
    hashes = [replay_events(event_log, NODE_ID).hash() for _ in range(5)]
    for index, hash_value in enumerate(hashes, start=1):
        print(f"run_{index}_hash: {hash_value}")
    print(f"all_hashes_identical: {len(set(hashes)) == 1}")


def main() -> int:
    event_log = build_valid_event_log()

    print_section("Deterministic Event Log")
    for event in event_log_as_dicts(event_log):
        print(event)

    final_state = run_original_execution(event_log)
    run_replay(event_log, final_state.hash())
    run_divergence_tests(event_log)
    run_determinism_proof(event_log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
