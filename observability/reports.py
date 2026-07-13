from __future__ import annotations

import json
from pathlib import Path

from coordination.scenarios import CoordinationVerification


def build_replay_evidence(verification: CoordinationVerification) -> dict[str, object]:
    """Return a JSON-safe, deterministic audit of coordinated execution."""
    timeline = [record.canonical() for record in verification.result.deliveries]
    return {
        "format_version": 1,
        "execution_audit_log": timeline,
        "execution_timeline": timeline,
        "runtime_summary": {
            "node_count": len(verification.node_summaries),
            "coordinated_state_hash": verification.result.coordinated_state_hash,
            "nodes": verification.node_summaries,
        },
        "replay_report": {
            "verified": verification.replay_verified,
            "node_replay_hashes": verification.node_replay_hashes,
        },
        "replay_summary": {
            "delivery_count": len(timeline),
            "final_coordinated_state_hash": verification.result.coordinated_state_hash,
            "result": "MATCHED" if verification.replay_verified else "MISMATCH",
        },
    }


def export_replay_evidence(
    verification: CoordinationVerification,
    destination: str | Path,
) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_replay_evidence(verification), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
