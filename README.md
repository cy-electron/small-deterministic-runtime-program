# Deterministic Runtime Simulation

Small Python implementation for the replay-safe deterministic runtime task.

It models one node, applies ordered events through an independent validation
layer, enforces runtime invariants, records immutable execution history, replays
the log, verifies every intermediate state hash, and shows deterministic failure
cases.

```powershell
python main.py
```

## Files

- `runtime/`: state model, transition rules, executor, errors, and serialization.
- `events/`: immutable event contract and append-only execution log.
- `replay/`: replay and replay-verification entry points.
- `validation/`: identity, sequence, duplicate, node, causal, transition, and invariant checks.
- `hashing/`: stable JSON/SHA-256 hashing helper.
- `stress.py`: deterministic valid and invalid execution scenarios.
- `main.py`: runs execution, replay, immutable-log proof, failure checks, and hash proof.
- `REVIEW_PACKET.md`: short explanation of the build.

No external packages are needed.
