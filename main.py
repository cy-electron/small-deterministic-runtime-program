from __future__ import annotations

<<<<<<< HEAD
from events import ExecutionEvent, ExecutionLog
from replay import replay_events
from runtime import Action, NodeState, RuntimeErrorReason
from runtime.executor import execute_events
from runtime.serialization import event_log_as_dicts, state_as_dict
=======
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
>>>>>>> 40bdd748e88a6aa251e04db1024868d220fa9a94


NODE_ID = "quantum-runtime-node-01"


<<<<<<< HEAD
def build_valid_event_log() -> ExecutionLog:
    log = ExecutionLog()
    log.append(ExecutionEvent.create(NODE_ID, Action.START, 1))
    log.append(ExecutionEvent.create(NODE_ID, Action.COMPLETE, 2))
    log.seal()
    return log
=======
def build_valid_event_log() -> list[ExecutionEvent]:
    return [
        ExecutionEvent.create(NODE_ID, Action.START, 1),
        ExecutionEvent.create(NODE_ID, Action.COMPLETE, 2),
    ]
>>>>>>> 40bdd748e88a6aa251e04db1024868d220fa9a94


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def print_mapping(mapping: dict[str, object]) -> None:
    for key, value in mapping.items():
        print(f"{key}: {value}")


<<<<<<< HEAD
def run_original_execution(event_log: ExecutionLog) -> NodeState:
    print_section("Original Execution")
    state = execute_events(NodeState.initial(NODE_ID), event_log.events())
=======
def run_original_execution(event_log: list[ExecutionEvent]) -> NodeState:
    print_section("Original Execution")
    state = execute_events(NodeState.initial(NODE_ID), event_log)
>>>>>>> 40bdd748e88a6aa251e04db1024868d220fa9a94
    print_mapping(state_as_dict(state))
    print(f"state_hash: {state.hash()}")
    return state


<<<<<<< HEAD
def run_replay(event_log: ExecutionLog | list[ExecutionEvent], original_hash: str) -> NodeState:
    print_section("Replay Proof")
    events = event_log.events() if isinstance(event_log, ExecutionLog) else event_log
    replayed = replay_events(events, NODE_ID)
=======
def run_replay(event_log: list[ExecutionEvent], original_hash: str) -> NodeState:
    print_section("Replay Proof")
    replayed = replay_events(event_log, NODE_ID)
>>>>>>> 40bdd748e88a6aa251e04db1024868d220fa9a94
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


<<<<<<< HEAD
def run_immutable_log_proof(event_log: ExecutionLog) -> None:
    print_section("Immutable Log Proof")
    try:
        event_log.append(ExecutionEvent.create(NODE_ID, Action.FAIL, 3))
    except RuntimeErrorReason as exc:
        print("post_seal_append_blocked: True")
        print(f"reason: {exc}")

    first_entry = event_log.entries()[0]
    try:
        first_entry.event.causal_id = 99
    except AttributeError as exc:
        print("event_mutation_blocked: True")
        print(f"reason: {exc}")
    print(f"log_length_after_attempts: {len(event_log)}")


def run_divergence_tests(valid_log: ExecutionLog) -> None:
    valid_events = list(valid_log.events())
    duplicate = [valid_events[0], valid_events[0]]
    out_of_order = [valid_events[1], valid_events[0]]
    missing = [
        valid_events[0],
=======
def run_divergence_tests(valid_log: list[ExecutionEvent]) -> None:
    duplicate = [valid_log[0], valid_log[0]]
    out_of_order = [valid_log[1], valid_log[0]]
    missing = [
        valid_log[0],
>>>>>>> 40bdd748e88a6aa251e04db1024868d220fa9a94
        ExecutionEvent.create(NODE_ID, Action.FAIL, 3),
    ]

    run_divergence_case("duplicate event", duplicate)
    run_divergence_case("out-of-order event", out_of_order)
    run_divergence_case("missing event", missing)


<<<<<<< HEAD
def run_determinism_proof(event_log: ExecutionLog) -> None:
    print_section("Determinism Proof")
    hashes = [replay_events(event_log.events(), NODE_ID).hash() for _ in range(5)]
=======
def run_determinism_proof(event_log: list[ExecutionEvent]) -> None:
    print_section("Determinism Proof")
    hashes = [replay_events(event_log, NODE_ID).hash() for _ in range(5)]
>>>>>>> 40bdd748e88a6aa251e04db1024868d220fa9a94
    for index, hash_value in enumerate(hashes, start=1):
        print(f"run_{index}_hash: {hash_value}")
    print(f"all_hashes_identical: {len(set(hashes)) == 1}")


def main() -> int:
    event_log = build_valid_event_log()

    print_section("Deterministic Event Log")
    for event in event_log_as_dicts(event_log):
        print(event)

<<<<<<< HEAD
    run_immutable_log_proof(event_log)
=======
>>>>>>> 40bdd748e88a6aa251e04db1024868d220fa9a94
    final_state = run_original_execution(event_log)
    run_replay(event_log, final_state.hash())
    run_divergence_tests(event_log)
    run_determinism_proof(event_log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
