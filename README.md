# small-deterministic-runtime-program (simulator)
this a simple deterministic runtime simulator, its show working a (runtime) program that gives defined output as per respective input over different events.


# Deterministic Runtime Simulation

Small Python implementation for the deterministic runtime coordination task.

It models one node, applies ordered events, replays the log, checks the final
state hash, and shows a few divergence cases.

```powershell
python main.py
```

## Files

- `runtime.py`: state model, event contract, apply/replay logic, hashing.
- `main.py`: runs the example, replay, failure checks, and hash proof.
- `REVIEW_PACKET.md`: short explanation of the build.

