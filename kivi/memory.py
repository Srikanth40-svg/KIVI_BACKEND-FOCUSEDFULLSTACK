"""The memory store: creation, confidence, promotion, supersession, deletion.

Every mutation writes a `memory_events` row, so "why does this memory exist", "why did its
confidence change" and "what did it used to say" are all answerable from the database
rather than from a narrative in a README.

Two kinds of memory, worth naming because they have different value:

  * **curative** memories come from a correction (evidence E1/E2/E3). The system got a word
    wrong, was told, and now fixes it. These start life already `confirmed`.
  * **prophylactic** memories come from repetition (E4) of a word ASR already transcribes
    correctly ("Sarvam", "Kshatriya", "EPD"). Nothing is broken yet. Storing them buys two
    things: the word's casing/joining becomes canonical (taxonomy A4), and a phonetic key
    now exists, so the *next* time ASR mis-hears it the error is caught.

That distinction is why repetition is allowed to create memories at all while still obeying
RULE 5: a repeated word is only learned when it is already correct, so learning it can
never itself introduce an error.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

from . import db
from .config import Thresholds
from .lexicon import rank as word_rank
from .phonetics import DEFAULT_ENCODER, encode
from .text import normalize_key, tokenize

LIVE_STATUSES = ("candidate", "confirmed")
APPLICABLE_STATUSES = ("confirmed",)   # only confirmed memories may change text (taxonomy N11)

EVIDENCE_CLASS = {
    "manual_entry": "authoritative",
    "user_spelling": "authoritative",
    "user_edit": "authoritative",
    "repetition": "corroborating",
    "naming_frame": "suggestive",
    "app_context": "weak",
    "irrealis": "insufficient",
    "llm_only": "insufficient",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"


@dataclass(frozen=True)
class MemoryKeys:
    canonical: str
    normalized: str
    phonetic: str
    token_count: int


def build_keys(canonical: str, *, encoder: str = DEFAULT_ENCODER) -> MemoryKeys:
    norm = normalize_key(canonical)
    return MemoryKeys(
        canonical=canonical,
        normalized=norm,
        phonetic=encode(canonical, encoder),
        token_count=max(1, len(tokenize(canonical))),
    )


# ----------------------------------------------------------------------------------------
# Confidence
# ----------------------------------------------------------------------------------------

def evidence_weight(evidence_type: str, th: Thresholds) -> float:
    return {
        "manual_entry": th.w_manual_entry,
        "user_spelling": th.w_user_spelling,
        "user_edit": th.w_user_edit,
        "repetition": th.w_repetition_step,
        "naming_frame": th.w_naming_frame,
        "app_context": th.w_app_context,
        "irrealis": 0.0,
        "llm_only": 0.0,
    }[evidence_type]


def compute_confidence(evidence: Iterable[dict[str, Any]], th: Thresholds) -> tuple[float, str]:
    """Confidence from the full evidence set, plus a human-readable explanation.

    Policy, in order:
      1. Any *authoritative* evidence (the user told us, or fixed our output) sets
         confidence directly. Nothing else can outrank being told.
      2. Otherwise evidence is additive: a suggestive base, plus repetition across
         SEPARATE interactions, plus a hard-capped weak contribution from app context.
      3. Non-authoritative evidence is capped below certainty, so a word can never become
         permanent just by being said a lot.
    """
    rows = list(evidence)
    auth = [r for r in rows if EVIDENCE_CLASS.get(r["evidence_type"]) == "authoritative"]
    if auth:
        best = max(auth, key=lambda r: float(r["weight"]))
        return float(best["weight"]), (
            f"authoritative evidence ({best['evidence_type']}) sets confidence to "
            f"{float(best['weight']):.2f}"
        )

    base = max(
        (float(r["weight"]) for r in rows if EVIDENCE_CLASS.get(r["evidence_type"]) == "suggestive"),
        default=0.0,
    )
    reps = [r for r in rows if r["evidence_type"] == "repetition"]
    rep_component = min(len(reps) * th.w_repetition_step, th.w_repetition_cap)
    apps = [r for r in rows if r["evidence_type"] == "app_context"]
    app_component = min(len(apps) * th.w_app_context, th.w_app_context_cap)

    conf = min(base + rep_component + app_component, th.w_repetition_cap)
    parts = []
    if base:
        parts.append(f"suggestive base {base:.2f}")
    if reps:
        parts.append(f"{len(reps)} repetition(s) +{rep_component:.2f}")
    if apps:
        parts.append(f"app context +{app_component:.2f} (capped)")
    if not parts:
        parts.append("no qualifying evidence")
    return conf, ", ".join(parts) + f" -> {conf:.2f}"


def status_for(confidence: float, evidence: Iterable[dict[str, Any]], th: Thresholds) -> str:
    rows = list(evidence)
    if any(EVIDENCE_CLASS.get(r["evidence_type"]) == "authoritative" for r in rows):
        return "confirmed"
    return "confirmed" if confidence >= th.confirm_at else "candidate"


# ----------------------------------------------------------------------------------------
# Reads
# ----------------------------------------------------------------------------------------

def get(conn: sqlite3.Connection, memory_id: int) -> dict[str, Any] | None:
    return db.row_to_dict(db.query_one(conn, "SELECT * FROM word_memories WHERE id = ?", (memory_id,)))


def find_live(
    conn: sqlite3.Connection, user_id: str, normalized_key: str, word_type: str | None = None
) -> dict[str, Any] | None:
    sql = (
        "SELECT * FROM word_memories WHERE user_id = ? AND normalized_key = ? "
        "AND status IN ('candidate','confirmed')"
    )
    params: list[Any] = [user_id, normalized_key]
    if word_type:
        sql += " AND word_type = ?"
        params.append(word_type)
    return db.row_to_dict(db.query_one(conn, sql + " ORDER BY confidence DESC LIMIT 1", params))


def evidence_for(conn: sqlite3.Connection, memory_id: int) -> list[dict[str, Any]]:
    return db.rows_to_dicts(
        db.query(conn, "SELECT * FROM memory_evidence WHERE memory_id = ? ORDER BY id", (memory_id,))
    )


def variants_for(conn: sqlite3.Connection, memory_id: int) -> list[dict[str, Any]]:
    return db.rows_to_dicts(
        db.query(
            conn,
            "SELECT * FROM memory_variants WHERE memory_id = ? ORDER BY observation_count DESC, id",
            (memory_id,),
        )
    )


def events_for(conn: sqlite3.Connection, memory_id: int) -> list[dict[str, Any]]:
    return db.rows_to_dicts(
        db.query(conn, "SELECT * FROM memory_events WHERE memory_id = ? ORDER BY id", (memory_id,))
    )


def get_full(conn: sqlite3.Connection, memory_id: int) -> dict[str, Any] | None:
    """A memory with everything needed to explain it: variants, evidence, audit trail."""
    mem = get(conn, memory_id)
    if mem is None:
        return None
    mem["variants"] = variants_for(conn, memory_id)
    mem["evidence"] = evidence_for(conn, memory_id)
    mem["events"] = events_for(conn, memory_id)
    mem["context_terms"] = sorted(context_profile(conn, memory_id))
    return mem


def list_memories(
    conn: sqlite3.Connection,
    user_id: str = "default",
    *,
    status: str | None = None,
    word_type: str | None = None,
    search: str | None = None,
    limit: int = 500,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM word_memories WHERE user_id = ?"
    params: list[Any] = [user_id]
    if status:
        sql += " AND status = ?"
        params.append(status)
    if word_type:
        sql += " AND word_type = ?"
        params.append(word_type)
    if search:
        sql += " AND normalized_key LIKE ?"
        params.append(f"%{normalize_key(search)}%")
    sql += " ORDER BY (status='confirmed') DESC, confidence DESC, id DESC LIMIT ?"
    params.append(limit)
    rows = db.rows_to_dicts(db.query(conn, sql, params))
    for r in rows:
        r["variants"] = variants_for(conn, r["id"])
    return rows


def max_token_count(conn: sqlite3.Connection, user_id: str = "default") -> int:
    """Widest span in memory — bounds the query-side n-gram window (taxonomy A7/A8).

    This must consider **variants**, not just canonical forms. Every canonical here is one
    token ("Kubernetes", "Postgres"), but their wrong forms are two ("Cuban Eighties",
    "Post Grease"). Measuring only canonicals returned 1, so no multi-token span was ever
    generated and those learned variants could never match anything — a capability that
    silently did nothing.

    Candidate memories count too, because a candidate can protect the span it covers even
    though it can never rewrite one.

    Token counts for variants are derived in SQL by counting the single spaces in the
    normalised form, which avoids a schema column that would exist only to be recomputed.
    """
    row = db.query_one(
        conn,
        """
        SELECT MAX(n) AS n FROM (
            SELECT LENGTH(v.variant_normalized)
                   - LENGTH(REPLACE(v.variant_normalized, ' ', '')) + 1 AS n
            FROM memory_variants v
            JOIN word_memories m ON m.id = v.memory_id
            WHERE m.user_id = ? AND m.status IN ('confirmed', 'candidate')
            UNION ALL
            SELECT token_count AS n FROM word_memories
            WHERE user_id = ? AND status IN ('confirmed', 'candidate')
        )
        """,
        (user_id, user_id),
    )
    return int(row["n"]) if row and row["n"] else 1


def context_profile(
    conn: sqlite3.Connection, memory_id: int, *, stopword_rank: int = 300
) -> set[str]:
    """Words seen NEAR this memory in its own evidence interactions.

    This is the learned half of the context gate: "Kivi" acquires {sarvam, service,
    review, ship} from the interactions that taught it, and those words later vouch for
    it. Nothing is hand-written per memory.

    Very frequent words are excluded. The exclusion is by measured frequency rank rather
    than a hand-written stoplist, for the same reason `TYPE_TRIGGERS` contains no function
    words: "the" sitting near a memory is not evidence of anything. Keeping it let the
    single token "the" push a substitution over the bar, turning "post grease warnings near
    the fryer" into "Postgres warnings near the fryer".
    """
    rows = db.query(
        conn,
        """
        SELECT i.formatted_text, i.asr_text, i.user_edited_text, i.app_context
        FROM memory_evidence e
        JOIN interactions i ON i.id = e.interaction_id
        WHERE e.memory_id = ?
          -- Weak app-context evidence is excluded. It is legitimate corroboration for
          -- CONFIDENCE ("this surface mentions the word"), but the sentence it came from
          -- says nothing about the word's neighbours: every dictation typed into
          -- "Slack - #kivi-eng" was donating its vocabulary to the Kivi profile, which
          -- diluted the one signal the context gate depends on.
          AND e.evidence_class != 'weak'
        """,
        (memory_id,),
    )
    mem = get(conn, memory_id)
    own = set(normalize_key(mem["canonical_form"]).split()) if mem else set()
    terms: set[str] = set()
    for r in rows:
        for field in ("formatted_text", "user_edited_text", "asr_text", "app_context"):
            if r[field]:
                terms |= {t.text.lower() for t in tokenize(normalize_key(r[field]))}
    return {
        t
        for t in terms - own
        if len(t) > 2 and word_rank(t) > stopword_rank
    }


# ----------------------------------------------------------------------------------------
# Writes
# ----------------------------------------------------------------------------------------

def _log_event(
    conn: sqlite3.Connection,
    memory_id: int,
    event: str,
    *,
    reason_code: str,
    reason_text: str | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    from_confidence: float | None = None,
    to_confidence: float | None = None,
    evidence_id: int | None = None,
) -> int:
    return db.insert(
        conn,
        "memory_events",
        {
            "memory_id": memory_id,
            "event": event,
            "from_status": from_status,
            "to_status": to_status,
            "from_confidence": from_confidence,
            "to_confidence": to_confidence,
            "reason_code": reason_code,
            "reason_text": reason_text,
            "evidence_id": evidence_id,
            "created_at": now_iso(),
        },
    )


def add_evidence(
    conn: sqlite3.Connection,
    memory_id: int,
    *,
    evidence_type: str,
    interaction_id: int | None,
    excerpt: str | None,
    th: Thresholds,
) -> int:
    return db.insert(
        conn,
        "memory_evidence",
        {
            "memory_id": memory_id,
            "interaction_id": interaction_id,
            "evidence_type": evidence_type,
            "evidence_class": EVIDENCE_CLASS[evidence_type],
            "weight": evidence_weight(evidence_type, th),
            "excerpt": excerpt,
            "created_at": now_iso(),
        },
    )


def add_variant(
    conn: sqlite3.Connection,
    memory_id: int,
    variant_form: str,
    *,
    kind: str,
    encoder: str = DEFAULT_ENCODER,
    count: int = 1,
) -> int:
    """Record a form this memory has been observed as. Idempotent per normalized form."""
    norm = normalize_key(variant_form)
    existing = db.query_one(
        conn,
        "SELECT * FROM memory_variants WHERE memory_id = ? AND variant_normalized = ?",
        (memory_id, norm),
    )
    ts = now_iso()
    if existing:
        conn.execute(
            "UPDATE memory_variants SET observation_count = observation_count + ?, last_seen = ? "
            "WHERE id = ?",
            (count, ts, existing["id"]),
        )
        return int(existing["id"])
    vid = db.insert(
        conn,
        "memory_variants",
        {
            "memory_id": memory_id,
            "variant_form": variant_form,
            "variant_normalized": norm,
            "variant_phonetic": encode(variant_form, encoder),
            "kind": kind,
            "observation_count": count,
            "first_seen": ts,
            "last_seen": ts,
            "created_at": ts,
        },
    )
    _log_event(
        conn,
        memory_id,
        "variant_added",
        reason_code="VARIANT_OBSERVED",
        reason_text=f"observed as {variant_form!r} ({kind})",
    )
    return vid


def refresh_confidence(
    conn: sqlite3.Connection, memory_id: int, th: Thresholds, *, reason_code: str = "EVIDENCE_ADDED"
) -> dict[str, Any]:
    """Recompute confidence and status from the evidence set, logging any movement."""
    mem = get(conn, memory_id)
    if mem is None:
        raise ValueError(f"no memory {memory_id}")
    if mem["status"] in ("deleted", "superseded"):
        return mem   # inert memories are not re-promoted by late-arriving evidence

    ev = evidence_for(conn, memory_id)
    new_conf, explanation = compute_confidence(ev, th)
    new_status = status_for(new_conf, ev, th)
    old_conf, old_status = float(mem["confidence"]), mem["status"]

    if abs(new_conf - old_conf) > 1e-9 or new_status != old_status:
        conn.execute(
            "UPDATE word_memories SET confidence = ?, status = ?, updated_at = ? WHERE id = ?",
            (new_conf, new_status, now_iso(), memory_id),
        )
        if new_status != old_status:
            event = "promoted" if new_status == "confirmed" else "demoted"
        else:
            event = "reinforced"
        _log_event(
            conn,
            memory_id,
            event,
            reason_code=reason_code,
            reason_text=explanation,
            from_status=old_status,
            to_status=new_status,
            from_confidence=old_conf,
            to_confidence=new_conf,
        )
    return get(conn, memory_id)  # type: ignore[return-value]


def create(
    conn: sqlite3.Connection,
    *,
    canonical_form: str,
    word_type: str,
    evidence_type: str,
    th: Thresholds,
    user_id: str = "default",
    interaction_id: int | None = None,
    excerpt: str | None = None,
    gloss: str | None = None,
    observed_form: str | None = None,
    observed_kind: str = "asr_error",
    encoder: str = DEFAULT_ENCODER,
) -> dict[str, Any]:
    """Create a memory from one piece of evidence. Status follows the policy, not the caller."""
    keys = build_keys(canonical_form, encoder=encoder)
    ts = now_iso()
    memory_id = db.insert(
        conn,
        "word_memories",
        {
            "user_id": user_id,
            "canonical_form": canonical_form,
            "normalized_key": keys.normalized,
            "phonetic_key": keys.phonetic,
            "token_count": keys.token_count,
            "word_type": word_type,
            "status": "candidate",
            "confidence": 0.0,
            "gloss": gloss,
            "occurrence_count": 1,
            "first_seen": ts,
            "last_seen": ts,
            "created_at": ts,
            "updated_at": ts,
        },
    )
    _log_event(
        conn,
        memory_id,
        "created",
        reason_code="EVIDENCE_" + evidence_type.upper(),
        reason_text=f"created from {evidence_type} evidence: {excerpt!r}",
        to_status="candidate",
        to_confidence=0.0,
    )
    # The canonical is stored as a variant too, so lookup is uniform across both tables.
    add_variant(conn, memory_id, canonical_form, kind="canonical", encoder=encoder)
    if observed_form and normalize_key(observed_form) != keys.normalized:
        add_variant(conn, memory_id, observed_form, kind=observed_kind, encoder=encoder)

    ev_id = add_evidence(
        conn, memory_id, evidence_type=evidence_type, interaction_id=interaction_id,
        excerpt=excerpt, th=th,
    )
    refresh_confidence(conn, memory_id, th, reason_code="EVIDENCE_" + evidence_type.upper())
    mem = get(conn, memory_id)
    assert mem is not None
    mem["_evidence_id"] = ev_id
    return mem


def reinforce(
    conn: sqlite3.Connection,
    memory_id: int,
    *,
    evidence_type: str,
    th: Thresholds,
    interaction_id: int | None = None,
    excerpt: str | None = None,
    observed_form: str | None = None,
    observed_kind: str = "asr_error",
    encoder: str = DEFAULT_ENCODER,
) -> dict[str, Any]:
    add_evidence(
        conn, memory_id, evidence_type=evidence_type, interaction_id=interaction_id,
        excerpt=excerpt, th=th,
    )
    if observed_form:
        mem = get(conn, memory_id)
        if mem and normalize_key(observed_form) != mem["normalized_key"]:
            add_variant(conn, memory_id, observed_form, kind=observed_kind, encoder=encoder)
    ts = now_iso()
    conn.execute(
        "UPDATE word_memories SET occurrence_count = occurrence_count + 1, last_seen = ?, "
        "updated_at = ? WHERE id = ?",
        (ts, ts, memory_id),
    )
    return refresh_confidence(conn, memory_id, th, reason_code="EVIDENCE_" + evidence_type.upper())


def supersede(
    conn: sqlite3.Connection,
    memory_id: int,
    new_canonical: str,
    *,
    th: Thresholds,
    evidence_type: str = "user_spelling",
    interaction_id: int | None = None,
    excerpt: str | None = None,
    encoder: str = DEFAULT_ENCODER,
) -> dict[str, Any]:
    """Replace knowledge without destroying it (taxonomy N10, §13).

    "Actually, it's spelled Aditya" creates a NEW memory, marks the old one `superseded`,
    and links them. The old row keeps its canonical form, its evidence and its history, so
    the change is inspectable — but it is inert, because retrieval only looks at live rows.
    The old spelling is carried onto the new memory as an `orthographic` variant, which is
    what makes the previously-correct output start being corrected.
    """
    old = get(conn, memory_id)
    if old is None:
        raise ValueError(f"no memory {memory_id}")

    new = create(
        conn,
        canonical_form=new_canonical,
        word_type=old["word_type"],
        evidence_type=evidence_type,
        th=th,
        user_id=old["user_id"],
        interaction_id=interaction_id,
        excerpt=excerpt,
        gloss=old["gloss"],
        observed_form=old["canonical_form"],
        observed_kind="orthographic",
        encoder=encoder,
    )
    # Every form the old memory answered to must follow, or corrections silently regress.
    for v in variants_for(conn, memory_id):
        if v["kind"] != "canonical":
            add_variant(conn, new["id"], v["variant_form"], kind=v["kind"], encoder=encoder)

    conn.execute(
        "UPDATE word_memories SET status = 'superseded', superseded_by = ?, updated_at = ? WHERE id = ?",
        (new["id"], now_iso(), memory_id),
    )
    _log_event(
        conn,
        memory_id,
        "superseded",
        reason_code="SUPERSEDED_BY_NEW_CANONICAL",
        reason_text=f"{old['canonical_form']!r} superseded by {new_canonical!r}",
        from_status=old["status"],
        to_status="superseded",
        from_confidence=float(old["confidence"]),
        to_confidence=float(old["confidence"]),
    )
    return new


def update(
    conn: sqlite3.Connection,
    memory_id: int,
    *,
    th: Thresholds,
    canonical_form: str | None = None,
    word_type: str | None = None,
    gloss: str | None = None,
    status: str | None = None,
    encoder: str = DEFAULT_ENCODER,
) -> dict[str, Any]:
    """Edit a memory in place.

    Changing the canonical form is NOT an in-place edit: it routes to `supersede`, because
    losing the previous spelling would make the change uninspectable.
    """
    mem = get(conn, memory_id)
    if mem is None:
        raise ValueError(f"no memory {memory_id}")

    if canonical_form and normalize_key(canonical_form) != mem["normalized_key"]:
        return supersede(
            conn, memory_id, canonical_form, th=th, evidence_type="manual_entry",
            excerpt="edited directly in the memory inspector", encoder=encoder,
        )

    fields: dict[str, Any] = {}
    if canonical_form:
        fields["canonical_form"] = canonical_form   # same normalised key: pure re-casing
    if word_type:
        fields["word_type"] = word_type
    if gloss is not None:
        fields["gloss"] = gloss
    if status:
        if status not in ("candidate", "confirmed"):
            raise ValueError("status can only be set to 'candidate' or 'confirmed'")
        fields["status"] = status

    if not fields:
        return mem
    fields["updated_at"] = now_iso()
    sets = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(f"UPDATE word_memories SET {sets} WHERE id = ?", (*fields.values(), memory_id))

    if status and status != mem["status"]:
        # A manual promotion is authoritative evidence in its own right, otherwise the next
        # confidence refresh would quietly undo the reviewer's decision.
        if status == "confirmed":
            add_evidence(
                conn, memory_id, evidence_type="manual_entry", interaction_id=None,
                excerpt="confirmed directly in the memory inspector", th=th,
            )
        _log_event(
            conn, memory_id, "promoted" if status == "confirmed" else "demoted",
            reason_code="MANUAL_STATUS_CHANGE",
            reason_text=f"status set to {status} by the user",
            from_status=mem["status"], to_status=status,
            from_confidence=float(mem["confidence"]), to_confidence=float(mem["confidence"]),
        )
        refresh_confidence(conn, memory_id, th, reason_code="MANUAL_STATUS_CHANGE")
    else:
        _log_event(
            conn, memory_id, "updated", reason_code="MANUAL_EDIT",
            reason_text=f"fields changed: {sorted(k for k in fields if k != 'updated_at')}",
        )
    return get(conn, memory_id)  # type: ignore[return-value]


def soft_delete(conn: sqlite3.Connection, memory_id: int, *, reason: str = "user requested") -> dict[str, Any]:
    """Remove a memory from the system's behaviour while keeping the record (§14)."""
    mem = get(conn, memory_id)
    if mem is None:
        raise ValueError(f"no memory {memory_id}")
    ts = now_iso()
    conn.execute(
        "UPDATE word_memories SET status = 'deleted', deleted_at = ?, updated_at = ? WHERE id = ?",
        (ts, ts, memory_id),
    )
    _log_event(
        conn, memory_id, "deleted", reason_code="USER_DELETED", reason_text=reason,
        from_status=mem["status"], to_status="deleted",
        from_confidence=float(mem["confidence"]), to_confidence=float(mem["confidence"]),
    )
    return get(conn, memory_id)  # type: ignore[return-value]


def restore(conn: sqlite3.Connection, memory_id: int, th: Thresholds) -> dict[str, Any]:
    mem = get(conn, memory_id)
    if mem is None:
        raise ValueError(f"no memory {memory_id}")
    if mem["status"] != "deleted":
        return mem
    conn.execute(
        "UPDATE word_memories SET status = 'candidate', deleted_at = NULL, updated_at = ? WHERE id = ?",
        (now_iso(), memory_id),
    )
    _log_event(
        conn, memory_id, "restored", reason_code="USER_RESTORED",
        from_status="deleted", to_status="candidate",
    )
    return refresh_confidence(conn, memory_id, th, reason_code="USER_RESTORED")
