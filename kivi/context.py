"""The context gate.

Similarity says a stored word *could* be the word that was heard. Context decides whether
it *is*. These are separate questions and this system keeps them separate: a candidate must
clear both, independently. Collapsing them into one score is what turns a memory system
into a find-and-replace that mangles "I ate a kiwi".

The gate has two halves:

  1. **The bar** (`required_context`) — how much evidence this particular substitution must
     produce before it is allowed. Set by what is at stake, not by the candidate's score:
     replacing an ordinary English word is dangerous, replacing a string that means nothing
     in English is cheap, and a meaning-preserving spelling swap ("grey"->"gray") is free.
  2. **The evidence** (`context_score`) — how much the surrounding words actually vouch for
     this memory, from a profile the memory learned itself plus type-appropriate cues.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import Thresholds
from .lexicon import span_ordinariness
from .text import Span, context_tokens, is_metalinguistic, normalize_key

# Content words that make a given kind of memory plausible in the sentence around it.
# Deliberately no function words: "the"/"to"/"and" vouch for nothing, and including them
# would let any sentence clear the bar.
TYPE_TRIGGERS: dict[str, set[str]] = {
    "person": {
        "ask", "asked", "asking", "tell", "told", "met", "meet", "meeting", "email",
        "emailed", "ping", "pinged", "call", "called", "dm", "cc", "loop", "sync",
        "reviewer", "review", "colleague", "manager", "team", "said", "says", "mentioned",
        "thanks", "birthday", "hired", "joined", "spoke", "chat", "standup", "assign",
        "assigned", "reports", "intern", "candidate", "interview",
    },
    "org": {
        "company", "startup", "client", "vendor", "acquired", "acquisition", "raised",
        "funding", "round", "hired", "joined", "partner", "partnership", "office", "team",
        "customer", "contract", "invoice", "vendor", "enterprise", "founded",
    },
    "product": {
        "service", "app", "product", "deploy", "deployed", "deployment", "ship", "shipped",
        "release", "released", "version", "build", "feature", "bug", "dashboard", "api",
        "launch", "demo", "repo", "pr", "review", "update", "integration", "backend",
        "frontend", "install", "using", "onboarding", "signup", "users", "latency",
    },
    "project": {
        "project", "milestone", "sprint", "roadmap", "kickoff", "scope", "deadline", "spec",
        "launch", "phase", "workstream", "epic", "ticket", "backlog", "planning",
    },
    "term": {
        "install", "cluster", "deploy", "server", "database", "query", "index", "cache",
        "container", "pod", "model", "training", "inference", "latency", "endpoint",
        "library", "package", "version", "config", "migration", "schema", "pipeline",
        "runtime", "memory", "throughput", "benchmark", "gpu", "node",
    },
    "acronym": {
        "team", "report", "metric", "metrics", "review", "meeting", "doc", "document",
        "process", "target", "quarter", "goal", "goals", "dashboard", "spec",
    },
    "handle": {
        "dm", "message", "slack", "mention", "mentioned", "tag", "tagged", "follow",
        "twitter", "github", "handle", "username", "profile", "ping",
    },
    "place": {
        "office", "city", "based", "flight", "travel", "visit", "visiting", "moved",
        "meetup", "campus", "team", "trip", "relocate", "airport", "hotel",
    },
    "preference": set(),   # meaning-preserving spelling choices need no situational support
}


@dataclass
class ContextAssessment:
    score: float
    required: float
    passed: bool
    vetoed: bool = False
    veto_reason: str | None = None
    is_ordinary: bool = False
    min_rank: int = 0
    signals: dict[str, Any] = field(default_factory=dict)


def required_context(
    span_tokens: tuple[str, ...] | list[str],
    *,
    variant_kind: str,
    word_type: str,
    th: Thresholds,
    match_tier: str = "fuzzy",
    looks_proper: bool = False,
) -> tuple[float, bool, int, str]:
    """How much context this substitution must earn. Returns (bar, is_ordinary, rank, why).

    The reasoning, in the order it is applied:

    * An `orthographic` variant is the same word spelled differently ("grey"/"gray",
      "Bengaluru"/"Bangalore"). Substituting it cannot change what the sentence means, so
      it needs no situational support at all. This is taxonomy A11 — the class only a
      *personal* memory can serve, since there is no globally correct answer.
    * If every token in the heard span is an ordinary English word, the span has a
      legitimate reading already and overwriting it risks destroying correct text. The bar
      rises, and rises further for very common words — "add it" (rank 16) must be far
      harder to overwrite than "kiwi" (rank 16,870).
    * Otherwise the heard form means nothing in English, so intervening is cheap.
    """
    is_ordinary, min_rank = span_ordinariness(list(span_tokens))
    exact = match_tier in ("exact", "variant")

    # The bar guards against MISIDENTIFICATION. So its height depends on two things: how
    # much damage a wrong substitution would do, and how uncertain the identification is.
    # An exact match against a form this person themselves corrected is not a guess.

    if variant_kind == "orthographic" and exact:
        return th.ctx_required_orthographic, is_ordinary, min_rank, (
            "an exactly-matched, meaning-preserving spelling variant: substituting it "
            "cannot change what the sentence means, so no situational evidence is needed"
        )

    if exact:
        # The one genuinely dangerous case left: the heard form is an ordinary English
        # word written in lower case. Then the formatting stage judged it a common noun
        # and it very likely is one — "I ate a kiwi", "move the cursor".
        if is_ordinary and not looks_proper:
            bar = (
                th.ctx_required_ordinary_common
                if min_rank <= th.ctx_common_rank
                else th.ctx_required_ordinary
            )
            return bar, is_ordinary, min_rank, (
                f"the heard form is an ordinary English word (rank {min_rank}) written in "
                f"lower case, so the formatting stage read it as a common noun and strong "
                f"context is required before overwriting it"
            )
        why = (
            "the heard form is capitalised mid-sentence, so the formatting stage already "
            "judged it a proper noun"
            if is_ordinary
            else "the heard form is not an ordinary English word"
        )
        return th.ctx_required_orthographic, is_ordinary, min_rank, (
            f"exact match on a form this person corrected before, and {why}; identity is "
            f"not in doubt, so no further situational evidence is required"
        )

    # Cold phonetic or fuzzy match: identity ITSELF is uncertain, so every case needs
    # real support. Without this, an unseen name was rewritten into a known one purely on
    # spelling similarity ("Verdance" -> "Vercel"), which is how a memory system starts
    # renaming people.
    if is_ordinary and min_rank <= th.ctx_common_rank:
        return th.ctx_required_ordinary_common, is_ordinary, min_rank, (
            f"an inexact match onto a very common English word (rank {min_rank}) is the "
            f"highest-risk substitution there is"
        )
    if is_ordinary:
        return th.ctx_required_ordinary, is_ordinary, min_rank, (
            f"an inexact match onto an ordinary English word (rank {min_rank}), which "
            f"already has a legitimate reading"
        )
    return th.ctx_required_fuzzy, is_ordinary, min_rank, (
        "an inexact match: the heard form is not ordinary English, but the identification "
        "is a guess rather than something this person taught us, so it needs support"
    )


def assess(
    *,
    text: str,
    span: Span,
    memory: dict[str, Any],
    variant_kind: str,
    profile: set[str],
    app_context: str | None,
    th: Thresholds,
    match_tier: str = "fuzzy",
) -> ContextAssessment:
    """Score how much the surroundings vouch for this memory, then compare to the bar."""
    # Sentence-initial capitalisation is uninformative: the formatter capitalises every
    # sentence start. Only a capital in mid-sentence position carries the formatter's
    # judgement that the token is a proper noun.
    sentence_initial = span.start == 0 or text[:span.start].rstrip()[-1:] in {".", "!", "?", ""}
    looks_proper = bool(span.tokens[0][:1].isupper() and not sentence_initial)

    bar, is_ordinary, min_rank, bar_why = required_context(
        span.tokens, variant_kind=variant_kind, word_type=memory["word_type"], th=th,
        match_tier=match_tier, looks_proper=looks_proper,
    )

    # Hard veto: the word is being discussed as a word, not used (taxonomy N7).
    if is_metalinguistic(text, span):
        return ContextAssessment(
            score=0.0, required=bar, passed=False, vetoed=True,
            veto_reason="the span is quoted or introduced by a metalinguistic cue "
                        "(\"the word ...\", \"spelled ...\"), so it is being talked about, not used",
            is_ordinary=is_ordinary, min_rank=min_rank,
            signals={"metalinguistic": True, "bar_reason": bar_why},
        )

    around = context_tokens(text, span)
    app_terms = {t for t in normalize_key(app_context or "").split() if len(t) > 2}

    # 1. The memory's own learned co-occurrence profile.
    profile_hits = sorted(around & profile)
    profile_signal = min(1.0, len(profile_hits) / 2.0)

    # 2. Cues appropriate to what kind of thing this memory is.
    triggers = TYPE_TRIGGERS.get(memory["word_type"], set())
    trigger_hits = sorted(around & triggers)
    type_signal = min(1.0, len(trigger_hits) / 2.0)

    # 3. Where the person is typing (window title / repo / channel). Weak by design.
    mem_key_parts = set(normalize_key(memory["canonical_form"]).split())
    app_hits = sorted(app_terms & (mem_key_parts | profile))
    app_signal = 1.0 if app_hits else 0.0

    # 4. Capitalised mid-sentence: the formatter already thought this was a proper noun.
    caps_signal = 1.0 if looks_proper else 0.0

    raw = 0.55 * profile_signal + 0.35 * type_signal + 0.25 * app_signal + 0.15 * caps_signal
    score = min(1.0, raw)

    return ContextAssessment(
        score=score,
        required=bar,
        passed=score >= bar,
        is_ordinary=is_ordinary,
        min_rank=min_rank,
        signals={
            "profile_hits": profile_hits,
            "profile_signal": round(profile_signal, 3),
            "trigger_hits": trigger_hits,
            "type_signal": round(type_signal, 3),
            "app_hits": app_hits,
            "app_signal": app_signal,
            "capitalised_midsentence": looks_proper,
            "sentence_initial": sentence_initial,
            "bar_reason": bar_why,
            "variant_kind": variant_kind,
            "is_ordinary_word": is_ordinary,
            "min_frequency_rank": None if min_rank >= 10**9 else min_rank,
        },
    )
