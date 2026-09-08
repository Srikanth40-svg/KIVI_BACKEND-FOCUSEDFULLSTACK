"""Metrics.

The brief asks for useful interventions to be reported **separately** from unnecessary or
incorrect ones, so the central table is a 2x2 over "did the system change the text" against
"should it have":

                        should change          should not change
    changed         correct_intervention    FALSE intervention
    left alone      MISSED intervention     correct silence

From that everything else follows. Two definitions worth stating because they are easy to
fudge:

  * A changed text only counts as a *correct* intervention if it equals the gold text
    exactly. Changing the right word to the wrong thing is a false intervention, not a
    partial success.
  * Correct silence is counted, not discarded. It is the denominator that makes false
    intervention rate meaningful, and it is a large share of real dictation.

Metrics that were not measured are reported as `null` with a `not_measured` note, never as
zero (§46).
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ApplyCounters:
    correct_intervention: int = 0
    false_intervention: int = 0
    missed_intervention: int = 0
    correct_silence: int = 0
    acted_but_wrong_text: int = 0   # acted, was right to act, but produced the wrong text

    @property
    def total(self) -> int:
        return (
            self.correct_intervention
            + self.false_intervention
            + self.missed_intervention
            + self.correct_silence
            + self.acted_but_wrong_text
        )

    @property
    def acted(self) -> int:
        return (
            self.correct_intervention
            + self.false_intervention
            + self.acted_but_wrong_text
        )

    @property
    def should_have_acted(self) -> int:
        return (
            self.correct_intervention
            + self.missed_intervention
            + self.acted_but_wrong_text
        )

    def as_dict(self) -> dict[str, Any]:
        def ratio(num: int, den: int) -> float | None:
            return round(num / den, 4) if den else None

        return {
            "cases": self.total,
            "correct_intervention": self.correct_intervention,
            "false_intervention": self.false_intervention,
            "missed_intervention": self.missed_intervention,
            "correct_silence": self.correct_silence,
            "acted_but_wrong_text": self.acted_but_wrong_text,
            # Of the changes it made, how many were right?
            "correction_precision": ratio(self.correct_intervention, self.acted),
            # Of the changes it should have made, how many did it make?
            "correction_recall": ratio(self.correct_intervention, self.should_have_acted),
            # How often did it damage text that was already correct?
            "false_intervention_rate": ratio(
                self.false_intervention, self.false_intervention + self.correct_silence
            ),
            "missed_intervention_rate": ratio(
                self.missed_intervention, self.should_have_acted
            ),
            "exact_text_accuracy": ratio(
                self.correct_intervention + self.correct_silence, self.total
            ),
        }


@dataclass
class LearnCounters:
    correct: int = 0            # expected memory in expected status
    wrong_status: int = 0       # learned, but at the wrong confidence tier
    missing: int = 0            # should have been learned, was not
    spurious: int = 0           # should NOT exist, but does

    def as_dict(self) -> dict[str, Any]:
        total = self.correct + self.wrong_status + self.missing + self.spurious
        learned = self.correct + self.wrong_status + self.spurious
        should = self.correct + self.wrong_status + self.missing

        def ratio(num: int, den: int) -> float | None:
            return round(num / den, 4) if den else None

        return {
            "assertions": total,
            "correct": self.correct,
            "wrong_status": self.wrong_status,
            "missing": self.missing,
            "spurious": self.spurious,
            # Of the words it learned, how many were words it should have learned?
            "memory_precision": ratio(self.correct, learned),
            # Of the words it should have learned, how many did it learn correctly?
            "memory_recall": ratio(self.correct, should),
        }


@dataclass
class Aggregate:
    apply: ApplyCounters = field(default_factory=ApplyCounters)
    learn: LearnCounters = field(default_factory=LearnCounters)
    state_passed: int = 0
    state_failed: int = 0
    latencies_ms: list[float] = field(default_factory=list)
    retrieval_ms: list[float] = field(default_factory=list)
    llm_calls: int = 0
    llm_tokens_in: int = 0
    llm_tokens_out: int = 0
    llm_cost_inr: float = 0.0
    llm_errors: list[str] = field(default_factory=list)
    by_category: dict[str, dict[str, int]] = field(default_factory=dict)

    def note_category(self, category: str, passed: bool) -> None:
        row = self.by_category.setdefault(category, {"passed": 0, "failed": 0})
        row["passed" if passed else "failed"] += 1

    def latency_summary(self) -> dict[str, Any]:
        def pct(values: list[float], q: float) -> float | None:
            if not values:
                return None
            ordered = sorted(values)
            idx = min(len(ordered) - 1, int(q * len(ordered)))
            return round(ordered[idx], 3)

        if not self.latencies_ms:
            return {"not_measured": "no apply cases ran"}
        return {
            "end_to_end_ms": {
                "n": len(self.latencies_ms),
                "mean": round(statistics.fmean(self.latencies_ms), 3),
                "p50": pct(self.latencies_ms, 0.50),
                "p95": pct(self.latencies_ms, 0.95),
                "max": round(max(self.latencies_ms), 3),
            },
            "retrieval_ms": {
                "n": len(self.retrieval_ms),
                "mean": round(statistics.fmean(self.retrieval_ms), 3) if self.retrieval_ms else None,
                "p50": pct(self.retrieval_ms, 0.50),
                "p95": pct(self.retrieval_ms, 0.95),
                "max": round(max(self.retrieval_ms), 3) if self.retrieval_ms else None,
            },
        }

    def model_summary(self, llm_available: bool) -> dict[str, Any]:
        if not llm_available:
            return {
                "not_measured": "SARVAM_API_KEY was not set for this run; no model calls "
                                "were made and no model cost was incurred",
                "calls": 0,
            }
        return {
            "calls": self.llm_calls,
            "tokens_in": self.llm_tokens_in,
            "tokens_out": self.llm_tokens_out,
            "cost_inr": round(self.llm_cost_inr, 4),
            "errors": self.llm_errors[:10],
            "error_count": len(self.llm_errors),
        }

    def as_dict(self, *, llm_available: bool) -> dict[str, Any]:
        return {
            "application": self.apply.as_dict(),
            "learning": self.learn.as_dict(),
            "state_assertions": {"passed": self.state_passed, "failed": self.state_failed},
            "latency": self.latency_summary(),
            "model_usage": self.model_summary(llm_available),
            "by_category": {
                k: {**v, "pass_rate": round(v["passed"] / (v["passed"] + v["failed"]), 4)}
                for k, v in sorted(self.by_category.items())
                if (v["passed"] + v["failed"])
            },
        }


def classify_apply(
    *, expected_intervention: str, expected_text: str, input_text: str, actual_text: str
) -> tuple[str, bool]:
    """Place one apply case in the 2x2. Returns (outcome, passed)."""
    changed = actual_text != input_text
    should_change = expected_intervention == "correct"

    if should_change and changed:
        if actual_text == expected_text:
            return "correct_intervention", True
        return "acted_but_wrong_text", False
    if should_change and not changed:
        return "missed_intervention", False
    if not should_change and changed:
        return "false_intervention", False
    return "correct_silence", True
