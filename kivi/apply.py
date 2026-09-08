"""Turning candidates into a decision, and the decision into text.

This is where the system decides to act or to stay quiet. The ordering below is
deliberate: every cheap reason to *not* intervene is checked before any reason to
intervene, because a false correction damages text the person got right, while a missed
correction merely leaves it as ASR produced it. The product is not the number of
corrections; it is the absence of the jarring word without collateral damage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import Thresholds
from .retrieval import Candidate
from .text import apply_morphology, match_case, normalize_key, rewrite


@dataclass
class Resolution:
    text: str
    candidates: list[Candidate] = field(default_factory=list)

    @property
    def applied(self) -> list[Candidate]:
        return [c for c in self.candidates if c.action == "applied"]

    @property
    def abstained(self) -> list[Candidate]:
        return [c for c in self.candidates if c.action == "abstained"]

    @property
    def noops(self) -> list[Candidate]:
        return [c for c in self.candidates if c.action == "noop"]

    @property
    def blocked(self) -> list[Candidate]:
        return [c for c in self.candidates if c.action == "blocked"]

    def counts(self) -> dict[str, int]:
        return {
            "applied": len(self.applied),
            "abstained": len(self.abstained),
            "noop": len(self.noops),
            "blocked": len(self.blocked),
        }


def _covering(
    span: tuple[int, int], protected: dict[tuple[int, int], dict[str, Any]]
) -> dict[str, Any] | None:
    """The candidate-held span that CONTAINS this span, if any.

    Containment rather than equality, because the protecting memory is often wider than
    the correction being proposed: mentions of the colleague "Aditya Ghosh" must shield
    the "Aditya" inside them, even though the proposed edit covers only the first token.
    """
    start, end = span
    for (p_start, p_end), holder in protected.items():
        if p_start <= start and end <= p_end:
            return holder
    return None


def _proposed_replacement(cand: Candidate) -> str:
    """The exact string that would replace the span, inflection and casing preserved."""
    canonical = cand.memory["canonical_form"]
    inflected = apply_morphology(canonical, cand.morphology.suffix)

    if cand.span.token_count == 1:
        return match_case(inflected, cand.span.tokens[0])

    # Multi-token: only the tokens that actually differ should move, so that
    # "sarvam kiwi" -> "Sarvam Kivi" rewrites the span while a span that merely
    # contains the memory is left structurally intact (taxonomy A8).
    return inflected


def _is_noop(cand: Candidate) -> bool:
    """Is the span already exactly what we would write?

    Recorded rather than skipped: a system that silently drops no-ops cannot report
    precision, because it has no denominator (taxonomy N8).
    """
    return cand.span.text == _proposed_replacement(cand)


def resolve(
    text: str,
    candidates: list[Candidate],
    th: Thresholds,
    protected: dict[tuple[int, int], dict[str, Any]] | None = None,
) -> Resolution:
    """Gate, disambiguate and de-overlap candidates, then rewrite the text.

    `protected` maps spans that a candidate-status memory already holds as correct. Those
    spans may not be rewritten: weak evidence cannot make a correction, but it is enough
    to doubt one.
    """
    protected = protected or {}
    for cand in candidates:
        cand.replacement = _proposed_replacement(cand)

    # 1. Already correct -> no-op. Checked first: nothing else matters if there is
    #    nothing to change.
    for cand in candidates:
        if _is_noop(cand):
            cand.action = "noop"
            cand.reason_code = "NOOP_ALREADY_CANONICAL"
            cand.reason_text = (
                f"{cand.span.text!r} is already the canonical form of memory "
                f"#{cand.memory_id}; no change made"
            )

    # 1b. If the span already IS some confirmed memory's canonical form, that settles it.
    #     The text is not a mis-hearing of anything — it is a word the system itself holds
    #     as correct. This is taxonomy N4: with colleagues named both "Aaditya" and
    #     "Aditya", the token "Aditya" must not be rewritten to "Aaditya" just because
    #     "Aditya" is also a registered wrong form of it.
    noop_spans = {(c.span.start, c.span.end) for c in candidates if c.action == "noop"}
    for cand in candidates:
        key = (cand.span.start, cand.span.end)
        if cand.action != "noop" and key in noop_spans:
            cand.action = "blocked"
            cand.reason_code = "BLOCKED_SPAN_IS_ANOTHER_CANONICAL"
            cand.reason_text = (
                f"{cand.span.text!r} is already the canonical form of another confirmed "
                f"memory, so it is correct as written and is not a mis-hearing of "
                f"{cand.memory['canonical_form']!r}"
            )
        elif (
            cand.action != "noop"
            and (holder := _covering(key, protected)) is not None
            # A candidate memory inhibits OTHER memories, never itself: otherwise
            # "Amber rail" -> "Amber Rail" was blocked by the very memory proposing it.
            and int(holder["id"]) != cand.memory_id
        ):
            cand.action = "blocked"
            cand.reason_code = "BLOCKED_SPAN_IS_CANDIDATE_CANONICAL"
            cand.reason_text = (
                f"{cand.span.text!r} is the canonical form of candidate memory "
                f"#{holder['id']} ({holder['canonical_form']!r}, confidence "
                f"{float(holder['confidence']):.2f}). That evidence is too weak to make a "
                f"correction of its own, but strong enough to doubt rewriting the word to "
                f"{cand.memory['canonical_form']!r}"
            )

    # 1c. A memory that is not confirmed can never change text (taxonomy N11). It is
    #     retrieved and recorded anyway, so the trace can explain the silence.
    # NOTE: `Candidate.action` defaults to "abstained", so the gate below cannot skip on
    # that value — it would skip everything. Inert candidates are tracked explicitly.
    inert: set[int] = set()
    for idx, cand in enumerate(candidates):
        if cand.action in ("noop", "blocked"):
            continue
        if cand.memory.get("status") != "confirmed":
            inert.add(idx)
            cand.action = "abstained"
            cand.reason_code = "ABSTAIN_MEMORY_CANDIDATE_ONLY"
            cand.reason_text = (
                f"{cand.span.text!r} matches memory #{cand.memory_id} "
                f"({cand.memory['canonical_form']!r}), but that memory is "
                f"{cand.memory['status']} at confidence "
                f"{float(cand.memory['confidence']):.2f}. Only confirmed memories may "
                f"change text, so the evidence is recorded and nothing is rewritten"
            )

    # 2. The context gate.
    for idx, cand in enumerate(candidates):
        if cand.action in ("noop", "blocked") or idx in inert:
            continue
        ctx = cand.context
        if ctx is None:
            continue
        if ctx.vetoed:
            cand.action = "abstained"
            cand.reason_code = "ABSTAIN_METALINGUISTIC"
            cand.reason_text = ctx.veto_reason or "vetoed by context"
        elif not ctx.passed:
            cand.action = "abstained"
            cand.reason_code = (
                "ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK" if ctx.is_ordinary
                else "ABSTAIN_CONTEXT_WEAK"
            )
            cand.reason_text = (
                f"context score {ctx.score:.2f} did not reach the {ctx.required:.2f} "
                f"required here — {ctx.signals.get('bar_reason', '')}"
            )
        else:
            cand.action = "applied"
            cand.reason_code = {
                "exact": "APPLIED_EXACT",
                "variant": "APPLIED_VARIANT_EXACT",
                "phonetic": "APPLIED_PHONETIC_CONTEXT_OK",
                "fuzzy": "APPLIED_FUZZY_CONTEXT_OK",
                "llm": "APPLIED_LLM_ADJUDICATED",
            }[cand.match_tier]
            cand.reason_text = (
                f"{cand.span.text!r} matched memory #{cand.memory_id} "
                f"({cand.memory['canonical_form']!r}) on the {cand.match_tier} tier "
                f"(lexical {cand.lexical_score:.2f}, phonetic {cand.phonetic_score:.2f}); "
                f"context scored {ctx.score:.2f} against a {ctx.required:.2f} bar"
            )

    # 3. Competing memories for the same span. Two plausible answers that are close
    #    together is ambiguity, and the honest response is to do nothing and say so
    #    (taxonomy N12) rather than to pick the marginally higher score.
    by_span: dict[tuple[int, int], list[Candidate]] = {}
    for cand in candidates:
        if cand.action == "applied":
            by_span.setdefault((cand.span.start, cand.span.end), []).append(cand)
    for group in by_span.values():
        if len(group) < 2:
            continue
        distinct = {c.memory_id: c for c in group}
        if len(distinct) < 2:
            continue
        ranked = sorted(distinct.values(), key=lambda c: -c.final_score)
        if ranked[0].final_score - ranked[1].final_score < th.ambiguity_margin:
            names = ", ".join(
                f"#{c.memory_id} {c.memory['canonical_form']!r} ({c.final_score:.2f})"
                for c in ranked
            )
            for cand in group:
                cand.action = "abstained"
                cand.reason_code = "ABSTAIN_AMBIGUOUS_COMPETING"
                cand.reason_text = (
                    f"{len(distinct)} memories compete for {cand.span.text!r} within "
                    f"{th.ambiguity_margin:.2f} of each other ({names}); the system "
                    f"abstains rather than guess"
                )

    # 4. Overlapping spans: the longest wins, so "Aaditya Labs" beats "Aaditya".
    applied = sorted(
        (c for c in candidates if c.action == "applied"),
        key=lambda c: (-c.span.token_count, -c.final_score, c.span.start),
    )
    taken: list[Candidate] = []
    for cand in applied:
        clash = next(
            (t for t in taken if not (cand.span.end <= t.span.start or cand.span.start >= t.span.end)),
            None,
        )
        if clash is None:
            taken.append(cand)
        else:
            cand.action = "blocked"
            cand.reason_code = "BLOCKED_OVERLAPPING_SPAN"
            cand.reason_text = (
                f"overlaps the wider match {clash.span.text!r} -> "
                f"{clash.replacement!r} (memory #{clash.memory_id}), which took precedence"
            )

    # 5. Same memory, same replacement, two readings of one span: keep one.
    deduped: list[Candidate] = []
    seen: set[tuple[int, int, int]] = set()
    for cand in sorted(taken, key=lambda c: (c.span.start, -c.final_score)):
        key = (cand.memory_id, cand.span.start, cand.span.end)
        if key in seen:
            cand.action = "blocked"
            cand.reason_code = "BLOCKED_DUPLICATE_READING"
            cand.reason_text = "another morphological reading of the same span was applied"
            continue
        seen.add(key)
        deduped.append(cand)

    edits = [(c.span.start, c.span.end, c.replacement) for c in deduped]
    return Resolution(text=rewrite(text, edits), candidates=candidates)


def memory_prompt_block(candidates: list[Candidate]) -> str:
    """The retrieved memories, rendered for injection into the formatting prompt.

    The brief states that relevant memory should be "found and placed into the formatting
    prompt when the person speaks again", so this is that placement. Only gate-passing
    candidates are offered, and each carries its evidence, so the model is being told what
    the system already concluded rather than asked to re-derive it.
    """
    rows: list[str] = []
    for cand in candidates:
        if cand.action not in ("applied", "noop"):
            continue
        mem = cand.memory
        gloss = f" — {mem['gloss']}" if mem.get("gloss") else ""
        rows.append(
            f"- heard {cand.span.text!r} -> write \"{cand.replacement}\" "
            f"({mem['word_type']}{gloss}; confidence {float(mem['confidence']):.2f})"
        )
    if not rows:
        return "(no personal vocabulary is relevant to this transcript)"
    return "\n".join(rows)
