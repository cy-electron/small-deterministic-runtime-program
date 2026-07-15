# Multi-Node Deterministic Runtime Coordination

A local, deterministic simulation of coordinated runtime participants. It
extends the existing replay-safe single-node core with four independent nodes,
immutable messages, bounded delivery, replay verification, and structured
evidence. It deliberately contains no networking, APIs, database, consensus
protocol, cloud dependency, or concurrent execution.

(previously Replay-Safe Runtime and small deterministic runtime simulator)

<<<<<<< HEAD
A Python implementation of a replay-safe deterministic runtime core demonstrating
immutable execution logs, deterministic event processing, runtime validation,
state hashing, and replay verification.

this is the updated program (version v2 as per the task) of small-deterministic-runtime-program

## Run
Run it with:
>>>>>>> 3e205ecaa0dff9f3c70a1b6bd56091f41bf19056

```powershell
python main.py
```

The command prints the original single-node proof, coordinated delivery audit,
replay result, and stress results. It writes JSON evidence to
`artifacts/replay_evidence.json`.

For validation, install optional development tools and run:

```powershell
python -m pip install -r requirements-dev.txt
powershell -ExecutionPolicy Bypass -File scripts/run_validation.ps1
```

This creates ignored, reproducible outputs under `artifacts/`: a coverage
report, benchmark result, and execution summary.

Pytest is configured to use `artifacts/pytest_tmp` rather than the Windows
system temporary folder, so the test suite remains usable on machines where
the default pytest temp directory is restricted.

## Architecture Overview

<<<<<<< HEAD
```text
immutable RuntimeMessage
          |
          v
DeterministicCoordinator -- canonical order --> independent RuntimeNode (3–5)
          |                                           |
          v                                           v
delivery audit                                 event history + state hash
          |                                           |
          +----------------> replay verification <---+
                                |
                                v
                         JSON replay evidence
```

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
>>>>>>> 3e205ecaa0dff9f3c70a1b6bd56091f41bf19056

- `runtime/`: immutable runtime state, legal transitions, execution, and
  `RuntimeNode`, which owns state, execution history, state hash, and replay
  history.
- `coordination/`: immutable `RuntimeMessage`, fixed-capacity coordinator, and
  four-node ring scenario.
- `observability/`: canonical audit, timeline, summary, replay report, and
  JSON export.
- `events/`, `validation/`, `replay/`, `hashing/`: the original deterministic
  event-sourcing and replay core.

For a guided, line-by-line explanation of what happens during one run, see
[docs/WORKING_GUIDE.md](docs/WORKING_GUIDE.md).

## Coordination Flow

1. `RuntimeMessage.create()` derives an immutable ID from canonical fields.
2. The coordinator accepts only known nodes and no more than `max_messages`.
3. It sorts pending messages by `(logical_clock, source, target, message_id)`.
4. A message becomes a deterministic target-node event and is appended with
   that node's next local sequence number.
5. The target node rebuilds from its complete history, records a state hash,
   and the coordinator records a delivery audit entry.

The included ring submits messages in deliberately non-canonical input order;
delivery is always logical-clock order. Every node receives `START` exactly
once and independently reaches `PROCESSING`.

## Execution Flow

For each node event, validation checks the event ID, deterministic timestamp,
sequence, event uniqueness, node identity, causal order, legal transition, and
post-transition invariants. The node only updates its visible state after the
complete candidate history executes successfully.

## Replay Flow

Each node re-executes its immutable history from `NodeState.initial(node_id)`.
Every resulting snapshot is checked against the original sequence, event ID,
and hash. The full coordination scenario is then reconstructed from the same
messages in reverse enqueue order; both delivery records and the coordinated
state hash must match.

## Design Decisions

- **Local deterministic model:** avoids nondeterminism from transport,
  clocks, threads, and external storage.
- **Canonical ordering:** a total ordering key makes arrival/enqueue order
  irrelevant.
- **Bounded queue:** a hard capacity fails safely before unbounded work grows.
- **History-based node update:** rebuilding from history prioritizes replay
  clarity and atomic state replacement over performance.
- **Structured evidence:** JSON contains execution audit logs, a timeline,
  runtime summaries, replay reports, and replay summaries.

## Validation

`tests/` is a pytest suite covering convergence, order independence, immutable
messages, capacity and unknown-node failures, replay history, and JSON exports.
`benchmark.py` confirms repeated coordinated executions produce one hash.
`scripts/run_validation.ps1` produces pytest/coverage/benchmark artifacts and
an execution summary.

## Known Limitations

- This is a simulation, not a distributed system: no network transport,
  persistence, failure recovery, clocks, or consensus.
- The coordinator delivers a finite batch serially; it does not model dynamic
  message generation during delivery.
- Nodes replay their complete history for every accepted event, which is
  intentionally simple but not optimized for long histories.
- The scenario demonstrates convergence as identical ordered coordinated state,
  not replicated identical node IDs or state hashes.

## Future Improvements

- Add deterministic snapshots to avoid full history rebuilds.
- Model scheduled batches and explicit causal dependencies.
- Add property-based tests for generated bounded message sets.
- Define a versioned import format for replay evidence.
- Add a separate, deliberately out-of-scope transport adapter only after the
  deterministic local model remains fully reproducible.

## Verification Evidence

See `review_packets/evidence` for generated artifacts.

Screenshots of the execution are available in `review_packets/Screenshots`.