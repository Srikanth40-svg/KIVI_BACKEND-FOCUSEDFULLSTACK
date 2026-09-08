"""The three-stage pipeline, and the decision record it leaves behind.

    raw ASR  ->  formatted  ->  retrieval  ->  gating / adjudication  ->  memory-aware

Stage 1 is an input (this system does not build ASR). Stage 2 is an input too, or comes
from the stand-in formatter. Stage 3 is what this system produces, and every stage-3 output
writes a `decisions` row plus one `decision_candidates` row per span considered — including
the spans it decided to leave alone.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from typing import Any

from . import db
from . import memory as mem_mod
from .adjudicator import adjudicate
from .apply import Resolution, memory_prompt_block, resolve
from .config import Config
from .formatter import format_stub, memory_aware_messages
from .llm import LLMUsage, SarvamClient
from .retrieval import Candidate, near_misses, retrieve


@dataclass
class PipelineResult:
    asr_text: str | None
    formatted_text: str
    memory_aware_text: str
    decision_id: int | None
    apply_mode: str
    candidates: list[Candidate] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    usage: LLMUsage = field(default_factory=LLMUsage)
    timings: dict[str, float] = field(default_factory=dict)
    notes: list[dict[str, Any]] = field(default_factory=list)

    @property
    def intervened(self) -> bool:
        return self.memory_aware_text != self.formatted_text


def _candidate_payload(cand: Candidate) -> dict[str, Any]:
    ctx = cand.context
    return {
        "memory_id": cand.memory_id,
        "canonical_form": cand.memory["canonical_form"],
        "word_type": cand.memory["word_type"],
        "memory_status": cand.memory["status"],
        "memory_confidence": float(cand.memory["confidence"]),
        "span_text": cand.span.text,
        "span_start": cand.span.start,
        "span_end": cand.span.end,
        "span_token_count": cand.span.token_count,
        "matched_variant": cand.variant.get("variant_form"),
        "matched_variant_kind": cand.variant.get("kind"),
        "match_tier": cand.match_tier,
        "morphology": cand.morphology.suffix or None,
        "replacement": cand.replacement,
        "lexical_score": round(cand.lexical_score, 4),
        "phonetic_score": round(cand.phonetic_score, 4),
        "identity_score": round(cand.identity_score, 4),
        "context_score": round(ctx.score, 4) if ctx else 0.0,
        "required_context": round(ctx.required, 4) if ctx else 0.0,
        "is_ordinary_word": bool(ctx.is_ordinary) if ctx else False,
        "final_score": round(cand.final_score, 4),
        "action": cand.action,
        "reason_code": cand.reason_code,
        "reason_text": cand.reason_text,
        "signals": cand.signals,
    }


def _persist(
    conn: sqlite3.Connection,
    *,
    interaction_id: int | None,
    apply_mode: str,
    asr_text: str | None,
    formatted_text: str,
    memory_aware_text: str,
    resolution: Resolution,
    diagnostics: dict[str, Any],
    usage: LLMUsage,
    timings: dict[str, float],
) -> int:
    counts = resolution.counts()
    decision_id = db.insert(
        conn,
        "decisions",
        {
            "interaction_id": interaction_id,
            "apply_mode": apply_mode,
            "asr_text": asr_text,
            "formatted_text": formatted_text,
            "memory_aware_text": memory_aware_text,
            "retrieval_ms": timings.get("retrieval_ms", 0.0),
            "adjudication_ms": timings.get("adjudication_ms", 0.0),
            "apply_ms": timings.get("apply_ms", 0.0),
            "total_ms": timings.get("total_ms", 0.0),
            "spans_considered": diagnostics.get("spans_considered", 0),
            "candidates_considered": len(resolution.candidates),
            "applied_count": counts["applied"],
            "abstained_count": counts["abstained"],
            "noop_count": counts["noop"],
            "llm_calls": usage.calls,
            "llm_tokens_in": usage.tokens_in,
            "llm_tokens_out": usage.tokens_out,
            "llm_cost_inr": usage.cost_inr,
            "created_at": mem_mod.now_iso(),
        },
    )
    for cand in resolution.candidates:
        ctx = cand.context
        db.insert(
            conn,
            "decision_candidates",
            {
                "decision_id": decision_id,
                "memory_id": cand.memory_id,
                "span_text": cand.span.text,
                "span_start": cand.span.start,
                "span_end": cand.span.end,
                "span_token_count": cand.span.token_count,
                "match_tier": cand.match_tier,
                "lexical_score": cand.lexical_score,
                "phonetic_score": cand.phonetic_score,
                "context_score": ctx.score if ctx else 0.0,
                "required_context": ctx.required if ctx else 0.0,
                "final_score": cand.final_score,
                "is_ordinary_word": 1 if (ctx and ctx.is_ordinary) else 0,
                "action": cand.action,
                "reason_code": cand.reason_code,
                "reason_text": cand.reason_text,
                "signals": json.dumps(cand.signals, default=str),
                "created_at": mem_mod.now_iso(),
            },
        )
    return decision_id


def memory_aware_format(
    conn: sqlite3.Connection,
    config: Config,
    *,
    formatted_text: str | None = None,
    asr_text: str | None = None,
    app_context: str | None = None,
    user_id: str = "default",
    apply_mode: str | None = None,
    client: SarvamClient | None = None,
    interaction_id: int | None = None,
    persist: bool = True,
    include_near_misses: bool = True,
) -> PipelineResult:
    """Produce the memory-aware transcript, with a full inspectable decision trace."""
    started = time.perf_counter()
    th = config.thresholds
    mode = apply_mode or config.apply_mode

    if formatted_text is None:
        if asr_text is None:
            raise ValueError("one of formatted_text or asr_text is required")
        formatted_text = format_stub(asr_text)

    t0 = time.perf_counter()
    candidates, diagnostics, protected = retrieve(
        conn, formatted_text, user_id=user_id, th=th, app_context=app_context
    )
    retrieval_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    resolution = resolve(formatted_text, candidates, th, protected)
    apply_ms = (time.perf_counter() - t0) * 1000

    usage = LLMUsage()
    notes: list[dict[str, Any]] = []
    adjudication_ms = 0.0

    # The adjudicator only sees genuinely uncertain spans, and only if it is switched on.
    if config.use_llm_adjudicator and client is not None:
        t0 = time.perf_counter()
        llm_usage, notes = adjudicate(client, formatted_text, resolution.candidates, th)
        adjudication_ms = (time.perf_counter() - t0) * 1000
        usage.merge(llm_usage)
        if notes:
            # Verdicts can flip actions, so overlap and ambiguity must be settled again.
            resolution = resolve(formatted_text, resolution.candidates, th, protected)

    memory_aware_text = resolution.text

    # The brief's "placed into the formatting prompt" path: the retrieved memories go to
    # the model and the model writes the final text. Measured against the deterministic
    # path rather than assumed better.
    if mode == "prompt":
        if client is None:
            raise ValueError("apply_mode='prompt' requires a Sarvam client")
        block = memory_prompt_block(resolution.candidates)
        result = client.chat(memory_aware_messages(formatted_text, block), max_tokens=600)
        usage.merge(result.usage)
        if result.ok and result.text:
            memory_aware_text = result.text.strip()
            notes.append({"prompt_mode": "model produced the final text", "memory_block": block})
        else:
            notes.append(
                {
                    "prompt_mode": "model call failed; fell back to deterministic application",
                    "error": result.error,
                }
            )

    if include_near_misses:
        already = {(c.memory_id, c.span.start, c.span.end) for c in resolution.candidates}
        resolution.candidates.extend(
            near_misses(conn, formatted_text, user_id=user_id, th=th, exclude=already)
        )

    total_ms = (time.perf_counter() - started) * 1000
    timings = {
        "retrieval_ms": round(retrieval_ms, 3),
        "apply_ms": round(apply_ms, 3),
        "adjudication_ms": round(adjudication_ms, 3),
        "total_ms": round(total_ms, 3),
    }

    decision_id: int | None = None
    if persist:
        decision_id = _persist(
            conn,
            interaction_id=interaction_id,
            apply_mode=mode,
            asr_text=asr_text,
            formatted_text=formatted_text,
            memory_aware_text=memory_aware_text,
            resolution=resolution,
            diagnostics=diagnostics,
            usage=usage,
            timings=timings,
        )
        if interaction_id is not None:
            conn.execute(
                "UPDATE interactions SET memory_aware_text = ? WHERE id = ?",
                (memory_aware_text, interaction_id),
            )

    return PipelineResult(
        asr_text=asr_text,
        formatted_text=formatted_text,
        memory_aware_text=memory_aware_text,
        decision_id=decision_id,
        apply_mode=mode,
        candidates=resolution.candidates,
        diagnostics={**diagnostics, "counts": resolution.counts()},
        usage=usage,
        timings=timings,
        notes=notes,
    )


def explain(result: PipelineResult) -> dict[str, Any]:
    """The full 'why' payload: three stages, every candidate, every score, every reason."""
    return {
        "stages": {
            "asr": result.asr_text,
            "formatted": result.formatted_text,
            "memory_aware": result.memory_aware_text,
        },
        "intervened": result.intervened,
        "decision_id": result.decision_id,
        "apply_mode": result.apply_mode,
        "applied": [_candidate_payload(c) for c in result.candidates if c.action == "applied"],
        # Highest-scoring first: an abstention that nearly fired is far more informative
        # than one that never came close.
        "abstained": [
            _candidate_payload(c)
            for c in sorted(
                (c for c in result.candidates if c.action == "abstained"),
                key=lambda c: -c.final_score,
            )
        ],
        "noop": [_candidate_payload(c) for c in result.candidates if c.action == "noop"],
        "blocked": [_candidate_payload(c) for c in result.candidates if c.action == "blocked"],
        "diagnostics": result.diagnostics,
        "timings": result.timings,
        "model_usage": result.usage.as_dict(),
        "notes": result.notes,
    }


def decision_trace(conn: sqlite3.Connection, decision_id: int) -> dict[str, Any] | None:
    """Reconstruct a past decision from the database alone (GET /api/decisions/:id)."""
    row = db.query_one(conn, "SELECT * FROM decisions WHERE id = ?", (decision_id,))
    if row is None:
        return None
    decision = dict(row)
    cands = db.rows_to_dicts(
        db.query(
            conn,
            "SELECT * FROM decision_candidates WHERE decision_id = ? "
            "ORDER BY span_start, final_score DESC",
            (decision_id,),
        )
    )
    for c in cands:
        try:
            c["signals"] = json.loads(c["signals"]) if c["signals"] else {}
        except (TypeError, json.JSONDecodeError):
            c["signals"] = {}
        mem = mem_mod.get(conn, int(c["memory_id"])) if c["memory_id"] else None
        c["memory"] = mem
    decision["candidates"] = cands
    decision["grouped"] = {
        action: [c for c in cands if c["action"] == action]
        for action in ("applied", "abstained", "noop", "blocked")
    }
    return decision
