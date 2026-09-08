"""Learning: what counts as evidence, and what is done with it.

The hard part of this product is not storing words. It is refusing to store most of them.
RULE 5 — do not learn every unknown word — is enforced here, by requiring every proposal to
arrive attached to a *typed* piece of evidence and then letting the confidence policy in
`memory.py` decide whether that evidence is enough.

Four extractors, in descending order of evidence strength:

  * `_from_user_edit`      E2  the person fixed our output. The strongest signal available
                               from ordinary use, because it is a correction, not a guess.
  * `_from_spelling_instruction`
                           E1  the person said the spelling out loud.
  * `_from_naming_frame`   E6  "the company is called Aaditya Labs" — an assertion, but a
                               single one, so it produces a candidate and nothing more.
  * `_from_repetition`     E4  a word ASR already transcribes consistently. Prophylactic:
                               learning it cannot introduce an error, and it means the
                               *next* mis-hearing is catchable.

Every proposal, including every refusal, is written to `learning_decisions`. Without that
row, "why was this not learned" is unanswerable and memory recall is unmeasurable.
"""

from __future__ import annotations

import difflib
import re
import sqlite3
from dataclasses import dataclass, field
from typing import Any

from . import db
from . import memory as mem_mod
from .config import Thresholds
from .context import TYPE_TRIGGERS
from .lexicon import is_ordinary_word, rank
from .phonetics import DEFAULT_ENCODER, encode, jaro_winkler, phonetic_similarity
from .text import (
    Span,
    is_irrealis,
    normalize_compact,
    normalize_key,
    spans,
    tokenize,
)

# A proposal must look like a word worth remembering before any evidence is even considered.
_SHAPE_RE = re.compile(r"^[@#]?[A-Za-z][A-Za-z0-9'._-]{1,29}$")

_MIN_LEN = 3

# Determiners and pronouns are never part of a name, so they are stripped from the front
# of a capitalised run. Needed because sentence-initial capitalisation is indiscriminate:
# without this, "The Kubernetes cluster..." proposes the name "The Kubernetes".
_RUN_LEADERS_TO_DROP = {
    "the", "a", "an", "this", "that", "these", "those", "our", "my", "your", "his",
    "her", "their", "its", "it", "we", "i", "you", "they", "he", "she",
}

# Repetition may only propose words that general English does not already contain.
# Measured on the vendored frequency list: friday 939, january 194, google 949, john 372,
# india 920 are all common globally, while aditya, sarvam, kivi, kubernetes and epd are
# absent from the top 30,000 entirely. So "absent from the 30k most frequent web tokens"
# is a data-driven test for "this could be someone's private vocabulary", and it keeps
# days, months, countries and famous names out of memory without a hand-written blocklist.
# Words below the floor can still be learned — but only from authoritative evidence, which
# is the correct route for "my colleague spells it Jon".
_REPETITION_RANK_FLOOR = 30_000

# Words the spelling patterns must never capture as the name being spelled. Without this,
# "Actually, it's spelled Aaditya" yields a memory for the word "spelled".
_NOT_A_NAME = {
    "spelled", "spelt", "spelling", "spell", "it", "its", "it's", "that", "thats",
    "that's", "this", "mean", "means", "meant", "actually", "no", "sorry", "as", "like",
    "the", "a", "an",
}

# Verbs that take an animate subject. Used only as a last resort, when no trigger word
# in the sentence indicated what kind of thing a name is.
_ANIMATE_SUBJECT_VERBS = {
    "is", "was", "will", "has", "had", "owns", "leads", "runs", "wrote", "said", "says",
    "thinks", "wants", "needs", "asked", "sent", "shared", "presented", "joined", "left",
    "reviewed", "approved", "signed", "reported", "mentioned", "replied", "called",
    "prefers", "spells", "works", "helped", "found", "fixed", "shipped", "merged",
}

# Head nouns that both introduce a name and reveal what kind of thing it is.
_NAMING_HEADS: dict[str, str] = {
    "company": "org", "startup": "org", "client": "org", "vendor": "org", "firm": "org",
    "product": "product", "service": "product", "app": "product", "tool": "product",
    "platform": "product", "feature": "product",
    "project": "project", "initiative": "project", "workstream": "project",
    "team": "org", "squad": "org", "group": "org",
    "colleague": "person", "manager": "person", "friend": "person", "intern": "person",
    "someone": "person", "guy": "person", "person": "person", "lead": "person",
    "city": "place", "office": "place", "town": "place",
    "library": "term", "package": "term", "framework": "term", "database": "term",
}

_HEADS_ALT = "|".join(_NAMING_HEADS)

# The name capture must stay CASE-SENSITIVE. Compiling these with re.IGNORECASE made the
# `[A-Z]` continuation match lowercase words too, so the capture ran past the name and
# produced memories for "Aaditya Labs and they" and "Aditya Ghosh signed of". Only the
# surrounding function words and head nouns are case-insensitive, via scoped (?i:...).
_NAMING_PATTERNS = [
    # "the company is called Aaditya Labs" / "our product is named Kivi"
    re.compile(
        r"\b(?i:the|a|an|our|my|this)?\s*(?P<head>(?i:" + _HEADS_ALT + r"))\b"
        r"[^.?!]{0,20}?\b(?i:is|are|was)?\s*(?i:called|named)\s+"
        r"(?P<name>[A-Z][\w'.-]*(?:\s+[A-Z][\w'.-]*){0,3})"
    ),
    # "someone named Aaditya" / "a guy called Kartik"
    re.compile(r"\b(?i:named|called)\s+(?P<name>[A-Z][\w'.-]*(?:\s+[A-Z][\w'.-]*){0,3})"),
    # "my colleague Aaditya" / "our client Aaditya Labs"
    re.compile(
        r"\b(?i:my|our|the)\s+(?P<head>(?i:" + _HEADS_ALT + r"))\s+"
        r"(?P<name>[A-Z][\w'.-]*(?:\s+[A-Z][\w'.-]*){0,3})"
    ),
]

_SPELLING_PATTERNS = [
    # "actually, it's spelled Aaditya" / "that's spelt Aaditya"
    re.compile(r"\b(?:spelled|spelt|spelling|spell)\s+(?:it\s+|that\s+|as\s+)?(?P<name>[A-Za-z][\w'.-]*)", re.IGNORECASE),
    # "no, it's Aaditya" / "actually it's Kivi"
    re.compile(r"\b(?:actually|no|sorry)[,\s]+(?:it'?s|that'?s|i\s+mean)\s+(?P<name>[A-Z][\w'.-]*)", re.IGNORECASE),
    # "I mean Aaditya"
    re.compile(r"\bI\s+mean\s+(?P<name>[A-Z][\w'.-]*)"),
]

# "A-A-D-I-T-Y-A" or "A A D I T Y A" — letters dictated one by one.
_LETTER_SPELLING_RE = re.compile(r"\b(?:[A-Za-z][\s.-]+){2,}[A-Za-z]\b")


@dataclass
class Proposal:
    surface_form: str            # what was observed
    canonical: str               # what it should be written as
    evidence_type: str
    word_type: str
    excerpt: str
    observed_form: str | None = None   # the wrong form, when evidence identifies one
    observed_kind: str = "asr_error"
    gloss: str | None = None
    # True when this single token was only seen INSIDE a longer capitalised name. Such a
    # sighting is evidence for the phrase, not for the token: "Aditya" appearing only ever
    # within "Aditya Ghosh" says nothing about a person called "Aditya".
    in_phrase: bool = False


@dataclass
class LearningOutcome:
    interaction_id: int
    proposals: list[dict[str, Any]] = field(default_factory=list)

    def summary(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for p in self.proposals:
            out[p["outcome"]] = out.get(p["outcome"], 0) + 1
        return out


# ----------------------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------------------

def _clean_name(raw: str) -> str:
    """Trim sentence punctuation off a captured name.

    The capture groups have to allow interior dots and hyphens ("sarvam.ai", "Sarvam-M"),
    which means they also swallow the full stop at the end of a sentence — that is how a
    memory for 'Aaditya.' got created, trailing period and all.
    """
    return raw.strip().strip(".,;:!?\"'()[]").strip()


def _shape_ok(form: str) -> bool:
    if not _SHAPE_RE.match(form):
        return False
    if form.lower() in _NOT_A_NAME:
        return False
    letters = re.sub(r"[^A-Za-z]", "", form)
    return len(letters) >= _MIN_LEN


def _infer_word_type(text: str, name: str, *, default: str = "term") -> str:
    """Guess what kind of thing a name is, from the words around it.

    Deterministic and deliberately conservative. The type only ever *raises* the bar a
    correction must clear (it selects which trigger words count as support), so guessing
    "term" when the truth is "person" costs recall, never precision.
    """
    if name.startswith("@") or "_" in name:
        return "handle"
    if re.fullmatch(r"[A-Z]{2,6}", name):
        return "acronym"

    toks = tokenize(text)
    around = {t.text.lower() for t in toks}
    for head, wtype in _NAMING_HEADS.items():
        if head in around:
            return wtype

    best, best_hits = default, 0
    for wtype, triggers in TYPE_TRIGGERS.items():
        hits = len(around & triggers)
        if hits > best_hits:
            best, best_hits = wtype, hits
    if best_hits:
        return best

    # No trigger fired. A capitalised name in subject position, followed by a verb that
    # takes an animate subject, is a person: "Vishal owns the pipeline", "Sumeet is
    # reviewing". Without this the default swallowed every colleague's name as a "term",
    # which costs recall because person-appropriate cues then never count as support.
    lowered = [t.text.lower() for t in toks]
    for idx, tok in enumerate(toks):
        if tok.text != name.split()[0] or not tok.text[:1].isupper():
            continue
        nxt = lowered[idx + 1] if idx + 1 < len(lowered) else ""
        if nxt in _ANIMATE_SUBJECT_VERBS or nxt.endswith("ed") or nxt.endswith("s"):
            return "person"
    return default


def _find_span(text: str, form: str) -> Span | None:
    target = normalize_key(form)
    n = max(1, len(tokenize(form)))
    for span in spans(text, max_tokens=max(n, 1)):
        if span.token_count == n and normalize_key(span.text) == target:
            return span
    return None


def _closest_prior_form(text: str, canonical: str, *, encoder: str = DEFAULT_ENCODER) -> str | None:
    """Which word in this text was the spelling instruction correcting?

    An instruction like "actually, spell it Aaditya" only supplies the right answer; the
    wrong one has to be located. The nearest-sounding earlier token is that word.
    """
    target_code = encode(canonical, encoder)
    target_compact = normalize_compact(canonical)
    best: tuple[float, str] | None = None
    for tok in tokenize(text):
        form = tok.text
        if normalize_compact(form) == target_compact:
            continue
        if not _shape_ok(form):
            continue
        score = max(
            phonetic_similarity(encode(form, encoder), target_code),
            jaro_winkler(normalize_compact(form), target_compact),
        )
        if score >= 0.70 and (best is None or score > best[0]):
            best = (score, form)
    return best[1] if best else None


def _variant_kind(old: str, new: str) -> str:
    """Does substituting `old` with `new` change what the sentence means?

    If both are real English words, or they differ only in case and spacing, the swap is
    orthographic and therefore safe anywhere ("grey"/"gray", "open ai"/"OpenAI"). If only
    the new form is a name, the swap changes the referent ("kiwi"/"Kivi") and must earn
    its context. This is the distinction that lets taxonomy A11 be applied freely while
    A1 stays gated.
    """
    same_letters = normalize_compact(old) == normalize_compact(new)

    # Capitalising an ordinary lowercase word is NOT a harmless orthographic change: the
    # case *is* the meaning distinction. "cursor" -> "Cursor", "notion" -> "Notion",
    # "apple" -> "Apple" all promote a common noun to a proper noun, so they must earn
    # context like any other referent change. Treating these as orthographic would have
    # rewritten "move the cursor left" unconditionally.
    if same_letters and is_ordinary_word(old) and old.islower() and new[:1].isupper():
        return "asr_error"

    if same_letters:
        return "orthographic"      # "open ai" -> "OpenAI": same letters, no common noun involved
    if is_ordinary_word(old) and is_ordinary_word(new):
        return "orthographic"      # "grey" -> "gray": two real words, same referent (A11)
    return "asr_error"


# ----------------------------------------------------------------------------------------
# Extractors
# ----------------------------------------------------------------------------------------

def _from_user_edit(formatted: str, edited: str, *, encoder: str = DEFAULT_ENCODER) -> list[Proposal]:
    """Diff our output against the person's correction of it (evidence E2).

    Only word-identity fixes are learned. If the person rewrote the sentence, the replaced
    spans will not resemble each other and nothing is proposed — this system learns
    vocabulary, not style.
    """
    old_tokens = [t.text for t in tokenize(formatted)]
    new_tokens = [t.text for t in tokenize(edited)]
    out: list[Proposal] = []

    matcher = difflib.SequenceMatcher(a=[t.lower() for t in old_tokens], b=[t.lower() for t in new_tokens])

    def emit_case_run(run: list[tuple[str, str]]) -> None:
        """A consecutive run of tokens whose CASE the person changed."""
        if not run:
            return
        old_phrase = " ".join(o for o, _ in run)
        new_phrase = " ".join(n for _, n in run)
        if not all(_shape_ok(n) for _, n in run):
            return
        # Only a promotion to upper case is meaningful ("cursor" -> "Cursor",
        # "epd" -> "EPD"). The reverse is usually the person de-emphasising a word.
        if not any(c.isupper() for c in new_phrase) or old_phrase == new_phrase:
            return
        out.append(
            Proposal(
                surface_form=old_phrase,
                canonical=new_phrase,
                evidence_type="user_edit",
                word_type=_infer_word_type(edited, new_phrase),
                excerpt=f"user recapitalised {old_phrase!r} to {new_phrase!r}",
                observed_form=old_phrase,
                observed_kind=_variant_kind(old_phrase, new_phrase),
            )
        )

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        # Alignment is computed on LOWERCASED tokens so that incidental casing does not
        # manufacture diffs. The cost is that a case-only fix lands in an "equal" block
        # and would otherwise be invisible — which silently lost every "cursor" ->
        # "Cursor" style correction, the most common kind of edit a person makes.
        if op == "equal":
            run: list[tuple[str, str]] = []
            for k in range(i2 - i1):
                o, n = old_tokens[i1 + k], new_tokens[j1 + k]
                if o != n:
                    run.append((o, n))
                else:
                    emit_case_run(run)
                    run = []
            emit_case_run(run)
            continue
        if op != "replace":
            continue
        # Only tight, aligned replacements are word-identity fixes.
        if (i2 - i1) > 4 or (j2 - j1) > 4:
            continue
        old = " ".join(old_tokens[i1:i2])
        new = " ".join(new_tokens[j1:j2])
        if not old or not new or normalize_key(old) == normalize_key(new):
            continue
        if not all(_shape_ok(t) for t in new_tokens[j1:j2]):
            continue

        similarity = max(
            phonetic_similarity(encode(old, encoder), encode(new, encoder)),
            jaro_winkler(normalize_compact(old), normalize_compact(new)),
        )
        if normalize_compact(old) != normalize_compact(new) and similarity < 0.55:
            continue   # a rewrite, not a spelling fix

        kind = _variant_kind(old, new)
        # A swap between two real English words is a settled spelling preference, not a
        # fact about the world ("grey"->"gray", "organise"->"organize"). That is
        # structurally detectable, so it does not need the type heuristic to guess it —
        # and getting it right matters, because `preference` memories are the ones allowed
        # to apply without situational support.
        if kind == "orthographic" and is_ordinary_word(old) and is_ordinary_word(new):
            word_type = "preference"
        else:
            word_type = _infer_word_type(edited, new)

        out.append(
            Proposal(
                surface_form=old,
                canonical=new,
                evidence_type="user_edit",
                word_type=word_type,
                excerpt=f"user corrected {old!r} to {new!r}",
                observed_form=old,
                observed_kind=kind,
            )
        )
    return out


def _from_spelling_instruction(text: str, *, encoder: str = DEFAULT_ENCODER) -> list[Proposal]:
    """"Actually, spell it Aaditya" (evidence E1)."""
    out: list[Proposal] = []
    seen: set[str] = set()

    letters = _LETTER_SPELLING_RE.search(text)
    if letters:
        joined = re.sub(r"[^A-Za-z]", "", letters.group(0))
        if _shape_ok(joined):
            canonical = joined[:1].upper() + joined[1:].lower()
            out.append(
                Proposal(
                    surface_form=letters.group(0),
                    canonical=canonical,
                    evidence_type="user_spelling",
                    word_type=_infer_word_type(text, canonical, default="person"),
                    excerpt=f"spelled out letter by letter: {letters.group(0)!r}",
                    observed_form=_closest_prior_form(text, canonical, encoder=encoder),
                )
            )
            seen.add(normalize_key(canonical))

    for pattern in _SPELLING_PATTERNS:
        for m in pattern.finditer(text):
            name = _clean_name(m.group("name"))
            if not _shape_ok(name) or normalize_key(name) in seen:
                continue
            seen.add(normalize_key(name))
            observed = _closest_prior_form(text, name, encoder=encoder)
            out.append(
                Proposal(
                    surface_form=observed or name,
                    canonical=name,
                    evidence_type="user_spelling",
                    word_type=_infer_word_type(text, name),
                    excerpt=m.group(0).strip(),
                    observed_form=observed,
                    observed_kind=_variant_kind(observed, name) if observed else "asr_error",
                )
            )
    return out


def _from_naming_frame(text: str) -> list[Proposal]:
    """"The company is called Aaditya Labs" (evidence E6, suggestive only)."""
    out: list[Proposal] = []
    seen: set[str] = set()
    for pattern in _NAMING_PATTERNS:
        for m in pattern.finditer(text):
            name = _clean_name(m.group("name"))
            if not name:
                continue
            parts = name.split()
            if not all(_shape_ok(p) for p in parts):
                continue
            head = (m.groupdict().get("head") or "").lower()

            # A "name" made entirely of ordinary English words is usually the pattern
            # misfiring ("the project called out the risk"). But an explicit head noun —
            # "our *client* is called Kiwi Foods" — is strong evidence that it really is a
            # name, and real companies are named after ordinary words all the time
            # (Apple, Notion, Linear, Arc). So the guard only applies without a head.
            if all(is_ordinary_word(p) for p in parts) and not head:
                continue
            key = normalize_key(name)
            if key in seen:
                continue
            seen.add(key)

            word_type = _NAMING_HEADS.get(head) or _infer_word_type(text, name)
            out.append(
                Proposal(
                    surface_form=name,
                    canonical=name,
                    evidence_type="naming_frame",
                    word_type=word_type,
                    excerpt=m.group(0).strip(),
                    gloss=f"introduced as a {word_type} in \"{m.group(0).strip()}\"",
                )
            )
    return out


def _from_repetition(text: str) -> list[Proposal]:
    """Words ASR already gets right but general English does not contain (evidence E4).

    These are prophylactic: nothing is wrong yet. Learning them makes the casing canonical
    and gives the word a phonetic key, so a later mis-hearing becomes catchable. Because
    the observed form is already correct, learning it can never introduce an error — which
    is what makes repetition an acceptable basis for a memory at all.
    """
    out: list[Proposal] = []
    seen: set[str] = set()
    toks = tokenize(text)

    def learnable_by_repetition(form: str) -> bool:
        """Could this word plausibly be private vocabulary rather than general English?"""
        return (
            _shape_ok(form)
            and not is_ordinary_word(form)
            and rank(form) >= _REPETITION_RANK_FLOOR
        )

    # Adjacent capitalised runs first, so "Aaditya Labs" is proposed as one thing.
    i = 0
    while i < len(toks):
        if toks[i].text[:1].isupper() and _shape_ok(toks[i].text):
            j = i + 1
            while j < len(toks) and toks[j].text[:1].isupper() and _shape_ok(toks[j].text) and j - i < 4:
                j += 1
            # Strip a leading determiner before judging the run.
            start = i
            if toks[start].text.lower() in _RUN_LEADERS_TO_DROP and j - start > 1:
                start += 1
            if j - start >= 2:
                phrase = " ".join(t.text for t in toks[start:j])
                # A capitalised multi-word run is a name even when every word in it is
                # ordinary English. The frequency floor applies to single tokens, where
                # it keeps days and famous names out; applied per-token to a phrase it
                # rejected real companies like "Amber Rail" outright.
                if not all(t.text.lower() in _RUN_LEADERS_TO_DROP for t in toks[start:j]):
                    key = normalize_key(phrase)
                    if key not in seen:
                        seen.add(key)
                        out.append(
                            Proposal(
                                surface_form=phrase, canonical=phrase,
                                evidence_type="repetition",
                                word_type=_infer_word_type(text, phrase),
                                excerpt=f"appeared as {phrase!r}",
                            )
                        )
                i = j
                continue
        i += 1

    # Character ranges covered by the capitalised phrases proposed above.
    phrase_ranges: list[tuple[int, int]] = []
    i = 0
    while i < len(toks):
        if toks[i].text[:1].isupper() and _shape_ok(toks[i].text):
            j = i + 1
            while j < len(toks) and toks[j].text[:1].isupper() and _shape_ok(toks[j].text) and j - i < 4:
                j += 1
            if j - i >= 2:
                phrase_ranges.append((toks[i].start, toks[j - 1].end))
                i = j
                continue
        i += 1

    for tok in toks:
        form = tok.text
        if not learnable_by_repetition(form):
            continue
        key = normalize_key(form)
        if key in seen:
            continue
        # A token is proposed on its own even when it also appears inside a proposed
        # phrase. Suppressing it was silently losing sightings: "Sarvam" never accumulated
        # repetition evidence from "Sarvam Kivi", so it stalled one step below confirmed.
        # Each proposal carries its own evidence and the policy judges them separately.
        seen.add(key)
        inside = any(a <= tok.start and tok.end <= b for a, b in phrase_ranges)
        out.append(
            Proposal(
                surface_form=form, canonical=form, evidence_type="repetition",
                word_type=_infer_word_type(text, form),
                excerpt=f"appeared as {form!r}"
                        + (" (only inside a longer capitalised name)" if inside else ""),
                in_phrase=inside,
            )
        )
    return out


# ----------------------------------------------------------------------------------------
# Policy
# ----------------------------------------------------------------------------------------

def _log(
    conn: sqlite3.Connection,
    interaction_id: int,
    proposal: Proposal,
    outcome: str,
    reason_code: str,
    reason_text: str,
    memory_id: int | None = None,
) -> dict[str, Any]:
    db.insert(
        conn,
        "learning_decisions",
        {
            "interaction_id": interaction_id,
            "surface_form": proposal.surface_form,
            "proposed_canonical": proposal.canonical,
            "word_type": proposal.word_type,
            "evidence_type": proposal.evidence_type,
            "outcome": outcome,
            "reason_code": reason_code,
            "reason_text": reason_text,
            "memory_id": memory_id,
            "created_at": mem_mod.now_iso(),
        },
    )
    return {
        "surface_form": proposal.surface_form,
        "canonical": proposal.canonical,
        "word_type": proposal.word_type,
        "evidence_type": proposal.evidence_type,
        "outcome": outcome,
        "reason_code": reason_code,
        "reason_text": reason_text,
        "memory_id": memory_id,
    }


def _prior_repetition_interactions(
    conn: sqlite3.Connection, canonical: str, exclude_interaction: int
) -> list[int]:
    """Earlier sightings of this word that were logged but not stored.

    This is how repetition accumulates without storing a memory on first sight: the
    refusals themselves are the record. It keeps RULE 5 intact — nothing is learned from a
    single sighting — while still letting ordinary use teach the system over time.
    """
    rows = db.query(
        conn,
        """
        SELECT DISTINCT interaction_id FROM learning_decisions
        WHERE proposed_canonical = ? AND evidence_type = 'repetition'
          AND outcome = 'rejected' AND interaction_id IS NOT NULL
          AND interaction_id != ?
        ORDER BY interaction_id
        """,
        (canonical, exclude_interaction),
    )
    return [int(r["interaction_id"]) for r in rows]


def _apply_proposal(
    conn: sqlite3.Connection,
    interaction_id: int,
    text_for_irrealis: str,
    proposal: Proposal,
    th: Thresholds,
    *,
    user_id: str,
    encoder: str,
) -> dict[str, Any]:
    # --- Refusal 1: hypothetical mentions assert nothing (evidence E7). ---
    if proposal.evidence_type in ("naming_frame", "repetition"):
        span = _find_span(text_for_irrealis, proposal.canonical)
        if span is not None and is_irrealis(text_for_irrealis, span):
            return _log(
                conn, interaction_id, proposal, "rejected", "REJECTED_IRREALIS",
                "the mention is hypothetical (\"might\", \"maybe\", \"if\"), so it asserts "
                "nothing about how this word is actually written",
            )

    existing = mem_mod.find_live(conn, user_id, normalize_key(proposal.canonical))

    # --- Already known: reinforce. ---
    if existing:
        before = float(existing["confidence"])
        updated = mem_mod.reinforce(
            conn, int(existing["id"]), evidence_type=proposal.evidence_type, th=th,
            interaction_id=interaction_id, excerpt=proposal.excerpt,
            observed_form=proposal.observed_form, observed_kind=proposal.observed_kind,
            encoder=encoder,
        )
        return _log(
            conn, interaction_id, proposal, "reinforced", "EVIDENCE_ADDED_TO_EXISTING",
            f"memory #{existing['id']} already held {existing['canonical_form']!r}; "
            f"{proposal.evidence_type} evidence moved confidence "
            f"{before:.2f} -> {float(updated['confidence']):.2f} ({updated['status']})",
            memory_id=int(existing["id"]),
        )

    # --- Authoritative evidence about a word we hold under a different spelling: supersede. ---
    if proposal.observed_form and proposal.evidence_type in ("user_edit", "user_spelling", "manual_entry"):
        prior = mem_mod.find_live(conn, user_id, normalize_key(proposal.observed_form))
        if prior:
            new = mem_mod.supersede(
                conn, int(prior["id"]), proposal.canonical, th=th,
                evidence_type=proposal.evidence_type, interaction_id=interaction_id,
                excerpt=proposal.excerpt, encoder=encoder,
            )
            return _log(
                conn, interaction_id, proposal, "superseded", "SUPERSEDED_PRIOR_CANONICAL",
                f"memory #{prior['id']} held {prior['canonical_form']!r}; authoritative "
                f"{proposal.evidence_type} evidence replaced it with {proposal.canonical!r} "
                f"as memory #{new['id']}, and the old form is kept as a variant",
                memory_id=int(new["id"]),
            )

    # --- Refusal 2: a token seen only inside a longer capitalised name is evidence
    #     for that name, not for the token. Without this, mentions of the colleague
    #     "Aditya Ghosh" manufactured a separate memory for "Aditya", which then
    #     inhibited every legitimate "Aditya" -> "Aaditya" correction. ---
    if proposal.evidence_type == "repetition" and proposal.in_phrase:
        return _log(
            conn, interaction_id, proposal, "rejected", "REJECTED_ONLY_SEEN_INSIDE_PHRASE",
            f"{proposal.canonical!r} appeared only as part of a longer capitalised name in "
            f"this observation, which is evidence about that name rather than about this "
            f"word on its own",
        )

    # --- Repetition needs to accumulate before anything is stored. ---
    if proposal.evidence_type == "repetition":
        priors = _prior_repetition_interactions(conn, proposal.canonical, interaction_id)
        total = len(priors) + 1
        projected = min(total * th.w_repetition_step, th.w_repetition_cap)
        if projected < th.candidate_floor:
            return _log(
                conn, interaction_id, proposal, "rejected", "INSUFFICIENT_EVIDENCE_REPETITION",
                f"seen {total} time(s); repetition evidence projects confidence "
                f"{projected:.2f}, below the {th.candidate_floor:.2f} floor for storing "
                f"anything. The sighting is recorded so a later one can build on it",
            )
        created = mem_mod.create(
            conn, canonical_form=proposal.canonical, word_type=proposal.word_type,
            evidence_type="repetition", th=th, user_id=user_id,
            interaction_id=priors[0] if priors else interaction_id,
            excerpt=proposal.excerpt, gloss=proposal.gloss, encoder=encoder,
        )
        for prior_id in priors[1:]:
            mem_mod.add_evidence(
                conn, int(created["id"]), evidence_type="repetition",
                interaction_id=prior_id, excerpt="earlier sighting", th=th,
            )
        mem_mod.add_evidence(
            conn, int(created["id"]), evidence_type="repetition",
            interaction_id=interaction_id, excerpt=proposal.excerpt, th=th,
        )
        final = mem_mod.refresh_confidence(
            conn, int(created["id"]), th, reason_code="EVIDENCE_REPETITION"
        )
        return _log(
            conn, interaction_id, proposal, final["status"], "LEARNED_FROM_REPETITION",
            f"seen {total} times across separate interactions; confidence "
            f"{float(final['confidence']):.2f} -> {final['status']}",
            memory_id=int(created["id"]),
        )

    # --- Suggestive / authoritative first sighting. ---
    created = mem_mod.create(
        conn, canonical_form=proposal.canonical, word_type=proposal.word_type,
        evidence_type=proposal.evidence_type, th=th, user_id=user_id,
        interaction_id=interaction_id, excerpt=proposal.excerpt, gloss=proposal.gloss,
        observed_form=proposal.observed_form, observed_kind=proposal.observed_kind,
        encoder=encoder,
    )
    cls = mem_mod.EVIDENCE_CLASS[proposal.evidence_type]
    return _log(
        conn, interaction_id, proposal, created["status"],
        "LEARNED_FROM_" + proposal.evidence_type.upper(),
        f"{cls} evidence ({proposal.evidence_type}) gave confidence "
        f"{float(created['confidence']):.2f} -> {created['status']}"
        + ("; only confirmed memories may change text" if created["status"] == "candidate" else ""),
        memory_id=int(created["id"]),
    )


def ingest_observation(
    conn: sqlite3.Connection,
    *,
    th: Thresholds,
    asr_text: str | None = None,
    formatted_text: str | None = None,
    user_edited_text: str | None = None,
    app_context: str | None = None,
    user_id: str = "default",
    kind: str = "observation",
    encoder: str = DEFAULT_ENCODER,
) -> LearningOutcome:
    """Record one observation and run the whole learning policy over it."""
    interaction_id = db.insert(
        conn,
        "interactions",
        {
            "user_id": user_id,
            "kind": kind,
            "asr_text": asr_text,
            "formatted_text": formatted_text,
            "user_edited_text": user_edited_text,
            "app_context": app_context,
            "created_at": mem_mod.now_iso(),
        },
    )

    primary = user_edited_text or formatted_text or asr_text or ""
    proposals: list[Proposal] = []

    if user_edited_text and formatted_text:
        proposals += _from_user_edit(formatted_text, user_edited_text, encoder=encoder)
    for source in filter(None, [user_edited_text, formatted_text, asr_text]):
        proposals += _from_spelling_instruction(source, encoder=encoder)
        break   # one spelling instruction per observation; the best-formatted text wins
    proposals += _from_naming_frame(primary)
    proposals += _from_repetition(primary)

    # Keep the strongest evidence per canonical form; weaker duplicates add nothing.
    strength = {"manual_entry": 5, "user_spelling": 4, "user_edit": 4, "naming_frame": 2, "repetition": 1}
    best: dict[str, Proposal] = {}
    for p in proposals:
        key = normalize_key(p.canonical)
        if key not in best or strength.get(p.evidence_type, 0) > strength.get(best[key].evidence_type, 0):
            best[key] = p

    outcome = LearningOutcome(interaction_id=interaction_id)
    for proposal in best.values():
        outcome.proposals.append(
            _apply_proposal(
                conn, interaction_id, primary, proposal, th,
                user_id=user_id, encoder=encoder,
            )
        )

    # App context is weak corroboration for memories the surface itself names (E5).
    if app_context:
        terms = {t for t in normalize_key(app_context).split() if len(t) > 2}
        for term in terms:
            mem = mem_mod.find_live(conn, user_id, term)
            if mem:
                mem_mod.reinforce(
                    conn, int(mem["id"]), evidence_type="app_context", th=th,
                    interaction_id=interaction_id,
                    excerpt=f"appeared in application context {app_context!r}",
                )
    return outcome
