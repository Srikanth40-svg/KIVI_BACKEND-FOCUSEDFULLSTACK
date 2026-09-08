"""Report writing.

Four artefacts, all committed to the repository so a reviewer can read the results before
running anything, and reproduce them afterwards:

  * ``summary.json``            every metric, the dataset composition, and the environment
                                the numbers came from.
  * ``report.md``               the readable version, including the baseline comparison.
  * ``cases-<split>-<sys>.jsonl`` one row per case: inputs, expected, actual, the relevant
                                memory state, and the decision reason.
  * ``failures-<split>.md``     every failing case in full, grouped by category.

Nothing here rounds a number in the system's favour, and any metric that was not measured
is written as such instead of being filled in with a zero.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def write_reports(runs: list[dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "runs": [
            {
                "split": run["split"],
                "composition": run["composition"],
                "systems": run["systems"],
                "storage_after_run": run["storage_after_run"],
                "environment": run.get("environment"),
            }
            for run in runs
        ]
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )

    for run in runs:
        split = run["split"]
        by_system: dict[str, list[Any]] = {}
        for result in run["results"]:
            by_system.setdefault(result.system, []).append(result)
        for system, results in by_system.items():
            path = out_dir / f"cases-{split}-{system}.jsonl"
            with path.open("w", encoding="utf-8") as fh:
                for result in results:
                    fh.write(
                        json.dumps(dataclasses.asdict(result), default=str, ensure_ascii=False)
                        + "\n"
                    )
        _write_failures(run, out_dir / f"failures-{split}.md")

    (out_dir / "report.md").write_text(_render_markdown(runs), encoding="utf-8")


def _write_failures(run: dict[str, Any], path: Path) -> None:
    failures = [r for r in run["results"] if not r.passed]
    lines = [
        f"# Failures — {run['split']} split",
        "",
        f"{len(failures)} failing case(s) out of {len(run['results'])} case-runs "
        f"across {len(run['systems'])} system(s).",
        "",
        "Every failure is listed in full. Nothing is summarised away, because the point of "
        "this file is that a reviewer can see exactly what the system got wrong and why it "
        "thought it was right.",
        "",
    ]
    if not failures:
        lines.append("_No failures in this run._")
        path.write_text("\n".join(lines), encoding="utf-8")
        return

    grouped: dict[str, list[Any]] = {}
    for f in failures:
        grouped.setdefault(f"{f.system} / {f.category}", []).append(f)

    for group, items in sorted(grouped.items()):
        lines += [f"## {group} — {len(items)} failing", ""]
        for f in items:
            lines += [
                f"### `{f.case_id}` — {f.outcome}",
                "",
                f"- **scenario**: `{f.scenario}`",
                f"- **why this case exists**: {f.note or '(no note)'}",
                f"- **input**: `{f.input_text}`",
                f"- **expected** ({f.expected_action}): `{f.expected_text}`",
                f"- **actual** ({f.actual_action}): `{f.actual_text}`",
            ]
            if f.reason_codes:
                lines.append(f"- **reason codes**: `{', '.join(f.reason_codes[:8])}`")
            if f.reason_texts:
                lines.append(f"- **system's reasoning**: {f.reason_texts[0]}")
            if f.memory_state:
                mem = ", ".join(
                    f"#{m['id']} {m['canonical_form']!r} ({m['word_type']}, {m['status']}, "
                    f"{m['confidence']})"
                    for m in f.memory_state[:6]
                )
                lines.append(f"- **relevant memory**: {mem}")
            if f.detail:
                lines += [
                    "",
                    "<details><summary>full decision detail</summary>",
                    "",
                    "```json",
                    json.dumps(f.detail, indent=2, default=str)[:4000],
                    "```",
                    "",
                    "</details>",
                ]
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


_METRIC_ROWS = [
    ("cases", "cases", str),
    ("correct interventions", "correct_intervention", str),
    ("**false interventions**", "false_intervention", str),
    ("missed interventions", "missed_intervention", str),
    ("acted but wrong text", "acted_but_wrong_text", str),
    ("correct silences", "correct_silence", str),
    ("correction precision", "correction_precision", _pct),
    ("correction recall", "correction_recall", _pct),
    ("**false intervention rate**", "false_intervention_rate", _pct),
    ("missed intervention rate", "missed_intervention_rate", _pct),
    ("exact text accuracy", "exact_text_accuracy", _pct),
]


def _render_markdown(runs: list[dict[str, Any]]) -> str:
    lines = [
        "# Evaluation results — Kivi phonetic memory",
        "",
        "Generated by `python -m kivi eval --split both`. Every number here comes from that "
        "command; nothing is hand-entered.",
        "",
    ]

    env = next((r.get("environment") for r in runs if r.get("environment")), None)
    if env:
        lines += [
            "## Environment",
            "",
            f"- python `{env.get('python')}` on `{env.get('platform')}`",
            f"- commit `{env.get('git_sha') or 'not a git checkout'}`",
            f"- model credentials present: **{env.get('llm_available')}**",
            f"- run started: `{env.get('started_at')}`",
            "",
        ]
        if not env.get("llm_available"):
            lines += [
                "> No `SARVAM_API_KEY` was set for this run. The full system and the "
                "`exact`/`fuzzy` baselines are therefore **fully measured**; the "
                "`llm_only` baseline and the LLM adjudicator are **NOT MEASURED** and are "
                "reported as such rather than estimated.",
                "",
            ]

    for run in runs:
        split = run["split"]
        systems = run["systems"]
        comp = run["composition"]

        lines += [
            f"## {split} split",
            "",
            "### Dataset composition",
            "",
            f"- **{comp['total']} cases**",
            f"- by kind: {comp['by_kind']}",
            f"- by expected behaviour: {comp['by_expected_intervention']}",
            f"- scenarios exercised: {len(comp['by_scenario'])}",
            "",
            "<details><summary>by category</summary>",
            "",
            "| category | cases |",
            "| --- | --- |",
        ]
        for cat, n in comp["by_category"].items():
            lines.append(f"| `{cat}` | {n} |")
        lines += ["", "</details>", ""]

        names = list(systems)
        lines += [
            "### Application metrics",
            "",
            "The two rows that matter most are bolded: a **false intervention** damages text "
            "the person said correctly, which is this product's worst failure.",
            "",
            "| metric | " + " | ".join(f"`{n}`" for n in names) + " |",
            "| --- | " + " | ".join("---" for _ in names) + " |",
        ]
        for label, key, fmt in _METRIC_ROWS:
            cells = []
            for name in names:
                app = systems[name]["metrics"]["application"]
                cells.append(fmt(app.get(key)))
            lines.append(f"| {label} | " + " | ".join(cells) + " |")
        lines.append("")

        kivi = systems.get("kivi")
        if kivi:
            learn = kivi["metrics"]["learning"]
            state = kivi["metrics"]["state_assertions"]
            lines += [
                "### Learning metrics (full system only)",
                "",
                "Baselines implement no learning policy, so scoring them here would produce "
                "meaningless numbers.",
                "",
                f"- assertions: **{learn['assertions']}**",
                f"- memory precision: **{_pct(learn['memory_precision'])}** "
                f"(of the words it learned, how many should it have learned)",
                f"- memory recall: **{_pct(learn['memory_recall'])}** "
                f"(of the words it should have learned, how many did it learn correctly)",
                f"- learned at the wrong confidence tier: {learn['wrong_status']}",
                f"- learned when it should not have: {learn['spurious']}",
                f"- failed to learn: {learn['missing']}",
                f"- state assertions: {state['passed']} passed, {state['failed']} failed",
                "",
                "### Latency, model usage and storage",
                "",
            ]
            lat = kivi["metrics"]["latency"]
            if "not_measured" in lat:
                lines.append(f"- latency: NOT MEASURED ({lat['not_measured']})")
            else:
                e2e, ret = lat["end_to_end_ms"], lat["retrieval_ms"]
                lines += [
                    f"- end-to-end: mean **{_fmt(e2e['mean'])} ms**, p50 {_fmt(e2e['p50'])} ms, "
                    f"p95 {_fmt(e2e['p95'])} ms, max {_fmt(e2e['max'])} ms (n={e2e['n']})",
                    f"- retrieval only: mean **{_fmt(ret['mean'])} ms**, p95 {_fmt(ret['p95'])} ms",
                ]
            usage = kivi["metrics"]["model_usage"]
            if "not_measured" in usage:
                lines.append(f"- model usage: NOT MEASURED — {usage['not_measured']}")
            else:
                lines.append(
                    f"- model usage: {usage['calls']} calls, "
                    f"{usage['tokens_in']} in / {usage['tokens_out']} out tokens, "
                    f"cost **₹{usage['cost_inr']}** ({usage['error_count']} errors)"
                )
            storage = run["storage_after_run"]
            lines += [
                f"- database after the run: **{storage['file_bytes']:,} bytes** "
                f"({storage['page_count']} pages of {storage['page_size']} bytes)",
                f"- row counts: {storage['row_counts']}",
                "",
                "### Pass rate by category",
                "",
                "| category | passed | failed | pass rate |",
                "| --- | --- | --- | --- |",
            ]
            for cat, row in kivi["metrics"]["by_category"].items():
                lines.append(
                    f"| `{cat}` | {row['passed']} | {row['failed']} | {_pct(row['pass_rate'])} |"
                )
            lines.append("")

        lines += [
            f"_Per-case records: `cases-{split}-<system>.jsonl`. "
            f"Every failure in full: `failures-{split}.md`._",
            "",
        ]

    return "\n".join(lines)
