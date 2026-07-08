# REVIEW_PACKET

## 1. Entry Point

Run:

```powershell
python main.py
```

The script builds a deterministic event log, executes it, replays it, tests
divergence cases, and prints the five-run determinism proof.

## 2. Core Flow

1. `NodeState.initial()` creates a node with `IDLE`, version `0`, and event
   counter `0`.
2. `ExecutionEvent.create()` creates events from deterministic inputs only.
3. `apply_event()` checks event identity, node ownership, causal sequence, and
   transition validity.
4. `execute_events()` applies the ordered log.
5. `replay_events()` rebuilds final state from the same immutable event log.
6. State hashes are generated from canonical JSON with sorted keys.

## 3. Real Execution Example

The valid execution is:

1. `START` with `causal_id = 1`: `IDLE -> PROCESSING`.
2. `COMPLETE` with `causal_id = 2`: `PROCESSING -> COMPLETED`.

The original execution hash and replay hash must match exactly.

## 4. Failure Cases

The script simulates and safely halts on:

- Duplicate event: the same `causal_id` is seen twice.
- Out-of-order event: causal sequence starts at `2` before `1`.
- Missing event: causal sequence jumps from `1` to `3`.

Each failure prints a readable reason. No failure is silent.

## 5. Determinism Proof

The script replays the same event log five times. Every run must produce the
same final hash. If any hash differs, `all_hashes_identical` prints `False`.

## 6. What Was Built

A small deterministic runtime coordination model with:

- Node state model.
- Deterministic event contract.
- Causal ordering enforcement.
- Transition validation.
- Replay engine.
- Divergence detection.
- Deterministic hash proof.

## 7. System Boundaries

This is not a quantum computer, network simulator, consensus implementation,
database, API, UI, async runtime, or AI system. It is intentionally local,
bounded, inspectable, and deterministic.

## 8. Known Limitations

- Single-node execution only.
- In-memory event log only.
- No persistence layer.
- No distributed transport.
- No recovery protocol beyond replay.
- Minimal transition graph by design: `IDLE`, `PROCESSING`, `COMPLETED`,
  `FAILED`.
