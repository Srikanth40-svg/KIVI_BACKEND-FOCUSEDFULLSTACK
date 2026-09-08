"""The optional LLM adjudicator.

Documented per §44, because a model call has to justify itself:

  PURPOSE       Decide the cases where deterministic context scoring is genuinely
                uncertain — the heard word is an ordinary English word and the surrounding
                evidence sits close to the bar. "I ate a kiwi" vs "ship the kiwi update"
                is a judgement about what the sentence *means*, which is the one thing a
                lexicon and a co-occurrence profile cannot do.
  INPUT         The formatted sentence, the span, and the candidate memory with its type
                and gloss. No database contents beyond that, and no chain of prior turns.
  OUTPUT        Strict JSON: one apply/abstain verdict per uncertain span, with a reason.
  WHEN CALLED   Only for candidates inside `ctx_uncertain_band` of the required bar, and
                only when KIVI_USE_LLM_ADJUDICATOR=1. Confident cases never reach it, so
                the common path costs nothing.
  FAILURE MODE  Timeout, non-JSON output, a hallucinated span, or an unavailable key.
  FALLBACK      Any failure keeps the deterministic verdict for that span. A failed call
                can never turn an abstention into a correction.
  BUDGET        One call per request regardless of how many spans are uncertain, so the
                cost is bounded and reported in `decisions.llm_cost_inr`.

It is allowed to *adjudicate*. It is not allowed to *learn*: an LLM opinion is evidence
class E8, which the learning policy rejects by rule. A model can decide whether to apply a
memory the system already earned; it cannot create one.
"""

from __future__ import annotations

from typing import Any

from .config import Thresholds
from .llm import LLMResult, LLMUsage, SarvamClient
from .retrieval import Candidate

ADJUDICATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "apply": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["id", "apply", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["verdicts"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = (
    "You decide whether a personal-vocabulary substitution should be applied to one "
    "sentence of dictated text.\n\n"
    "Apply the substitution only if the sentence is genuinely referring to the person's "
    "personal term. Do NOT apply it if the word is being used in its ordinary everyday "
    "sense, if it refers to a different entity, or if the sentence is talking about the "
    "word itself.\n\n"
    "Example of the distinction: with a memory 'Kivi' (a software product), the sentence "
    "'ship the kiwi update on Friday' refers to the product, but 'I ate a kiwi on the "
    "flight' does not.\n\n"
    "Prefer leaving text unchanged when uncertain: a wrong substitution corrupts text the "
    "person said correctly. Answer with strict JSON only."
)


def uncertain(cand: Candidate, th: Thresholds) -> bool:
    """Is this candidate close enough to the bar that a judgement call would help?"""
    ctx = cand.context
    if ctx is None or ctx.vetoed:
        return False
    return abs(ctx.score - ctx.required) <= th.ctx_uncertain_band


def adjudicate(
    client: SarvamClient,
    text: str,
    candidates: list[Candidate],
    th: Thresholds,
) -> tuple[LLMUsage, list[dict[str, Any]]]:
    """Ask for verdicts on the uncertain candidates and apply them in place.

    Returns (usage, notes). Candidates not in the uncertain band are untouched.
    """
    targets = [c for c in candidates if uncertain(c, th)]
    if not targets:
        return LLMUsage(), []

    lines = []
    for idx, cand in enumerate(targets):
        mem = cand.memory
        gloss = f", {mem['gloss']}" if mem.get("gloss") else ""
        lines.append(
            f"{idx}. heard \"{cand.span.text}\" -> proposed \"{cand.replacement}\" "
            f"(memory: {mem['canonical_form']!r}, a {mem['word_type']}{gloss})"
        )

    result: LLMResult = client.chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Sentence:\n{text}\n\nCandidate substitutions:\n" + "\n".join(lines) +
                    "\n\nReturn a verdict for each id."
                ),
            },
        ],
        json_schema=ADJUDICATION_SCHEMA,
        max_tokens=400,
    )

    notes: list[dict[str, Any]] = []
    if not result.ok or not result.data:
        for cand in targets:
            cand.signals["llm"] = {"consulted": True, "usable": False, "error": result.error}
        notes.append({"error": result.error, "fallback": "kept the deterministic verdict"})
        return result.usage, notes

    verdicts = {int(v["id"]): v for v in result.data.get("verdicts", []) if "id" in v}
    for idx, cand in enumerate(targets):
        verdict = verdicts.get(idx)
        if verdict is None:
            cand.signals["llm"] = {"consulted": True, "usable": False, "error": "no verdict returned"}
            continue

        approved = bool(verdict.get("apply"))
        reason = str(verdict.get("reason", ""))[:400]
        cand.signals["llm"] = {"consulted": True, "usable": True, "apply": approved, "reason": reason}

        if approved and cand.action == "abstained":
            cand.action = "applied"
            cand.match_tier = "llm"
            cand.reason_code = "APPLIED_LLM_ADJUDICATED"
            cand.reason_text = (
                f"deterministic context scored {cand.context.score:.2f} against a "  # type: ignore[union-attr]
                f"{cand.context.required:.2f} bar, inside the uncertain band; the "  # type: ignore[union-attr]
                f"adjudicator judged the sentence to refer to the personal term: {reason}"
            )
        elif not approved and cand.action == "applied":
            cand.action = "abstained"
            cand.reason_code = "ABSTAIN_LLM_DECLINED"
            cand.reason_text = (
                f"deterministic gating would have applied this, but the adjudicator judged "
                f"the sentence not to refer to the personal term: {reason}"
            )
        notes.append({"span": cand.span.text, "apply": approved, "reason": reason})

    return result.usage, notes
