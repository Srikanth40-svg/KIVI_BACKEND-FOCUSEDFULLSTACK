"""Retrieval: which stored memory could this heard span be?

**No vector database and no embeddings**, and the reason is not budget. The question here
is "which stored span could this heard span *be*" — an identity question about surface and
sound. Embeddings answer a different question, semantic relatedness, and on this exact
problem they answer it wrongly: "Kivi" and "kiwi" are semantically *unrelated* (a product
and a fruit) yet they are the pair we must link, while "kiwi" and "mango" are semantically
close and must never be linked. A similarity-only baseline is measured in `eval/` rather
than dismissed by assertion.

Four tiers, cheapest first:

  1. ``exact``    — the span's normalised or space-collapsed key equals a stored form.
                    Indexed. Catches taxonomy A4 ("open ai" -> "OpenAI") and every variant
                    the system has already been taught.
  2. ``variant``  — same query, matched against a learned wrong form ("kiwi" -> "Kivi").
  3. ``phonetic`` — the span's phonetic code equals a stored code. Indexed.
  4. ``fuzzy``    — bounded comparison over the confirmed vocabulary for novel ASR errors.

Tiers 1-3 are indexed SQL ``IN`` queries built from every span at once, so the cost is a
constant number of round-trips regardless of sentence length. Tier 4 needs a scan; it is
bounded by a cheap blocking filter and by the fact that one person's personal vocabulary is
small. The measured cost of that scan is reported in eval/results/ rather than assumed.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any

from . import memory as mem_mod
from .config import Thresholds
from .context import ContextAssessment, assess
from .phonetics import DEFAULT_ENCODER, encode, jaro_winkler, phonetic_similarity
from .text import (
    Morphology,
    Span,
    morphology_candidates,
    normalize_compact,
    normalize_key,
    spans,
)

# Identity floor for a near-miss to be recorded in the decision trace. Below this a span is
# simply unrelated and logging it would bury the interesting rows in noise.
NEAR_MISS_FLOOR = 0.55


@dataclass
class Candidate:
    span: Span
    memory: dict[str, Any]
    variant: dict[str, Any]
    match_tier: str
    lexical_score: float
    phonetic_score: float
    identity_score: float
    morphology: Morphology
    replacement: str = ""
    context: ContextAssessment | None = None
    final_score: float = 0.0
    action: str = "abstained"
    reason_code: str = "ABSTAIN_BELOW_SIMILARITY"
    reason_text: str = ""
    signals: dict[str, Any] = field(default_factory=dict)

    @property
    def memory_id(self) -> int:
        return int(self.memory["id"])


# ----------------------------------------------------------------------------------------
# Query key construction
# ----------------------------------------------------------------------------------------

@dataclass(frozen=True)
class SpanQuery:
    span: Span
    morphology: Morphology
    key: str            # normalised lookup key for this reading
    compact: str        # space-collapsed key (taxonomy A4)
    phonetic: str


def span_queries(text: str, max_tokens: int, encoder: str = DEFAULT_ENCODER) -> list[SpanQuery]:
    """Every (span, morphological reading) pair worth looking up.

    Inflections are enumerated rather than guessed (see text.morphology_candidates): a
    plural or possessive ending is only ever stripped when doing so reveals a real memory,
    so morphology handling cannot itself cause a false match.
    """
    out: list[SpanQuery] = []
    for span in spans(text, max_tokens=max_tokens):
        readings: list[Morphology]
        if span.token_count == 1:
            readings = morphology_candidates(span.tokens[0])
        else:
            # Only the last token of a multi-word span can carry the inflection
            # ("Aaditya Labs'"), so vary that and keep the rest verbatim.
            readings = []
            for m in morphology_candidates(span.tokens[-1]):
                stem_text = " ".join([*span.tokens[:-1], m.stem])
                readings.append(Morphology(stem=stem_text, suffix=m.suffix))
        for reading in readings:
            key = normalize_key(reading.stem)
            if not key:
                continue
            out.append(
                SpanQuery(
                    span=span,
                    morphology=reading,
                    key=key,
                    compact=normalize_compact(reading.stem),
                    phonetic=encode(reading.stem, encoder),
                )
            )
    return out


# ----------------------------------------------------------------------------------------
# Database lookups
# ----------------------------------------------------------------------------------------

_VARIANT_JOIN = """
    SELECT m.*, v.id AS variant_id, v.variant_form, v.variant_normalized,
           v.variant_phonetic, v.kind AS variant_kind
    FROM memory_variants v
    JOIN word_memories m ON m.id = v.memory_id
    WHERE m.user_id = ? AND m.status = 'confirmed'
"""


def _split(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    variant = {
        "id": row.pop("variant_id"),
        "variant_form": row.pop("variant_form"),
        "variant_normalized": row.pop("variant_normalized"),
        "variant_phonetic": row.pop("variant_phonetic"),
        "kind": row.pop("variant_kind"),
    }
    return row, variant


def _fetch_by_normalized(
    conn: sqlite3.Connection, user_id: str, keys: set[str]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    if not keys:
        return []
    marks = ",".join("?" for _ in keys)
    rows = conn.execute(
        _VARIANT_JOIN + f" AND v.variant_normalized IN ({marks})", (user_id, *keys)
    ).fetchall()
    return [_split(dict(r)) for r in rows]


def _fetch_by_phonetic(
    conn: sqlite3.Connection, user_id: str, codes: set[str]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    if not codes:
        return []
    marks = ",".join("?" for _ in codes)
    rows = conn.execute(
        _VARIANT_JOIN + f" AND v.variant_phonetic IN ({marks})", (user_id, *codes)
    ).fetchall()
    return [_split(dict(r)) for r in rows]


def _fetch_all_confirmed(
    conn: sqlite3.Connection, user_id: str
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    rows = conn.execute(_VARIANT_JOIN, (user_id,)).fetchall()
    return [_split(dict(r)) for r in rows]


_CANDIDATE_VARIANT_JOIN = """
    SELECT m.*, v.id AS variant_id, v.variant_form, v.variant_normalized,
           v.variant_phonetic, v.kind AS variant_kind
    FROM memory_variants v
    JOIN word_memories m ON m.id = v.memory_id
    WHERE m.user_id = ? AND m.status = 'candidate'
"""


def _fetch_candidate_matches(
    conn: sqlite3.Connection, user_id: str, keys: set[str], codes: set[str]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Candidate-status memories that WOULD have matched, had they been confirmed.

    Retrieved purely so the decision trace can say so. A silent system is not an
    inspectable one: "why didn't Kivi correct this?" deserves the answer "because that
    memory is still a candidate", not an empty list. These never change text.
    """
    out: list[tuple[dict[str, Any], dict[str, Any]]] = []
    seen: set[int] = set()
    for column, values in (("v.variant_normalized", keys), ("v.variant_phonetic", codes)):
        if not values:
            continue
        marks = ",".join("?" for _ in values)
        rows = conn.execute(
            _CANDIDATE_VARIANT_JOIN + f" AND {column} IN ({marks})", (user_id, *values)
        ).fetchall()
        for row in rows:
            pair = _split(dict(row))
            if pair[1]["id"] not in seen:
                seen.add(pair[1]["id"])
                out.append(pair)
    return out


def _fetch_candidate_canonicals(
    conn: sqlite3.Connection, user_id: str, keys: set[str]
) -> list[dict[str, Any]]:
    """Candidate-status memories whose canonical form appears verbatim in the text.

    Candidates may not change text — that is taxonomy N11 and the whole point of having a
    weak tier. But they are still evidence that a word is *already right*, and evidence
    strong enough to doubt a rewrite is much weaker than evidence strong enough to make
    one. Without this asymmetry, a colleague called "Aditya" (candidate) was rewritten to
    "Aaditya" (confirmed) simply because the confirmed memory listed "Aditya" as one of
    its wrong forms.

    So candidates get one power only: to inhibit.
    """
    if not keys:
        return []
    marks = ",".join("?" for _ in keys)
    rows = conn.execute(
        "SELECT * FROM word_memories WHERE user_id = ? AND status = 'candidate' "
        f"AND normalized_key IN ({marks})",
        (user_id, *keys),
    ).fetchall()
    return [dict(r) for r in rows]


# ----------------------------------------------------------------------------------------
# Identity scoring / admission
# ----------------------------------------------------------------------------------------

def _identity(
    query: SpanQuery, variant: dict[str, Any], th: Thresholds, memory_type: str = ""
) -> tuple[str, float, float, float] | None:
    """Decide whether this (span-reading, stored-form) pair is admissible.

    Returns (tier, lexical, phonetic, identity) or None. Two independent signals are used
    because they fail differently: an exact key match needs no phonetic support, and a
    phonetic hit still needs *some* spelling proximity or "eight" would match "ate".
    """
    v_norm = variant["variant_normalized"]
    v_compact = v_norm.replace(" ", "")
    lexical = jaro_winkler(query.compact, v_compact)
    phon = phonetic_similarity(query.phonetic, variant["variant_phonetic"])

    if query.key == v_norm or query.compact == v_compact:
        tier = "exact" if variant["kind"] == "canonical" else "variant"
        return tier, 1.0, phon, 1.0

    # A handle is a strict identifier, not a word. Nobody mis-hears "@aaditya_k" into
    # ordinary English; they dictate a describable form ("at aaditya underscore k") which
    # is stored as a variant and matched exactly above. Allowing inexact tiers to match
    # INTO a handle only invents corrections — it scored "Ask Aditya" against "@aaditya_k"
    # at 0.90 lexical similarity.
    if memory_type == "handle":
        return None

    if query.phonetic and query.phonetic == variant["variant_phonetic"]:
        if lexical >= th.phonetic_min_lexical:
            return "phonetic", lexical, 1.0, 0.6 * lexical + 0.4 * 1.0
        return None

    # Length guard for the inexact tiers. Jaro-Winkler is length-normalised and rewards a
    # shared prefix, which makes very short strings score deceptively well against long
    # ones: "a" vs "aaditya" reaches 0.74 and was being admitted. A one- or two-letter
    # token is never a mis-hearing of a personal name, so require real length agreement.
    shorter, longer = sorted((len(query.compact), len(v_compact)))
    if shorter < 4 or shorter / longer < 0.6:
        return None

    # Token-count agreement for the fuzzy tier. The exact and phonetic-equality tiers are
    # allowed to cross token counts, because there the evidence is strong: a learned
    # variant ("Cuban Eighties" -> Kubernetes) or an identical phonetic code ("red is" ->
    # Redis). Cold *fuzzy* matching across counts has no such evidence, and measurably
    # invents matches — it turned "Ask Aditya" into "@aaditya_k" and "I ate a" into
    # "Aaditya", because gluing function words together produces a long enough string to
    # clear a length-normalised similarity threshold.
    v_tokens = v_norm.count(" ") + 1
    if query.span.token_count != v_tokens:
        return None

    # Novel ASR errors: either strong sound agreement with moderate spelling agreement
    # (multi-token collapses like "cuban eighties" -> "Kubernetes"), or strong spelling
    # agreement on its own.
    if phon >= 0.80 and lexical >= 0.60:
        return "fuzzy", lexical, phon, 0.6 * lexical + 0.4 * phon
    if lexical >= th.fuzzy_min_lexical:
        return "fuzzy", lexical, phon, 0.6 * lexical + 0.4 * phon
    return None


def _blocking_admits(query: SpanQuery, variant: dict[str, Any]) -> bool:
    """Cheap filter before the O(len) comparisons in the fuzzy tier."""
    qp, vp = query.phonetic, variant["variant_phonetic"]
    if not qp or not vp:
        return False
    if abs(len(qp) - len(vp)) > 3:
        return False
    return qp[0] == vp[0] or query.compact[:1] == variant["variant_normalized"][:1]


# ----------------------------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------------------------

def retrieve(
    conn: sqlite3.Connection,
    text: str,
    *,
    user_id: str = "default",
    th: Thresholds,
    app_context: str | None = None,
    encoder: str = DEFAULT_ENCODER,
) -> tuple[list[Candidate], dict[str, Any], dict[tuple[int, int], dict[str, Any]]]:
    """Find and gate every candidate correction for `text`.

    Returns (candidates, diagnostics, protected_spans). Candidates include the ones that
    were rejected: abstentions and no-ops are recorded, because a system that only logs
    its interventions cannot have its precision measured. `protected_spans` are spans a
    candidate-status memory already holds as correct, which may inhibit a correction but
    never cause one.
    """
    max_n = min(mem_mod.max_token_count(conn, user_id), th.max_span_tokens)
    queries = span_queries(text, max_n, encoder)

    keys = {q.key for q in queries} | {q.compact for q in queries}
    codes = {q.phonetic for q in queries if q.phonetic}

    exactish = _fetch_by_normalized(conn, user_id, keys)
    phonetish = _fetch_by_phonetic(conn, user_id, codes)

    # Tier 4 only needs the vocabulary that the indexed tiers did not already resolve.
    already = {(m["id"], v["id"]) for m, v in (*exactish, *phonetish)}
    all_confirmed = _fetch_all_confirmed(conn, user_id)
    fuzzy_pool = [(m, v) for m, v in all_confirmed if (m["id"], v["id"]) not in already]

    profiles: dict[int, set[str]] = {}
    candidates: list[Candidate] = []
    seen: set[tuple[int, int, int, str]] = set()   # (memory, span start, span end, suffix)

    def consider(query: SpanQuery, m: dict[str, Any], v: dict[str, Any]) -> None:
        verdict = _identity(query, v, th, m["word_type"])
        if verdict is None:
            return
        tier, lexical, phon, identity = verdict
        dedupe = (int(m["id"]), query.span.start, query.span.end, query.morphology.suffix)
        if dedupe in seen:
            return
        seen.add(dedupe)

        if m["id"] not in profiles:
            profiles[int(m["id"])] = mem_mod.context_profile(
                conn, int(m["id"]), stopword_rank=th.ctx_profile_stopword_rank
            )

        ctx = assess(
            text=text, span=query.span, memory=m, variant_kind=v["kind"],
            profile=profiles[int(m["id"])], app_context=app_context, th=th,
            match_tier=tier,
        )
        candidates.append(
            Candidate(
                span=query.span, memory=m, variant=v, match_tier=tier,
                lexical_score=lexical, phonetic_score=phon, identity_score=identity,
                morphology=query.morphology, context=ctx,
                final_score=0.7 * identity + 0.3 * ctx.score,
                signals=ctx.signals,
            )
        )

    inert = _fetch_candidate_matches(conn, user_id, keys, codes)

    for query in queries:
        for m, v in exactish:
            if query.key == v["variant_normalized"] or query.compact == v["variant_normalized"].replace(" ", ""):
                consider(query, m, v)
        for m, v in phonetish:
            if query.phonetic == v["variant_phonetic"]:
                consider(query, m, v)
        for m, v in fuzzy_pool:
            if _blocking_admits(query, v):
                consider(query, m, v)
        for m, v in inert:
            if (
                query.key == v["variant_normalized"]
                or (query.phonetic and query.phonetic == v["variant_phonetic"])
            ):
                consider(query, m, v)

    # Spans that a candidate-status memory already holds as correct.
    protected: dict[tuple[int, int], dict[str, Any]] = {}
    for cand_mem in _fetch_candidate_canonicals(conn, user_id, keys):
        for query in queries:
            if query.morphology.suffix:
                continue
            if query.key == cand_mem["normalized_key"]:
                protected[(query.span.start, query.span.end)] = cand_mem

    diagnostics = {
        "spans_considered": len({(q.span.start, q.span.end) for q in queries}),
        "span_readings": len(queries),
        "max_span_tokens": max_n,
        "vocabulary_confirmed_forms": len(all_confirmed),
        "fuzzy_pool_size": len(fuzzy_pool),
        "indexed_hits": len(exactish) + len(phonetish),
        "protected_spans": [
            {"span": text[s:e], "memory_id": m["id"], "canonical_form": m["canonical_form"]}
            for (s, e), m in protected.items()
        ],
    }
    return candidates, diagnostics, protected


def near_misses(
    conn: sqlite3.Connection,
    text: str,
    *,
    user_id: str = "default",
    th: Thresholds,
    encoder: str = DEFAULT_ENCODER,
    exclude: set[tuple[int, int, int]] | None = None,
) -> list[Candidate]:
    """Spans that came close but were not admitted, for the decision trace.

    Recording these is what lets a reviewer see that "the kitty is asleep" was examined
    against `Kivi` and rejected on similarity, rather than never considered at all.
    """
    exclude = exclude or set()
    max_n = min(mem_mod.max_token_count(conn, user_id), th.max_span_tokens)
    out: list[Candidate] = []
    pool = _fetch_all_confirmed(conn, user_id)
    for query in span_queries(text, max_n, encoder):
        if query.morphology.suffix:
            continue     # one reading per span is enough for a diagnostic row
        for m, v in pool:
            if v["kind"] != "canonical":
                continue
            key = (int(m["id"]), query.span.start, query.span.end)
            if key in exclude:
                continue
            lexical = jaro_winkler(query.compact, v["variant_normalized"].replace(" ", ""))
            phon = phonetic_similarity(query.phonetic, v["variant_phonetic"])
            identity = 0.6 * lexical + 0.4 * phon
            if NEAR_MISS_FLOOR <= identity and _identity(query, v, th, m["word_type"]) is None:
                out.append(
                    Candidate(
                        span=query.span, memory=m, variant=v, match_tier="fuzzy",
                        lexical_score=lexical, phonetic_score=phon, identity_score=identity,
                        morphology=query.morphology, final_score=identity * 0.7,
                        action="abstained", reason_code="ABSTAIN_BELOW_SIMILARITY",
                        reason_text=(
                            f"closest memory {m['canonical_form']!r} scored "
                            f"lexical {lexical:.2f} / phonetic {phon:.2f}, below the "
                            f"admission floor, so this span was left alone"
                        ),
                        signals={"lexical": round(lexical, 3), "phonetic": round(phon, 3)},
                    )
                )
                exclude.add(key)
    return out
