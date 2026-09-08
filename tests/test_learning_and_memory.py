"""Learning policy, confidence, and the memory lifecycle."""

from __future__ import annotations

from kivi import db
from kivi import memory as mem_mod
from kivi.seed import load_seed, replay_seed


# ── evidence strength decides what happens ─────────────────────────────────────

def test_a_correction_confirms_immediately(observe, find):
    observe(
        formatted_text="Review the Sarvam Kiwi service before Friday.",
        user_edited_text="Review the Sarvam Kivi service before Friday.",
    )
    mem = find("Kivi")
    assert mem["status"] == "confirmed"
    assert mem["confidence"] >= 0.9
    assert mem["word_type"] == "product"


def test_a_correction_records_the_wrong_form_it_answers_to(observe, find, conn):
    observe(
        formatted_text="Review the Sarvam Kiwi service.",
        user_edited_text="Review the Sarvam Kivi service.",
    )
    variants = mem_mod.variants_for(conn, find("Kivi")["id"])
    assert {v["variant_form"] for v in variants} == {"Kivi", "Kiwi"}
    assert {v["kind"] for v in variants} == {"canonical", "asr_error"}


def test_a_spoken_spelling_confirms_immediately(observe, find):
    observe(formatted_text="Ask Aditya to review it. Actually, it's spelled Aaditya.")
    assert find("Aaditya")["status"] == "confirmed"


def test_a_naming_frame_only_earns_a_candidate(observe, find):
    observe(formatted_text="Our client is called Aaditya Labs and they need the integration.")
    mem = find("Aaditya Labs")
    assert mem["status"] == "candidate"
    assert mem["confidence"] < 0.7


def test_a_hypothetical_mention_teaches_nothing(observe, find, conn):
    observe(formatted_text="We might call the new service Kivali if the name clears legal.")
    assert find("Kivali") is None
    rows = db.query(
        conn, "SELECT * FROM learning_decisions WHERE proposed_canonical = 'Kivali'"
    )
    assert rows and rows[0]["outcome"] == "rejected"
    assert rows[0]["reason_code"] == "REJECTED_IRREALIS"


def test_a_single_sighting_stores_nothing(observe, find):
    observe(formatted_text="Kshatriya presented the evaluation results.")
    assert find("Kshatriya") is None


def test_repetition_accumulates_across_separate_interactions(observe, find):
    for text in [
        "Kshatriya presented the evaluation results.",
        "I sent Kshatriya the latency numbers.",
    ]:
        observe(formatted_text=text)
    assert find("Kshatriya")["status"] == "candidate"

    for text in [
        "Kshatriya is on leave next week.",
        "Kshatriya reviewed the retrieval design.",
    ]:
        observe(formatted_text=text)
    assert find("Kshatriya")["status"] == "confirmed"


def test_ordinary_words_are_never_learned_by_repetition(observe, find):
    for _ in range(6):
        observe(formatted_text="The cluster is down and the cache is cold.")
    assert find("cluster") is None
    assert find("cache") is None


def test_globally_famous_names_are_never_learned_by_repetition(observe, find):
    for text in [
        "Friday works for the review.", "Friday is a public holiday.",
        "Move it to Friday afternoon.", "Friday and Monday are blocked.",
    ]:
        observe(formatted_text=text)
    assert find("Friday") is None


def test_a_rewrite_teaches_nothing_because_this_learns_vocabulary_not_style(observe, conn):
    observe(
        formatted_text="I rewrote the paragraph about latency because it was unclear.",
        user_edited_text="I rewrote the section on response times since readers were confused.",
    )
    learned = db.query(
        conn, "SELECT * FROM learning_decisions WHERE outcome IN ('confirmed','candidate')"
    )
    assert learned == []


def test_a_spelling_preference_is_typed_as_a_preference(observe, find):
    observe(
        formatted_text="Use the grey background for the dashboard.",
        user_edited_text="Use the gray background for the dashboard.",
    )
    mem = find("gray")
    assert mem["word_type"] == "preference"


def test_every_refusal_is_recorded_with_a_reason(observe, conn):
    observe(formatted_text="Kshatriya presented the evaluation results.")
    rows = db.rows_to_dicts(
        db.query(conn, "SELECT * FROM learning_decisions WHERE outcome = 'rejected'")
    )
    assert rows
    assert all(r["reason_code"] and r["reason_text"] for r in rows)


# ── confidence model ───────────────────────────────────────────────────────────

def test_authoritative_evidence_outranks_any_amount_of_repetition(th):
    auth = [{"evidence_type": "user_edit", "weight": 0.9}]
    many = [{"evidence_type": "repetition", "weight": 0.18}] * 10
    assert mem_mod.compute_confidence(auth, th)[0] > mem_mod.compute_confidence(many, th)[0]


def test_repetition_alone_can_never_reach_certainty(th):
    many = [{"evidence_type": "repetition", "weight": 0.18}] * 50
    assert mem_mod.compute_confidence(many, th)[0] <= th.w_repetition_cap < 1.0


def test_app_context_alone_cannot_promote_anything(th):
    weak = [{"evidence_type": "app_context", "weight": 0.05}] * 20
    conf, _ = mem_mod.compute_confidence(weak, th)
    assert conf <= th.w_app_context_cap < th.candidate_floor


def test_confidence_always_comes_with_an_explanation(th):
    _, why = mem_mod.compute_confidence(
        [{"evidence_type": "naming_frame", "weight": 0.4},
         {"evidence_type": "repetition", "weight": 0.18}], th
    )
    assert "suggestive base" in why and "repetition" in why


# ── lifecycle ──────────────────────────────────────────────────────────────────

def test_changing_a_spelling_supersedes_rather_than_overwrites(conn, th, observe, find):
    observe(formatted_text="Ask Sumit to review. Actually, it's spelled Sumeet.")
    old = find("Sumeet")
    new = mem_mod.supersede(conn, old["id"], "Sumit", th=th)

    refreshed = mem_mod.get(conn, old["id"])
    assert refreshed["status"] == "superseded"
    assert refreshed["superseded_by"] == new["id"]
    assert refreshed["canonical_form"] == "Sumeet"          # history preserved
    assert new["status"] == "confirmed"


def test_supersession_carries_the_old_form_across_as_a_variant(conn, th, observe, find):
    observe(formatted_text="Ask Sumit to review. Actually, it's spelled Sumeet.")
    new = mem_mod.supersede(conn, find("Sumeet")["id"], "Sumit", th=th)
    forms = {v["variant_form"] for v in mem_mod.variants_for(conn, new["id"])}
    assert "Sumeet" in forms


def test_deletion_is_a_recorded_transition_not_a_vanishing_row(conn, th, observe, find):
    observe(
        formatted_text="Review the Sarvam Kiwi service.",
        user_edited_text="Review the Sarvam Kivi service.",
    )
    mem_id = find("Kivi")["id"]
    mem_mod.soft_delete(conn, mem_id, reason="test")

    after = mem_mod.get(conn, mem_id)
    assert after["status"] == "deleted" and after["deleted_at"]
    assert "deleted" in [e["event"] for e in mem_mod.events_for(conn, mem_id)]


def test_a_deleted_memory_can_be_restored(conn, th, observe, find):
    observe(
        formatted_text="Review the Sarvam Kiwi service.",
        user_edited_text="Review the Sarvam Kivi service.",
    )
    mem_id = find("Kivi")["id"]
    mem_mod.soft_delete(conn, mem_id)
    mem_mod.restore(conn, mem_id, th)
    assert mem_mod.get(conn, mem_id)["status"] in ("candidate", "confirmed")


def test_late_evidence_does_not_resurrect_a_deleted_memory(conn, th, observe, find):
    observe(
        formatted_text="Review the Sarvam Kiwi service.",
        user_edited_text="Review the Sarvam Kivi service.",
    )
    mem_id = find("Kivi")["id"]
    mem_mod.soft_delete(conn, mem_id)
    mem_mod.refresh_confidence(conn, mem_id, th)
    assert mem_mod.get(conn, mem_id)["status"] == "deleted"


def test_every_mutation_leaves_an_audit_row(conn, th, observe, find):
    observe(
        formatted_text="Review the Sarvam Kiwi service.",
        user_edited_text="Review the Sarvam Kivi service.",
    )
    events = mem_mod.events_for(conn, find("Kivi")["id"])
    assert [e["event"] for e in events][0] == "created"
    assert all(e["reason_code"] for e in events)


# ── seed determinism and reset ─────────────────────────────────────────────────

def test_the_seed_is_deterministic(conn, config):
    def snapshot():
        return [
            (m["canonical_form"], m["word_type"], m["status"], round(m["confidence"], 4))
            for m in mem_mod.list_memories(conn)
        ]

    replay_seed(conn, config, load_seed())
    first = snapshot()
    db.reset(conn)
    replay_seed(conn, config, load_seed())
    assert snapshot() == first


def test_reset_empties_every_table(seeded, config):
    deleted = db.reset(seeded)
    assert sum(deleted.values()) > 0
    stats = db.storage_stats(seeded, config.db_path)
    assert all(count == 0 for count in stats["row_counts"].values())


def test_the_seed_produces_the_vocabulary_the_demo_relies_on(seeded, find):
    for word in ["Kivi", "Aaditya", "Kubernetes", "OpenAI", "EPD", "gray", "Bengaluru"]:
        mem = find(word)
        assert mem is not None, f"seed did not learn {word!r}"
        assert mem["status"] == "confirmed", f"{word!r} is {mem['status']}, not confirmed"


def test_the_seed_leaves_some_memories_deliberately_unconfirmed(seeded, find):
    """Weak evidence must be visible and inert, or N11 cannot be demonstrated."""
    assert find("Aaditya Labs")["status"] == "candidate"
