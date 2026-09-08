"""Command line interface: `python -m kivi <command>`.

Everything a reviewer needs without a browser: migrate, seed, reset, inspect memory,
run the three stages, read a decision trace, and run the evaluation.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import db
from . import learning
from . import memory as mem_mod
from . import pipeline
from .config import ConfigError, load_config
from .formatter import format_stub
from .llm import SarvamClient
from .seed import load_seed, replay_seed


def _open(create: bool = True):
    config = load_config()
    conn = db.connect(config.db_path)
    if create:
        db.migrate(conn)
    return config, conn


def _print(obj: Any) -> None:
    print(json.dumps(obj, indent=2, default=str, ensure_ascii=False))


# ----------------------------------------------------------------------------------------

def cmd_migrate(args: argparse.Namespace) -> int:
    config = load_config()
    conn = db.connect(config.db_path)
    applied = db.migrate(conn)
    print(f"database: {config.db_path}")
    print(f"applied: {applied or '(already up to date)'}")
    print(f"all versions: {sorted(db.applied_versions(conn))}")
    return 0


def cmd_seed(args: argparse.Namespace) -> int:
    config, conn = _open()
    existing = db.query_one(conn, "SELECT COUNT(*) AS n FROM interactions")["n"]
    if existing and not args.force:
        print(
            f"refusing to seed: {existing} interactions already exist.\n"
            "Run `python -m kivi reset --reseed` for a clean, deterministic rebuild, "
            "or pass --force to seed on top of what is there."
        )
        return 1
    result = replay_seed(conn, config, load_seed())
    print(f"replayed {result['observations']} seed observations")
    print(f"learning outcomes: {result['learning_summary']}")
    cmd_memories(argparse.Namespace(status=None, json=False))
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    config, conn = _open()
    deleted = db.reset(conn)
    print(f"cleared: { {k: v for k, v in deleted.items() if v} or 'nothing to clear'}")
    if args.reseed:
        result = replay_seed(conn, config, load_seed())
        print(f"replayed {result['observations']} seed observations")
        print(f"learning outcomes: {result['learning_summary']}")
    return 0


def cmd_memories(args: argparse.Namespace) -> int:
    _, conn = _open()
    memories = mem_mod.list_memories(conn, status=getattr(args, "status", None))
    if getattr(args, "json", False):
        _print(memories)
        return 0
    if not memories:
        print("no memories yet")
        return 0
    print(f"{'id':>4}  {'canonical':22} {'type':10} {'status':10} {'conf':>5}  variants")
    print("-" * 100)
    for m in memories:
        variants = ", ".join(
            f"{v['variant_form']}[{v['kind'][:4]}]" for v in m["variants"] if v["kind"] != "canonical"
        )
        print(
            f"{m['id']:>4}  {m['canonical_form'][:22]:22} {m['word_type']:10} "
            f"{m['status']:10} {float(m['confidence']):>5.2f}  {variants}"
        )
    return 0


def cmd_memory(args: argparse.Namespace) -> int:
    _, conn = _open()
    full = mem_mod.get_full(conn, args.id)
    if full is None:
        print(f"no memory {args.id}", file=sys.stderr)
        return 1
    _print(full)
    return 0


def cmd_observe(args: argparse.Namespace) -> int:
    config, conn = _open()
    outcome = learning.ingest_observation(
        conn, th=config.thresholds, asr_text=args.asr, formatted_text=args.formatted,
        user_edited_text=args.edited, app_context=args.app,
    )
    print(f"interaction #{outcome.interaction_id}: {outcome.summary()}")
    for p in outcome.proposals:
        print(f"\n  [{p['outcome']}] {p['surface_form']!r} -> {p['canonical']!r}  ({p['word_type']})")
        print(f"    {p['reason_code']}: {p['reason_text']}")
    if not outcome.proposals:
        print("  nothing proposed: no evidence in this observation supported learning a word")
    return 0


def cmd_format(args: argparse.Namespace) -> int:
    print(format_stub(args.asr))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    config, conn = _open()
    client = SarvamClient(config) if config.llm_available else None
    result = pipeline.memory_aware_format(
        conn, config, formatted_text=args.formatted, asr_text=args.asr,
        app_context=args.app, apply_mode=args.mode, client=client,
    )
    if args.json:
        _print(pipeline.explain(result))
        return 0

    print(f"ASR          : {result.asr_text or '(not supplied)'}")
    print(f"FORMATTED    : {result.formatted_text}")
    print(f"MEMORY-AWARE : {result.memory_aware_text}")
    print(f"\nintervened   : {result.intervened}")
    print(f"decision     : #{result.decision_id}   mode={result.apply_mode}")
    print(f"timings      : {result.timings}")
    if result.usage.calls:
        print(f"model usage  : {result.usage.as_dict()}")

    for label, action in (
        ("APPLIED", "applied"), ("ABSTAINED", "abstained"),
        ("NO-OP", "noop"), ("BLOCKED", "blocked"),
    ):
        rows = [c for c in result.candidates if c.action == action]
        if not rows:
            continue
        print(f"\n{label}:")
        for c in rows:
            ctx = c.context
            gate = f"ctx {ctx.score:.2f}/{ctx.required:.2f}" if ctx else "no gate"
            print(f"  {c.span.text!r} -> {c.replacement!r}  [{c.reason_code}]  {gate}")
            print(f"      {c.reason_text}")
    if client:
        client.close()
    return 0


def cmd_decision(args: argparse.Namespace) -> int:
    _, conn = _open()
    trace = pipeline.decision_trace(conn, args.id)
    if trace is None:
        print(f"no decision {args.id}", file=sys.stderr)
        return 1
    _print(trace)
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    config, conn = _open()
    _print(db.storage_stats(conn, config.db_path))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """Verify configuration, and optionally make one real model call."""
    config, conn = _open()
    print(json.dumps(config.describe(), indent=2))
    print(f"migrations: {sorted(db.applied_versions(conn))}")
    if not config.llm_available:
        print("\nSARVAM_API_KEY is not set. The system is fully functional without it; "
              "only the optional adjudicator and prompt mode are unavailable.")
        return 0
    client = SarvamClient(config)
    result = client.health()
    client.close()
    if result.ok:
        print(f"\nSarvam API: OK (model={config.llm_model})")
        print(f"  reply: {(result.text or '').strip()[:60]!r}")
        print(f"  usage: {result.usage.as_dict()}")
        return 0
    print(f"\nSarvam API: FAILED — {result.error}", file=sys.stderr)
    return 1


def cmd_eval(args: argparse.Namespace) -> int:
    from .eval.runner import main as eval_main

    return eval_main(args)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m kivi", description="Kivi phonetic memory")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("migrate", help="create or upgrade the database").set_defaults(func=cmd_migrate)

    s = sub.add_parser("seed", help="replay the committed seed observations")
    s.add_argument("--force", action="store_true", help="seed even if data already exists")
    s.set_defaults(func=cmd_seed)

    s = sub.add_parser("reset", help="clear all data (optionally reseed)")
    s.add_argument("--reseed", action="store_true", help="replay the seed after clearing")
    s.set_defaults(func=cmd_reset)

    s = sub.add_parser("memories", help="list memory state")
    s.add_argument("--status", choices=["candidate", "confirmed", "superseded", "deleted"])
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_memories)

    s = sub.add_parser("memory", help="one memory with evidence and audit trail")
    s.add_argument("id", type=int)
    s.set_defaults(func=cmd_memory)

    s = sub.add_parser("observe", help="feed an observation and show what was learned")
    s.add_argument("--asr")
    s.add_argument("--formatted")
    s.add_argument("--edited", help="the person's corrected version of our output (strongest evidence)")
    s.add_argument("--app", help="window title / surface, e.g. 'Slack - #kivi-eng'")
    s.set_defaults(func=cmd_observe)

    s = sub.add_parser("format", help="stage 2 only (stand-in formatter)")
    s.add_argument("asr")
    s.set_defaults(func=cmd_format)

    s = sub.add_parser("apply", help="run all three stages and explain the decision")
    s.add_argument("--asr")
    s.add_argument("--formatted")
    s.add_argument("--app")
    s.add_argument("--mode", choices=["deterministic", "prompt"])
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_apply)

    s = sub.add_parser("decision", help="replay a stored decision trace")
    s.add_argument("id", type=int)
    s.set_defaults(func=cmd_decision)

    sub.add_parser("stats", help="database growth and row counts").set_defaults(func=cmd_stats)
    sub.add_parser("check", help="validate config and credentials").set_defaults(func=cmd_check)

    s = sub.add_parser("eval", help="run the evaluation")
    s.add_argument("--split", default="dev", choices=["dev", "holdout", "both"])
    s.add_argument("--system", default="all",
                   help="'all', 'kivi', or a baseline name (exact, fuzzy, llm_only)")
    s.add_argument("--out", default="eval/results")
    s.add_argument("--limit", type=int, default=0, help="run only the first N cases")
    s.set_defaults(func=cmd_eval)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except ConfigError as exc:
        print(f"configuration error:\n{exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"missing file: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
