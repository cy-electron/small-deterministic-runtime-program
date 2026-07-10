# Deterministic Runtime Simulation

This is a small Python project that shows a replay-safe runtime core.

A Python implementation of a replay-safe deterministic runtime core demonstrating
immutable execution logs, deterministic event processing, runtime validation,
state hashing, and replay verification.

this is the updated program (version v2 as per the task) of small-deterministic-runtime-program

Run it with:

```powershell
python main.py
```

No external packages are needed.

## What It Shows

- Events are immutable after they are created.
- The execution log only allows appending.
- Every logged event gets a deterministic sequence number.
- Invalid events stop execution before state changes.
- Replay checks every intermediate state hash, not only the final state.
- Stress cases are deterministic and repeatable.

## Project Layout

- `main.py`: runs the demo and prints the proof output.
- `events/`: event objects and the append-only execution log.
- `runtime/`: node state, transitions, execution, and serialization helpers.
- `validation/`: pre-execution checks and runtime invariant checks.
- `replay/`: replay and replay verification logic.
- `hashing/`: stable SHA-256 hashing for canonical state data.
- `stress.py`: valid and invalid deterministic stress scenarios.
- `review_packets/`: review notes and evidence for submission.

## Runtime Flow

```
Incoming Event
      │
      ▼
 Validation
      │
      ▼
 Execution
      │
      ▼
 Immutable Event Log
      │
      ▼
 State Hash
      │
      ▼
 Replay Verification
```


## Current Scope

This project is intentionally local and simple. It does not include networking,
databases, APIs, consensus, or distributed runtime behavior. The goal is to keep
the runtime easy to inspect and easy to replay.
