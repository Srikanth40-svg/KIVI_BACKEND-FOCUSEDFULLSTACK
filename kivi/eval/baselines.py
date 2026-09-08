"""Baselines, so that every piece of complexity has to earn its place with a number.

The full system is a four-tier retrieval cascade plus a context gate. That is more
machinery than a dictionary replace, and the only honest way to justify it is to run the
simpler things on the same cases and show the difference. Three baselines:

  * ``exact``   — the obvious implementation: every learned wrong form is replaced wherever
                  it appears, with no notion of context. This is what "just add a
                  dictionary" actually does.
  * ``fuzzy``   — exact, plus phonetic/fuzzy matching, still with no context. Tests whether
                  the *matching* is what matters or whether the *gating* is.
  * ``llm_only``— no persistent memory at all: hand the sentence to the model and ask it to
                  fix personal words. Tests the premise of the whole product — whether
                  durable state is needed, or a good model is enough. Requires a key; it is
                  reported as "not measured" when none is present rather than guessed at.

All baselines read the same memory table the full system uses, so the comparison isolates
retrieval and gating rather than accidentally comparing different vocabularies.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from ..config import Config
from ..llm import LLMUsage, SarvamClient
from ..phonetics import DEFAULT_ENCODER, encode, jaro_winkler, phonetic_similarity
from ..text import (
    apply_morphology,
    match_case,
    morphology_candidates,
    normalize_compact,
    normalize_key,
    rewrite,
    spans,
)

BASELINE_NAMES = ("exact", "fuzzy", "llm_only")


def _vocabulary(conn: sqlite3.Connection, user_id: str = "default") -> list[dict[str, Any]]:
    """Confirmed memories with their variants — the same state the full system sees."""
    rows = conn.execute(
        """
        SELECT m.id, m.canonical_form, m.normalized_key, m.phonetic_key, m.token_count,
               v.variant_form, v.variant_normalized, v.variant_phonetic, v.kind
        FROM memory_variants v
        JOIN word_memories m ON m.id = v.memory_id
        WHERE m.user_id = ? AND m.status = 'confirmed'
        """,
        (user_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def _max_tokens(vocab: list[dict[str, Any]]) -> int:
    return max((int(v["token_count"]) for v in vocab), default=1)


def run_exact(
    conn: sqlite3.Connection, text: str, *, user_id: str = "default"
) -> tuple[str, list[dict[str, Any]]]:
    """Replace any exact match of a known wrong form. No context, no gating."""
    vocab = _vocabulary(conn, user_id)
    edits: list[tuple[int, int, str]] = []
    applied: list[dict[str, Any]] = []
    taken: list[tuple[int, int]] = []

    for span in sorted(spans(text, max_tokens=_max_tokens(vocab)), key=lambda s: -s.token_count):
        if any(not (span.end <= a or span.start >= b) for a, b in taken):
            continue
        for reading in morphology_candidates(span.tokens[-1] if span.token_count == 1 else span.text):
            key = normalize_key(
                reading.stem if span.token_count == 1
                else " ".join([*span.tokens[:-1], reading.stem])
            )
            hit = next((v for v in vocab if v["variant_normalized"] == key), None)
            if hit is None:
                continue
            replacement = apply_morphology(hit["canonical_form"], reading.suffix)
            if span.token_count == 1:
                replacement = match_case(replacement, span.tokens[0])
            if replacement == span.text:
                break
            edits.append((span.start, span.end, replacement))
            taken.append((span.start, span.end))
            applied.append(
                {"span": span.text, "replacement": replacement, "memory_id": hit["id"]}
            )
            break
    return rewrite(text, edits), applied


def run_fuzzy(
    conn: sqlite3.Connection,
    text: str,
    *,
    user_id: str = "default",
    min_lexical: float = 0.72,
) -> tuple[str, list[dict[str, Any]]]:
    """Exact plus phonetic and fuzzy matching. Still no context gate."""
    vocab = _vocabulary(conn, user_id)
    edits: list[tuple[int, int, str]] = []
    applied: list[dict[str, Any]] = []
    taken: list[tuple[int, int]] = []

    for span in sorted(spans(text, max_tokens=_max_tokens(vocab)), key=lambda s: -s.token_count):
        if any(not (span.end <= a or span.start >= b) for a, b in taken):
            continue
        best: tuple[float, dict[str, Any], str] | None = None
        for reading in morphology_candidates(span.tokens[-1] if span.token_count == 1 else span.text):
            stem = (
                reading.stem if span.token_count == 1
                else " ".join([*span.tokens[:-1], reading.stem])
            )
            compact = normalize_compact(stem)
            code = encode(stem, DEFAULT_ENCODER)
            if len(compact) < 3:
                continue
            for v in vocab:
                v_compact = v["variant_normalized"].replace(" ", "")
                lexical = jaro_winkler(compact, v_compact)
                phon = phonetic_similarity(code, v["variant_phonetic"])
                if compact == v_compact:
                    score = 1.0
                elif code == v["variant_phonetic"] or phon >= 0.80:
                    score = 0.6 * lexical + 0.4 * phon
                elif lexical >= min_lexical:
                    score = 0.6 * lexical + 0.4 * phon
                else:
                    continue
                if best is None or score > best[0]:
                    best = (score, v, reading.suffix)
        if best is None:
            continue
        _, hit, suffix = best
        replacement = apply_morphology(hit["canonical_form"], suffix)
        if span.token_count == 1:
            replacement = match_case(replacement, span.tokens[0])
        if replacement == span.text:
            continue
        edits.append((span.start, span.end, replacement))
        taken.append((span.start, span.end))
        applied.append({"span": span.text, "replacement": replacement, "memory_id": hit["id"]})
    return rewrite(text, edits), applied


LLM_ONLY_PROMPT = (
    "You are finishing a dictated transcript for one specific person. Correct any "
    "personal names, product names, project names or technical terms that speech "
    "recognition is likely to have mis-transcribed, and leave everything else exactly as "
    "it is. Do not reword, do not change punctuation, and do not add anything. "
    "Return only the final text."
)


def run_llm_only(
    client: SarvamClient | None, text: str
) -> tuple[str, list[dict[str, Any]], LLMUsage]:
    """No memory at all: can a good model do this on its own?"""
    if client is None:
        return text, [{"skipped": "no SARVAM_API_KEY: this baseline was NOT MEASURED"}], LLMUsage()
    result = client.chat(
        [
            {"role": "system", "content": LLM_ONLY_PROMPT},
            {"role": "user", "content": text},
        ],
        max_tokens=400,
    )
    if not result.ok or not result.text:
        return text, [{"error": result.error}], result.usage
    return result.text.strip(), [], result.usage


def run_baseline(
    name: str,
    conn: sqlite3.Connection,
    text: str,
    *,
    config: Config,
    client: SarvamClient | None = None,
    user_id: str = "default",
) -> tuple[str, list[dict[str, Any]], LLMUsage]:
    if name == "exact":
        out, applied = run_exact(conn, text, user_id=user_id)
        return out, applied, LLMUsage()
    if name == "fuzzy":
        out, applied = run_fuzzy(
            conn, text, user_id=user_id, min_lexical=config.thresholds.fuzzy_min_lexical
        )
        return out, applied, LLMUsage()
    if name == "llm_only":
        return run_llm_only(client, text)
    raise ValueError(f"unknown baseline {name!r}")
