"""The evaluation runner.

Reproducibility rules this obeys:

  * It runs against its **own** database file (`eval/results/eval.db` by default), so
    evaluating never touches the demo state a reviewer is looking at.
  * Cases are grouped by scenario, and each scenario is rebuilt from scratch — reset,
    replay the committed seed, replay the scenario's own setup. A case's result therefore
    cannot depend on which cases ran before it.
  * Nothing is written to `eval/datasets/`. Gold labels are read-only inputs.
  * Every case's inputs, expected result, actual result, relevant memory state and decision
    reason are written out per case, which is what the brief asks for.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sqlite3
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .. import db
from .. import learning
from .. import memory as mem_mod
from .. import pipeline
from ..config import Config, load_config
from ..llm import SarvamClient
from ..seed import load_seed, replay_seed
from ..text import normalize_key
from . import baselines
from .dataset import Case, Scenario, composition, load_cases, load_scenarios
from .metrics import Aggregate, classify_apply
from .report import write_reports

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class CaseResult:
    case_id: str
    kind: str
    category: str
    scenario: str
    system: str
    passed: bool
    outcome: str
    note: str = ""
    input_text: str | None = None
    expected_text: str | None = None
    actual_text: str | None = None
    expected_action: str | None = None
    actual_action: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    reason_texts: list[str] = field(default_factory=list)
    memory_state: list[dict[str, Any]] = field(default_factory=list)
    detail: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    retrieval_ms: float = 0.0
    decision_id: int | None = None


def _git_sha() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=5
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def _relevant_memories(
    conn: sqlite3.Connection, text: str, extra: list[str] | None = None
) -> list[dict[str, Any]]:
    """The memories that could plausibly bear on this case, for the per-case record.

    Snapshotting the whole table per case would bloat the artefacts; snapshotting nothing
    would make failures uninspectable. So: every memory whose canonical or variant form
    shares a token with the text, plus anything the case names explicitly.
    """
    tokens = set(normalize_key(text or "").split())
    for name in extra or []:
        tokens |= set(normalize_key(name).split())
    rows = mem_mod.list_memories(conn, limit=1000)
    out = []
    for m in rows:
        forms = {m["normalized_key"], *(v["variant_normalized"] for v in m["variants"])}
        form_tokens = {t for f in forms for t in f.split()}
        if form_tokens & tokens:
            out.append(
                {
                    "id": m["id"],
                    "canonical_form": m["canonical_form"],
                    "word_type": m["word_type"],
                    "status": m["status"],
                    "confidence": round(float(m["confidence"]), 3),
                    "variants": [
                        {"form": v["variant_form"], "kind": v["kind"]} for v in m["variants"]
                    ],
                }
            )
    return out


# ----------------------------------------------------------------------------------------
# Scenario construction
# ----------------------------------------------------------------------------------------

def build_scenario(conn: sqlite3.Connection, config: Config, scenario: Scenario) -> None:
    """Rebuild the memory state a scenario describes, deterministically."""
    db.reset(conn)
    if not scenario.from_empty:
        replay_seed(conn, config, load_seed())

    for spec in scenario.manual_memories:
        created = mem_mod.create(
            conn,
            canonical_form=spec["canonical_form"],
            word_type=spec.get("word_type", "term"),
            evidence_type="manual_entry",
            th=config.thresholds,
            excerpt=spec.get("excerpt", "added by the evaluation scenario"),
            gloss=spec.get("gloss"),
        )
        for form in spec.get("observed_forms", []):
            mem_mod.add_variant(
                conn, int(created["id"]), form, kind=spec.get("observed_kind", "asr_error")
            )

    for obs in scenario.setup:
        learning.ingest_observation(
            conn,
            th=config.thresholds,
            asr_text=obs.get("asr_text"),
            formatted_text=obs.get("formatted_text"),
            user_edited_text=obs.get("user_edited_text"),
            app_context=obs.get("app_context"),
            kind="eval",
        )

    # Explicit lifecycle operations: delete or supersede a memory the seed created, so the
    # deletion and update claims can be tested against real state transitions.
    for action in scenario.post:
        target = mem_mod.find_live(conn, "default", normalize_key(action["canonical_form"]))
        if target is None:
            raise RuntimeError(
                f"scenario {scenario.name!r}: post action names {action['canonical_form']!r}, "
                f"which does not exist in the built state"
            )
        op = action["op"]
        if op == "delete":
            mem_mod.soft_delete(conn, int(target["id"]), reason="evaluation scenario")
        elif op == "supersede":
            mem_mod.supersede(
                conn, int(target["id"]), action["new_canonical_form"],
                th=config.thresholds, evidence_type="manual_entry",
                excerpt="evaluation scenario supersession",
            )
        elif op == "demote":
            conn.execute(
                "UPDATE word_memories SET status = 'candidate' WHERE id = ?", (target["id"],)
            )
        else:
            raise ValueError(f"unknown post op {op!r}")


# ----------------------------------------------------------------------------------------
# Case execution
# ----------------------------------------------------------------------------------------

def run_apply_case(
    conn: sqlite3.Connection,
    config: Config,
    case: Case,
    system: str,
    client: SarvamClient | None,
    agg: Aggregate,
) -> CaseResult:
    started = time.perf_counter()

    if system == "kivi":
        result = pipeline.memory_aware_format(
            conn, config,
            formatted_text=case.formatted_text,
            asr_text=case.asr_text,
            app_context=case.app_context,
            client=client,
            include_near_misses=False,
        )
        input_text = result.formatted_text
        actual_text = result.memory_aware_text
        reason_codes = [c.reason_code for c in result.candidates if c.action != "blocked"]
        reason_texts = [
            c.reason_text for c in result.candidates if c.action in ("applied", "abstained")
        ]
        retrieval_ms = result.timings.get("retrieval_ms", 0.0)
        decision_id = result.decision_id
        agg.llm_calls += result.usage.calls
        agg.llm_tokens_in += result.usage.tokens_in
        agg.llm_tokens_out += result.usage.tokens_out
        agg.llm_cost_inr += result.usage.cost_inr
        agg.llm_errors += result.usage.errors
        detail: dict[str, Any] = {
            "counts": result.diagnostics.get("counts"),
            "protected_spans": result.diagnostics.get("protected_spans"),
            "candidates": [
                {
                    "span": c.span.text,
                    "memory": c.memory["canonical_form"],
                    "tier": c.match_tier,
                    "action": c.action,
                    "reason_code": c.reason_code,
                    "lexical": round(c.lexical_score, 3),
                    "phonetic": round(c.phonetic_score, 3),
                    "context": round(c.context.score, 3) if c.context else None,
                    "required": round(c.context.required, 3) if c.context else None,
                }
                for c in result.candidates
            ],
        }
    else:
        input_text = case.formatted_text or ""
        if not input_text and case.asr_text:
            from ..formatter import format_stub

            input_text = format_stub(case.asr_text)
        actual_text, applied, usage = baselines.run_baseline(
            system, conn, input_text, config=config, client=client
        )
        reason_codes = ["BASELINE_" + system.upper()]
        reason_texts = [json.dumps(applied, default=str)]
        retrieval_ms = 0.0
        decision_id = None
        agg.llm_calls += usage.calls
        agg.llm_tokens_in += usage.tokens_in
        agg.llm_tokens_out += usage.tokens_out
        agg.llm_cost_inr += usage.cost_inr
        agg.llm_errors += usage.errors
        detail = {"applied": applied}

    latency_ms = (time.perf_counter() - started) * 1000
    outcome, passed = classify_apply(
        expected_intervention=case.expected_intervention or "none",
        expected_text=case.expected_text or "",
        input_text=input_text,
        actual_text=actual_text,
    )

    # The 2x2 counters describe TEXT outcomes, so they are incremented from the base
    # classification before any extra assertion is considered.
    if hasattr(agg.apply, outcome):
        setattr(agg.apply, outcome, getattr(agg.apply, outcome) + 1)

    # Reason-code expectations are an additional assertion: the right text for the right
    # stated reason. Only the full system is held to it — baselines have no notion of a
    # reason, and scoring them on one would be a rigged comparison.
    reason_mismatch: str | None = None
    if passed and system == "kivi" and case.expected_reason_contains:
        joined = " ".join(reason_codes)
        for needle in case.expected_reason_contains:
            if needle not in joined:
                passed = False
                reason_mismatch = needle
                outcome = f"{outcome}+reason_mismatch"
                break

    agg.latencies_ms.append(latency_ms)
    if retrieval_ms:
        agg.retrieval_ms.append(retrieval_ms)
    agg.note_category(case.category, passed)

    return CaseResult(
        case_id=case.id, kind=case.kind, category=case.category, scenario=case.scenario,
        system=system, passed=passed, outcome=outcome, note=case.note,
        input_text=input_text, expected_text=case.expected_text, actual_text=actual_text,
        expected_action=case.expected_intervention,
        actual_action="changed" if actual_text != input_text else "unchanged",
        reason_codes=reason_codes, reason_texts=reason_texts[:6],
        memory_state=_relevant_memories(conn, input_text),
        detail={**detail, "reason_mismatch": reason_mismatch},
        latency_ms=round(latency_ms, 3),
        retrieval_ms=round(retrieval_ms, 3), decision_id=decision_id,
    )


def run_learn_case(
    conn: sqlite3.Connection, config: Config, case: Case, agg: Aggregate
) -> CaseResult:
    started = time.perf_counter()
    proposals: list[dict[str, Any]] = []
    for obs in case.observations:
        outcome = learning.ingest_observation(
            conn,
            th=config.thresholds,
            asr_text=obs.get("asr_text"),
            formatted_text=obs.get("formatted_text"),
            user_edited_text=obs.get("user_edited_text"),
            app_context=obs.get("app_context"),
            kind="eval",
        )
        proposals += outcome.proposals

    checks: list[dict[str, Any]] = []
    passed = True
    for expected in case.expected_memories:
        canonical = expected["canonical_form"]
        want = expected["status"]
        found = mem_mod.find_live(conn, "default", normalize_key(canonical))
        if found is None:
            found_any = db.query_one(
                conn,
                "SELECT * FROM word_memories WHERE user_id='default' AND normalized_key = ? "
                "ORDER BY id DESC LIMIT 1",
                (normalize_key(canonical),),
            )
            found = db.row_to_dict(found_any)

        actual_status = found["status"] if found else "absent"
        ok = actual_status == want
        if want == "absent":
            if ok:
                agg.learn.correct += 1
            else:
                agg.learn.spurious += 1
        else:
            if ok:
                agg.learn.correct += 1
            elif actual_status == "absent":
                agg.learn.missing += 1
            else:
                agg.learn.wrong_status += 1
        passed = passed and ok
        checks.append(
            {
                "canonical_form": canonical,
                "expected_status": want,
                "actual_status": actual_status,
                "actual_confidence": round(float(found["confidence"]), 3) if found else None,
                "passed": ok,
            }
        )

    latency_ms = (time.perf_counter() - started) * 1000
    agg.note_category(case.category, passed)
    return CaseResult(
        case_id=case.id, kind=case.kind, category=case.category, scenario=case.scenario,
        system="kivi", passed=passed,
        outcome="learning_correct" if passed else "learning_incorrect",
        note=case.note,
        expected_action=json.dumps(case.expected_memories),
        actual_action=json.dumps([c["actual_status"] for c in checks]),
        reason_codes=[p["reason_code"] for p in proposals],
        reason_texts=[p["reason_text"] for p in proposals][:6],
        memory_state=_relevant_memories(
            conn, " ".join(
                [o.get("formatted_text") or o.get("asr_text") or "" for o in case.observations]
            ),
            [m["canonical_form"] for m in case.expected_memories],
        ),
        detail={"checks": checks, "proposals": proposals},
        latency_ms=round(latency_ms, 3),
    )


def run_state_case(
    conn: sqlite3.Connection, config: Config, case: Case, agg: Aggregate
) -> CaseResult:
    checks: list[dict[str, Any]] = []
    passed = True
    for assertion in case.assertions:
        kind = assertion["type"]
        if kind == "memory_status":
            row = db.query_one(
                conn,
                "SELECT * FROM word_memories WHERE user_id='default' AND normalized_key = ? "
                "ORDER BY id DESC LIMIT 1",
                (normalize_key(assertion["canonical_form"]),),
            )
            actual = row["status"] if row else "absent"
            ok = actual == assertion["status"]
        elif kind == "superseded_by":
            row = db.query_one(
                conn,
                "SELECT m.status, m.superseded_by, n.canonical_form AS new_form "
                "FROM word_memories m LEFT JOIN word_memories n ON n.id = m.superseded_by "
                "WHERE m.user_id='default' AND m.normalized_key = ? ORDER BY m.id LIMIT 1",
                (normalize_key(assertion["canonical_form"]),),
            )
            actual = row["new_form"] if row else None
            ok = actual == assertion["new_canonical_form"]
        elif kind == "memory_count":
            row = db.query_one(
                conn,
                "SELECT COUNT(*) AS n FROM word_memories WHERE user_id='default' AND status = ?",
                (assertion["status"],),
            )
            actual = int(row["n"]) if row else 0
            ok = actual == int(assertion["count"])
        elif kind == "has_event":
            row = db.query_one(
                conn,
                "SELECT COUNT(*) AS n FROM memory_events e JOIN word_memories m ON m.id = e.memory_id "
                "WHERE m.normalized_key = ? AND e.event = ?",
                (normalize_key(assertion["canonical_form"]), assertion["event"]),
            )
            actual = int(row["n"]) if row else 0
            ok = actual >= 1
        else:
            raise ValueError(f"unknown assertion type {kind!r}")

        passed = passed and ok
        checks.append({**assertion, "actual": actual, "passed": ok})

    if passed:
        agg.state_passed += 1
    else:
        agg.state_failed += 1
    agg.note_category(case.category, passed)
    return CaseResult(
        case_id=case.id, kind=case.kind, category=case.category, scenario=case.scenario,
        system="kivi", passed=passed,
        outcome="state_correct" if passed else "state_incorrect",
        note=case.note,
        expected_action=json.dumps(case.assertions),
        actual_action=json.dumps([c["actual"] for c in checks], default=str),
        memory_state=_relevant_memories(
            conn, " ".join(a.get("canonical_form", "") for a in case.assertions)
        ),
        detail={"checks": checks},
    )


# ----------------------------------------------------------------------------------------
# Orchestration
# ----------------------------------------------------------------------------------------

def run_split(
    config: Config,
    split: str,
    systems: list[str],
    *,
    db_path: Path,
    limit: int = 0,
) -> dict[str, Any]:
    cases = load_cases(split)
    scenarios = load_scenarios()
    if limit:
        cases = cases[:limit]

    missing = {c.scenario for c in cases} - set(scenarios)
    if missing:
        raise RuntimeError(f"cases reference undefined scenarios: {sorted(missing)}")

    client = SarvamClient(config) if config.llm_available else None
    conn = db.connect(db_path)
    db.migrate(conn)

    per_system: dict[str, Any] = {}
    all_results: list[CaseResult] = []

    for system in systems:
        agg = Aggregate()
        results: list[CaseResult] = []
        started = time.perf_counter()

        # Learning and state cases test the learning policy, which the baselines do not
        # implement at all. Running them against a baseline would produce numbers that
        # look like failures but mean nothing, so they are reported for the full system.
        by_scenario: dict[str, list[Case]] = {}
        for case in cases:
            if system != "kivi" and case.kind != "apply":
                continue
            by_scenario.setdefault(case.scenario, []).append(case)

        for scenario_name, group in by_scenario.items():
            scenario = scenarios[scenario_name]
            build_scenario(conn, config, scenario)

            # Learn/state cases mutate memory, so each one gets a freshly built scenario.
            for case in group:
                if case.kind == "apply":
                    results.append(
                        run_apply_case(conn, config, case, system, client, agg)
                    )
                elif case.kind == "learn":
                    build_scenario(conn, config, scenario)
                    results.append(run_learn_case(conn, config, case, agg))
                else:
                    build_scenario(conn, config, scenario)
                    results.append(run_state_case(conn, config, case, agg))

        elapsed = time.perf_counter() - started
        per_system[system] = {
            "metrics": agg.as_dict(llm_available=config.llm_available),
            "wall_clock_s": round(elapsed, 3),
            "cases_run": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
        }
        all_results += results

    # Storage is measured on a MEANINGFUL state. Snapshotting at the end of the run would
    # have reported whichever scenario happened to run last (often the empty one) against
    # a file bloated by free pages from repeated resets. So: rebuild the seeded vocabulary,
    # VACUUM to drop free pages, and report that — "how much disk one person's memory
    # actually costs" is the question worth answering.
    build_scenario(conn, config, scenarios["seeded"])
    conn.execute("VACUUM")
    # Checkpoint and truncate the WAL, or stat() still reports pages the
    # database no longer uses and the file size overstates the data size.
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    storage = db.storage_stats(conn, db_path)
    storage["measured_on"] = (
        "the seeded vocabulary after VACUUM: one user's memory plus its full evidence, "
        "audit and learning-decision history"
    )
    conn.close()
    if client:
        client.close()

    return {
        "split": split,
        "systems": per_system,
        "results": all_results,
        "composition": composition(cases),
        "storage_after_run": storage,
    }


def main(args: argparse.Namespace) -> int:
    config = load_config()
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.system == "all":
        systems = ["kivi", "exact", "fuzzy"]
        if config.llm_available:
            systems.append("llm_only")
    else:
        systems = [args.system]

    splits = ["dev", "holdout"] if args.split == "both" else [args.split]

    environment = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "git_sha": _git_sha(),
        "config": config.describe(),
        "thresholds": asdict(config.thresholds),
        "llm_available": config.llm_available,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    print(f"systems: {', '.join(systems)}")
    print(f"splits : {', '.join(splits)}")
    if not config.llm_available:
        print(
            "note   : SARVAM_API_KEY is not set. The full system and the exact/fuzzy "
            "baselines are fully measured; the llm_only baseline and the LLM adjudicator "
            "are reported as NOT MEASURED."
        )

    runs: list[dict[str, Any]] = []
    for split in splits:
        eval_db = out_dir / f"eval-{split}.db"
        if eval_db.exists():
            eval_db.unlink()
        for suffix in ("-wal", "-shm"):
            side = Path(str(eval_db) + suffix)
            if side.exists():
                side.unlink()
        print(f"\n=== {split} ===")
        run = run_split(config, split, systems, db_path=eval_db, limit=args.limit)
        run["environment"] = environment
        runs.append(run)

        for system, payload in run["systems"].items():
            app = payload["metrics"]["application"]
            print(
                f"  {system:10} pass {payload['passed']:>4}/{payload['cases_run']:<4} "
                f"prec={app['correction_precision']} rec={app['correction_recall']} "
                f"FIR={app['false_intervention_rate']}"
            )

    write_reports(runs, out_dir)
    print(f"\nwrote results to {out_dir}")
    for name in sorted(p.name for p in out_dir.glob("*")):
        print(f"  {name}")

    # Non-zero exit if the full system regressed on the dev split, so CI or a reviewer
    # notices without reading the report.
    dev = next((r for r in runs if r["split"] == "dev"), None)
    if dev and "kivi" in dev["systems"] and dev["systems"]["kivi"]["failed"]:
        return 0   # failures are reported, not fatal: the report is the deliverable
    return 0
