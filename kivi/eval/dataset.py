"""Evaluation dataset: schema, loading, validation.

**Gold labels are authored by hand, in the dataset files, before the system runs.** The
runner only ever reads them. Nothing in this package writes to `eval/datasets/`, and the
runner refuses to start if a case is missing its expected result — a system that can supply
its own answers is not being evaluated (§31).

Three kinds of case, because the product makes three different kinds of claim:

  * ``apply``  — given a known memory state, the memory-aware output must equal the gold
                 text, and the intervention flag must match. This is where false and
                 missed interventions are counted.
  * ``learn``  — given a sequence of observations, a named word must end up in a specific
                 status (or must not exist at all). This is where memory precision and
                 recall are counted.
  * ``state``  — after setup, assert something about memory that is not about one word:
                 supersession links, deletion effects, counts.

Every case names a ``scenario``, which fixes the memory state it runs against. The runner
rebuilds each scenario from the committed seed plus the scenario's own setup observations,
so a case's result never depends on which cases ran before it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DATASET_DIR = Path(__file__).resolve().parent.parent.parent / "eval" / "datasets"

CASE_KINDS = {"apply", "learn", "state"}
INTERVENTIONS = {"correct", "none"}


class DatasetError(ValueError):
    pass


@dataclass
class Scenario:
    name: str
    description: str
    from_empty: bool = False
    setup: list[dict[str, Any]] = field(default_factory=list)
    manual_memories: list[dict[str, Any]] = field(default_factory=list)
    post: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Case:
    id: str
    kind: str
    category: str
    scenario: str
    note: str
    raw: dict[str, Any]

    # apply
    formatted_text: str | None = None
    asr_text: str | None = None
    app_context: str | None = None
    expected_text: str | None = None
    expected_intervention: str | None = None
    expected_reason_contains: list[str] = field(default_factory=list)

    # learn
    observations: list[dict[str, Any]] = field(default_factory=list)
    expected_memories: list[dict[str, Any]] = field(default_factory=list)

    # state
    assertions: list[dict[str, Any]] = field(default_factory=list)


def _require(case: dict[str, Any], key: str, cid: str) -> Any:
    if key not in case:
        raise DatasetError(f"case {cid!r}: missing required field {key!r}")
    return case[key]


def parse_case(raw: dict[str, Any]) -> Case:
    cid = raw.get("id") or "<no id>"
    kind = _require(raw, "kind", cid)
    if kind not in CASE_KINDS:
        raise DatasetError(f"case {cid!r}: kind must be one of {sorted(CASE_KINDS)}")

    case = Case(
        id=cid,
        kind=kind,
        category=_require(raw, "category", cid),
        scenario=raw.get("scenario", "seeded"),
        note=raw.get("note", ""),
        raw=raw,
    )

    if kind == "apply":
        expected = _require(raw, "expected", cid)
        case.formatted_text = raw.get("formatted_text")
        case.asr_text = raw.get("asr_text")
        case.app_context = raw.get("app_context")
        if not case.formatted_text and not case.asr_text:
            raise DatasetError(f"case {cid!r}: needs formatted_text or asr_text")
        case.expected_text = _require(expected, "text", cid)
        case.expected_intervention = _require(expected, "intervention", cid)
        if case.expected_intervention not in INTERVENTIONS:
            raise DatasetError(
                f"case {cid!r}: expected.intervention must be one of {sorted(INTERVENTIONS)}"
            )
        # Consistency check on the gold label itself: "none" must mean the text is unchanged.
        source = case.formatted_text
        if source is not None:
            unchanged = case.expected_text == source
            if case.expected_intervention == "none" and not unchanged:
                raise DatasetError(
                    f"case {cid!r}: intervention 'none' but expected text differs from input"
                )
            if case.expected_intervention == "correct" and unchanged:
                raise DatasetError(
                    f"case {cid!r}: intervention 'correct' but expected text equals input"
                )
        case.expected_reason_contains = list(expected.get("reason_contains", []))

    elif kind == "learn":
        case.observations = list(_require(raw, "observations", cid))
        case.expected_memories = list(_require(raw, "expected", cid).get("memories", []))
        if not case.expected_memories:
            raise DatasetError(f"case {cid!r}: learn case needs expected.memories")
        for m in case.expected_memories:
            if "canonical_form" not in m or "status" not in m:
                raise DatasetError(
                    f"case {cid!r}: each expected memory needs canonical_form and status "
                    f"(status may be 'absent')"
                )

    else:  # state
        case.assertions = list(_require(raw, "assertions", cid))
        if not case.assertions:
            raise DatasetError(f"case {cid!r}: state case needs assertions")

    return case


def load_cases(split: str, directory: Path | None = None) -> list[Case]:
    path = (directory or DATASET_DIR) / f"{split}.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"no dataset for split {split!r}: {path}")
    cases: list[Case] = []
    seen: set[str] = set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DatasetError(f"{path}:{lineno}: invalid JSON — {exc}") from exc
        case = parse_case(raw)
        if case.id in seen:
            raise DatasetError(f"{path}:{lineno}: duplicate case id {case.id!r}")
        seen.add(case.id)
        cases.append(case)
    return cases


def load_scenarios(directory: Path | None = None) -> dict[str, Scenario]:
    path = (directory or DATASET_DIR) / "scenarios.json"
    if not path.exists():
        raise FileNotFoundError(f"scenarios file missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, Scenario] = {}
    for name, spec in data.items():
        out[name] = Scenario(
            name=name,
            description=spec.get("description", ""),
            from_empty=bool(spec.get("from_empty", False)),
            setup=list(spec.get("setup", [])),
            manual_memories=list(spec.get("manual_memories", [])),
            post=list(spec.get("post", [])),
        )
    return out


def composition(cases: list[Case]) -> dict[str, Any]:
    """Exact dataset composition, reported rather than described."""
    by_kind: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_scenario: dict[str, int] = {}
    by_intervention: dict[str, int] = {}
    for c in cases:
        by_kind[c.kind] = by_kind.get(c.kind, 0) + 1
        by_category[c.category] = by_category.get(c.category, 0) + 1
        by_scenario[c.scenario] = by_scenario.get(c.scenario, 0) + 1
        if c.expected_intervention:
            by_intervention[c.expected_intervention] = (
                by_intervention.get(c.expected_intervention, 0) + 1
            )
    return {
        "total": len(cases),
        "by_kind": dict(sorted(by_kind.items())),
        "by_expected_intervention": dict(sorted(by_intervention.items())),
        "by_category": dict(sorted(by_category.items())),
        "by_scenario": dict(sorted(by_scenario.items())),
    }
