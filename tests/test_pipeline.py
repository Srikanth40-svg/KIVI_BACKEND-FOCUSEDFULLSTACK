"""Retrieval, the context gate, and the end-to-end three-stage pipeline.

The negative tests here matter more than the positive ones: a false correction damages
text the person got right, which is this product's worst failure.
"""

from __future__ import annotations

import pytest

from kivi import memory as mem_mod
from kivi import pipeline


# ── the brief's own example, end to end through real state ─────────────────────

def test_the_briefs_example_from_asr_to_memory_aware(seeded, config):
    result = pipeline.memory_aware_format(
        seeded, config, asr_text="ask aditya to review the sarvam kiwi service"
    )
    assert result.formatted_text == "Ask Aditya to review the Sarvam Kiwi service."
    assert result.memory_aware_text == "Ask Aaditya to review the Sarvam Kivi service."
    assert result.intervened


def test_nothing_happens_when_memory_is_empty(conn, config):
    """Proof the corrections come from stored state, not from hardcoded rules."""
    result = pipeline.memory_aware_format(
        conn, config, asr_text="ask aditya to review the sarvam kiwi service"
    )
    assert result.memory_aware_text == result.formatted_text
    assert not result.intervened


# ── interventions ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "formatted,expected",
    [
        ("Ship the Kiwi update on Friday.", "Ship the Kivi update on Friday."),
        ("The Kiwi service is down for everyone.", "The Kivi service is down for everyone."),
        ("Ask Aditya to review the PR.", "Ask Aaditya to review the PR."),
        ("The Cuban Eighties cluster is down again.", "The Kubernetes cluster is down again."),
        ("The Post Grease connection is timing out.", "The Postgres connection is timing out."),
        ("Compare it with Open Ai and Anthropic.", "Compare it with OpenAI and Anthropic."),
        ("Use the grey background for the dashboard.", "Use the gray background for the dashboard."),
        ("The Bangalore office is closed on Monday.", "The Bengaluru office is closed on Monday."),
        ("Send the metrics to E P D before the review.", "Send the metrics to EPD before the review."),
        ("Wishal owns the ASR pipeline.", "Vishal owns the ASR pipeline."),
        ("Kiwi's onboarding flow is confusing.", "Kivi's onboarding flow is confusing."),
    ],
)
def test_useful_corrections_are_applied(apply_text, seeded, formatted, expected):
    assert apply_text(formatted).memory_aware_text == expected


def test_morphology_survives_the_substitution(apply_text, seeded):
    """Apply the canonical stem, keep the inflection (taxonomy A10)."""
    out = apply_text("Kiwi's onboarding flow is confusing.").memory_aware_text
    assert out.startswith("Kivi's")


# ── deliberate non-intervention ────────────────────────────────────────────────

@pytest.mark.parametrize(
    "formatted",
    [
        "I ate a kiwi on the flight.",
        "Add a kiwi to the fruit salad.",
        "Peel the kiwi before slicing it.",
        "Move the cursor to the end of the line.",
        "The cursor keeps jumping while I type.",
        "Add it to the list before the standup.",
        "Give me a minute to finish this.",
        "The kitty is asleep on my keyboard.",
        "The word 'kiwi' has four letters.",
        "Aditya Ghosh approved the budget.",
        "We need to post grease warnings near the fryer.",
        "Remind me to book the flight and pay the electricity bill.",
    ],
)
def test_text_that_must_be_left_alone_is_left_alone(apply_text, seeded, formatted):
    result = apply_text(formatted)
    assert result.memory_aware_text == result.formatted_text, (
        f"falsely corrected: {result.memory_aware_text!r}"
    )


def test_an_abstention_always_carries_a_reason(apply_text, seeded):
    result = apply_text("I ate a kiwi on the flight.")
    abstentions = [c for c in result.candidates if c.action == "abstained"]
    assert abstentions
    assert all(c.reason_code and c.reason_text for c in abstentions)


def test_the_ordinary_word_guard_is_the_stated_reason_for_the_fruit(apply_text, seeded):
    result = apply_text("I ate a kiwi on the flight.")
    codes = {c.reason_code for c in result.candidates}
    assert "ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK" in codes


def test_a_quoted_word_is_vetoed_as_metalinguistic(apply_text, seeded):
    result = apply_text("The word 'cursor' is oddly chosen for an editor.")
    codes = {c.reason_code for c in result.candidates}
    assert "ABSTAIN_METALINGUISTIC" in codes


def test_already_correct_text_is_recorded_as_a_no_op(apply_text, seeded):
    result = apply_text("Ship the Kivi update on Friday.")
    assert not result.intervened
    assert any(c.action == "noop" for c in result.candidates)


# ── status gating ──────────────────────────────────────────────────────────────

def test_a_candidate_memory_is_visible_but_inert(apply_text, seeded, conn, find):
    mem_id = find("Kivi")["id"]
    conn.execute("UPDATE word_memories SET status='candidate' WHERE id=?", (mem_id,))
    result = apply_text("Ship the Kiwi update on Friday.")
    assert not result.intervened
    assert "ABSTAIN_MEMORY_CANDIDATE_ONLY" in {c.reason_code for c in result.candidates}


def test_a_deleted_memory_stops_affecting_output(apply_text, seeded, conn, find):
    before = apply_text("Ship the Kiwi update on Friday.")
    assert before.intervened

    mem_mod.soft_delete(conn, find("Kivi")["id"])
    after = apply_text("Ship the Kiwi update on Friday.")
    assert not after.intervened


def test_a_superseded_memory_stops_winning_and_the_new_form_takes_over(
    apply_text, seeded, conn, th, find
):
    mem_mod.supersede(conn, find("Sumeet")["id"], "Sumit", th=th)
    assert apply_text("Sumeet is reviewing the code.").memory_aware_text == (
        "Sumit is reviewing the code."
    )
    # ...and the new canonical is not corrected back.
    assert not apply_text("Sumit is reviewing the code.").intervened


# ── competing memories ────────────────────────────────────────────────────────

def test_two_equally_good_answers_produce_an_abstention_not_a_guess(
    apply_text, seeded, conn, th
):
    created = mem_mod.create(
        conn, canonical_form="Kiwee", word_type="org", evidence_type="manual_entry",
        th=th, excerpt="a client, unrelated to the product",
    )
    mem_mod.add_variant(conn, created["id"], "kiwi", kind="asr_error")

    result = apply_text("The Kiwi meeting moved to Thursday.")
    assert not result.intervened
    assert "ABSTAIN_AMBIGUOUS_COMPETING" in {c.reason_code for c in result.candidates}


def test_context_still_resolves_competing_memories_when_it_can(apply_text, seeded, conn, th):
    """Competing memories are not automatically ambiguous ones."""
    created = mem_mod.create(
        conn, canonical_form="Kiwee", word_type="org", evidence_type="manual_entry",
        th=th, excerpt="a client",
    )
    mem_mod.add_variant(conn, created["id"], "kiwi", kind="asr_error")
    assert apply_text("Ship the Kiwi update on Friday.").memory_aware_text == (
        "Ship the Kivi update on Friday."
    )


def test_the_wider_span_wins_over_a_token_inside_it(apply_text, seeded):
    result = apply_text("The Cuban Eighties cluster is down again.")
    applied = [c for c in result.candidates if c.action == "applied"]
    assert len(applied) == 1
    assert applied[0].span.token_count == 2


# ── observability ──────────────────────────────────────────────────────────────

def test_every_decision_is_persisted_and_replayable(apply_text, seeded, conn):
    result = apply_text("Ship the Kiwi update on Friday.")
    trace = pipeline.decision_trace(conn, result.decision_id)
    assert trace["memory_aware_text"] == result.memory_aware_text
    assert trace["candidates"]
    assert all(c["reason_code"] for c in trace["candidates"])


def test_the_trace_records_scores_and_the_bar_that_was_applied(apply_text, seeded, conn):
    result = apply_text("I ate a kiwi on the flight.")
    trace = pipeline.decision_trace(conn, result.decision_id)
    row = next(c for c in trace["candidates"] if c["span_text"] == "kiwi")
    assert row["required_context"] > 0
    assert row["is_ordinary_word"] == 1
    assert "bar_reason" in row["signals"]


def test_explain_returns_all_three_stages_and_every_group(apply_text, seeded):
    payload = pipeline.explain(apply_text("Ship the Kiwi update on Friday."))
    assert set(payload["stages"]) == {"asr", "formatted", "memory_aware"}
    for key in ("applied", "abstained", "noop", "blocked", "timings", "model_usage"):
        assert key in payload


def test_latency_is_actually_measured(apply_text, seeded):
    timings = apply_text("Ship the Kiwi update on Friday.").timings
    assert timings["retrieval_ms"] >= 0 and timings["total_ms"] > 0


def test_no_model_calls_happen_in_the_default_configuration(apply_text, seeded):
    usage = apply_text("Ship the Kiwi update on Friday.").usage
    assert usage.calls == 0 and usage.cost_inr == 0.0
