from __future__ import annotations

from events import ExecutionEvent, ExecutionLog
from coordination import verify_coordination_replay
from observability import build_replay_evidence, export_replay_evidence
from replay import replay_events, replay_verified
from runtime import Action, NodeState, RuntimeErrorReason
from runtime.executor import ExecutionSnapshot, execute_with_trace
from runtime.serialization import event_log_as_dicts, state_as_dict
from stress import run_stress_validation


NODE_ID = "quantum-runtime-node-01"


def build_valid_event_log() -> ExecutionLog:
    log = ExecutionLog()
    log.append(ExecutionEvent.create(NODE_ID, Action.START, 1))
    log.append(ExecutionEvent.create(NODE_ID, Action.COMPLETE, 2))
    log.seal()
    return log


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def print_mapping(mapping: dict[str, object]) -> None:
    for key, value in mapping.items():
        print(f"{key}: {value}")


def run_original_execution(
    event_log: ExecutionLog,
) -> tuple[NodeState, tuple[ExecutionSnapshot, ...]]:
    print_section("Original Execution")
    state, trace = execute_with_trace(NodeState.initial(NODE_ID), event_log.entries())
    print_mapping(state_as_dict(state))
    print(f"state_hash: {state.hash()}")
    for snapshot in trace:
        print(f"trace_{snapshot.sequence}_hash: {snapshot.state_hash}")
    return state, trace


def run_replay(
    event_log: ExecutionLog,
    original_hash: str,
    original_trace: tuple[ExecutionSnapshot, ...],
) -> NodeState:
    print_section("Replay Proof")
    replayed = replay_verified(event_log.entries(), NODE_ID, original_trace)
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
        ExecutionEvent.create(NODE_ID, Action.FAIL, 3),
    ]
    invalid_node = [
        ExecutionEvent.create("unexpected-runtime-node", Action.START, 1),
    ]

    run_divergence_case("duplicate event", duplicate)
    run_divergence_case("out-of-order event", out_of_order)
    run_divergence_case("missing event", missing)
    run_divergence_case("invalid node", invalid_node)


def run_replay_mismatch_case(
    event_log: ExecutionLog,
    original_trace: tuple[ExecutionSnapshot, ...],
) -> None:
    print_section("Replay Verification Mismatch")
    bad_trace = (
        ExecutionSnapshot(
            sequence=original_trace[0].sequence,
            event_id=original_trace[0].event_id,
            state_hash="0" * 64,
            state=original_trace[0].state,
        ),
        *original_trace[1:],
    )
    try:
        replay_verified(event_log.entries(), NODE_ID, bad_trace)
    except RuntimeErrorReason as exc:
        print("halted: True")
        print(f"reason: {exc}")
        return
    print("halted: False")
    print("reason: replay mismatch was not detected")


def run_determinism_proof(event_log: ExecutionLog) -> None:
    print_section("Determinism Proof")
    hashes = [replay_events(event_log.entries(), NODE_ID).hash() for _ in range(5)]
    for index, hash_value in enumerate(hashes, start=1):
        print(f"run_{index}_hash: {hash_value}")
    print(f"all_hashes_identical: {len(set(hashes)) == 1}")


def run_stress_proof() -> None:
    print_section("Deterministic Stress Validation")
    results = run_stress_validation()
    valid_results = [result for result in results if result["valid"] is True]
    invalid_results = [result for result in results if result["valid"] is False]
    invalid_halts = sum(1 for result in invalid_results if result["halted"] is True)

    print(f"valid_executions: {len(valid_results)}")
    print(f"invalid_executions: {len(invalid_results)}")
    print(f"invalid_halts: {invalid_halts}")

    for result in results:
        print(result)


def run_coordination_observability() -> None:
    print_section("Coordinated Runtime Audit")
    verification = verify_coordination_replay()
    evidence = build_replay_evidence(verification)
    for record in evidence["execution_timeline"]:
        print(record)
    print(f"coordinated_state_hash: {verification.result.coordinated_state_hash}")
    print(f"coordination_replay_verified: {verification.replay_verified}")
    output_path = export_replay_evidence(verification, "artifacts/replay_evidence.json")
    print(f"replay_evidence_json: {output_path}")


def main() -> int:
    event_log = build_valid_event_log()

    print_section("Deterministic Event Log")
    for event in event_log_as_dicts(event_log):
        print(event)

    run_immutable_log_proof(event_log)
    final_state, original_trace = run_original_execution(event_log)
    run_replay(event_log, final_state.hash(), original_trace)
    run_replay_mismatch_case(event_log, original_trace)
    run_divergence_tests(event_log)
    run_determinism_proof(event_log)
    run_coordination_observability()
    run_stress_proof()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
