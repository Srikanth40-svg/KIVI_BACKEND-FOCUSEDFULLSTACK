"""Reproducible seed data.

The seed is a list of **observations**, not a list of memories. Replaying it runs the real
learning policy, so the memory state a reviewer sees was earned by evidence in exactly the
way a real user's would be. Nothing is inserted directly into `word_memories`, which is
what makes RULE 11 (no hardcoded demo behaviour) checkable rather than merely claimed: if
the policy changed, the seeded state would change with it.

Deterministic: the same file always produces the same memories, ids and confidences after
`reset`, because ids restart and every value is derived from the evidence.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from . import learning
from .config import Config

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seed" / "observations.jsonl"


def load_seed(path: Path | None = None) -> list[dict[str, Any]]:
    src = path or SEED_PATH
    if not src.exists():
        raise FileNotFoundError(f"seed file missing: {src}")
    records: list[dict[str, Any]] = []
    for line in src.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        records.append(json.loads(line))
    return sorted(records, key=lambda r: r.get("seq", 0))


def replay_seed(
    conn: sqlite3.Connection,
    config: Config,
    records: list[dict[str, Any]],
    *,
    user_id: str = "default",
) -> dict[str, Any]:
    """Feed every seed observation through the ordinary learning path."""
    summary: dict[str, int] = {}
    detail: list[dict[str, Any]] = []
    for record in records:
        outcome = learning.ingest_observation(
            conn,
            th=config.thresholds,
            asr_text=record.get("asr_text"),
            formatted_text=record.get("formatted_text"),
            user_edited_text=record.get("user_edited_text"),
            app_context=record.get("app_context"),
            user_id=user_id,
            kind="seed",
        )
        for key, value in outcome.summary().items():
            summary[key] = summary.get(key, 0) + value
        detail.append(
            {
                "seq": record.get("seq"),
                "note": record.get("note"),
                "interaction_id": outcome.interaction_id,
                "outcomes": outcome.summary(),
            }
        )
    return {"observations": len(records), "learning_summary": summary, "detail": detail}
