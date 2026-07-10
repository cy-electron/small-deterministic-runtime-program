<<<<<<< HEAD
# Deterministic Runtime Simulation

Small Python implementation for the replay-safe deterministic runtime task.

It models one node, applies ordered events, records immutable execution history,
replays the log, checks the final state hash, and shows divergence cases.
=======
# small-deterministic-runtime-program (simulator)
this a simple deterministic runtime simulator, its show working a (runtime) program that gives defined output as per respective input over different events.


# Deterministic Runtime Simulation

Small Python implementation for the deterministic runtime coordination task.

It models one node, applies ordered events, replays the log, checks the final
state hash, and shows a few divergence cases.
>>>>>>> 40bdd748e88a6aa251e04db1024868d220fa9a94

```powershell
python main.py
```

## Files

<<<<<<< HEAD
- `runtime/`: state model, transition executor, errors, and serialization.
- `events/`: immutable event contract and append-only execution log.
- `replay/`: replay entry point.
- `validation/`: event identity checks kept separate from execution.
- `hashing/`: stable JSON/SHA-256 hashing helper.
- `main.py`: runs the example, replay, failure checks, and hash proof.
- `REVIEW_PACKET.md`: short explanation of the build.

No external packages are needed.
=======
- `runtime.py`: state model, event contract, apply/replay logic, hashing.
- `main.py`: runs the example, replay, failure checks, and hash proof.
- `REVIEW_PACKET.md`: short explanation of the build.

>>>>>>> 40bdd748e88a6aa251e04db1024868d220fa9a94
