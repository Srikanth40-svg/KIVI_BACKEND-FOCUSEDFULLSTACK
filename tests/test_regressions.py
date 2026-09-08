"""Regression tests — one per bug this system actually had.

Every test here failed at some point during development. They are kept because the
failures were not typos: each one was a design mistake that produced plausible-looking
wrong behaviour, which is exactly the kind that comes back. The docstrings say what went
wrong, so a future change that reintroduces the mistake gets told why it matters.

The full narrative, with the measured effect of each fix, is in docs/04-failure-analysis.md.
"""

from __future__ import annotations

from kivi import db, learning
from kivi import memory as mem_mod
from kivi.formatter import format_stub
from kivi.phonetics import kivi_code
from kivi.text import tokenize


# ── learning-side regressions ──────────────────────────────────────────────────

def test_captured_names_do_not_keep_the_sentence_full_stop(observe, find):
    """Was: 'Aaditya.' — the capture group allowed interior dots for "sarvam.ai", so it
    also swallowed the full stop and stored a memory with a period in its canonical form."""
    observe(formatted_text="Ask Aditya to review it. Actually, it's spelled Aaditya.")
    mem = find("Aaditya")
    assert mem is not None
    # The surface form is what matters here; `find` looks up by normalised key, and
    # "Aaditya." and "Aaditya" share one.
    assert mem["canonical_form"] == "Aaditya"
    assert not mem["canonical_form"].endswith(".")


def test_the_instruction_verb_is_not_learned_as_a_name(observe, find):
    """Was: a memory for the word 'spelled', because a second spelling pattern matched
    "Actually, it's spelled" and captured the verb as the name."""
    observe(formatted_text="Ask Aditya to review it. Actually, it's spelled Aaditya.")
    assert find("spelled") is None


def test_the_naming_pattern_stops_at_the_end_of_the_name(observe, find):
    """Was: 'Aaditya Labs and they' — the pattern was compiled with re.IGNORECASE, so its
    `[A-Z]` continuation matched lowercase words and the capture ran past the name."""
    observe(formatted_text="Our client is called Aaditya Labs and they need the integration.")
    assert find("Aaditya Labs") is not None
    assert find("Aaditya Labs and they") is None


def test_a_first_name_inside_a_full_name_is_not_extracted_on_its_own(observe, find):
    """Was: repeated mentions of the colleague "Aditya Ghosh" manufactured a separate
    memory for "Aditya", which then inhibited every legitimate Aditya -> Aaditya
    correction elsewhere. A token seen only inside a longer name is evidence about the
    name, not the token."""
    for text in [
        "My manager Aditya Ghosh signed off on the budget.",
        "Aditya Ghosh is joining the standup.",
        "I met Aditya Ghosh at the offsite.",
        "Aditya Ghosh approved the plan.",
    ]:
        observe(formatted_text=text)
    assert find("Aditya Ghosh") is not None
    assert find("Aditya") is None


def test_a_word_inside_a_phrase_still_accumulates_its_own_sightings(observe, find):
    """Was: the opposite over-correction. Suppressing a unigram whenever it also appeared
    inside a proposed phrase silently lost sightings, so "Sarvam" stalled one step below
    confirmed because its first sighting was inside "Sarvam Kivi"."""
    for text in [
        "The Sarvam Kivi service shipped.",
        "The Sarvam team is shipping next week.",
        "I joined Sarvam in March.",
        "Sarvam is hiring two more interns.",
        "Sarvam published the technical report.",
    ]:
        observe(formatted_text=text)
    assert find("Sarvam")["status"] == "confirmed"


def test_a_multi_word_name_made_of_ordinary_words_can_still_be_learned(observe, find):
    """Was: the per-token frequency floor (which correctly keeps 'Friday' out) was applied
    to phrases too, so a real company called "Amber Rail" was rejected outright."""
    observe(formatted_text="Our client is called Amber Rail and they want the migration.")
    observe(formatted_text="Amber Rail confirmed the contract this morning.")
    observe(formatted_text="Amber Rail wants the migration finished by June.")
    assert find("Amber Rail")["status"] == "confirmed"


def test_a_determiner_never_becomes_part_of_a_name(observe, find):
    """Guard for the fix above: sentence-initial capitalisation is indiscriminate, so
    "The Kubernetes cluster..." must not propose the name "The Kubernetes"."""
    for _ in range(4):
        observe(formatted_text="The Kubernetes cluster is healthy.")
    assert find("The Kubernetes") is None


def test_a_case_only_correction_is_learned(observe, find):
    """Was: invisible. The diff aligns on lowercased tokens so that incidental casing does
    not manufacture diffs — which meant a pure case fix landed in an "equal" block and was
    never seen. Every "cursor" -> "Cursor" style correction was silently discarded, and
    the Cursor memory the negative tests depend on never existed."""
    observe(
        formatted_text="We are switching the team to cursor next sprint.",
        user_edited_text="We are switching the team to Cursor next sprint.",
    )
    mem = find("Cursor")
    assert mem is not None and mem["status"] == "confirmed"


def test_capitalising_an_ordinary_word_is_not_a_free_orthographic_swap(
    observe, find, apply_text
):
    """Was: "cursor" -> "Cursor" was classified as an orthographic variant, which carries
    a zero context bar, so "move the cursor left" would have been rewritten
    unconditionally. Case IS the meaning distinction between a common and a proper noun.

    Asserted on behaviour rather than on the stored variant: a case-only observed form
    normalises to the canonical's own key, and the schema keeps one variant row per
    normalised form, so "cursor" is not recorded as a separate surface. The requirement is
    that the substitution still has to earn its context."""
    observe(
        formatted_text="We are switching the team to cursor next sprint.",
        user_edited_text="We are switching the team to Cursor next sprint.",
    )
    assert find("Cursor")["status"] == "confirmed"
    assert not apply_text("Move the cursor to the end of the line.").intervened
    assert not apply_text("The cursor keeps jumping while I type.").intervened


# ── phonetics and text regressions ─────────────────────────────────────────────

def test_the_phonetic_code_does_not_collapse_distinct_consonants():
    """Was: a final run-collapse on the finished code turned "Aditya to" (ADTT) into
    "Aaditya" (ADT), so the span "Aditya to" matched the memory and the word "to" was
    deleted from the output. Doubled letters are already collapsed on the input, so any
    repeat left in the code comes from two genuinely different consonants."""
    assert kivi_code("Aditya to") != kivi_code("Aaditya")


def test_silent_gh_is_silent_only_after_a_vowel():
    """Was: 'gh' mapped to G unconditionally, leaving a phantom consonant in "eighties"
    and breaking the "cuban eighties" -> "Kubernetes" collapse."""
    assert kivi_code("Ghosh").startswith("G")     # hard, word-initial
    assert "G" not in kivi_code("eighties")       # silent after a vowel


def test_quotes_are_not_part_of_the_token():
    """Was: the token pattern allowed a leading apostrophe, so the span for 'Cursor'
    included its quotes; is_quoted() never saw them and the metalinguistic veto never
    fired on any quoted word."""
    assert [t.text for t in tokenize("'Cursor' is odd")][0] == "Cursor"


def test_the_formatter_does_not_capitalise_a_whole_trailing_phrase():
    """Was: "Sarvam Kiwi Service" — the proper-noun compound rule chained indefinitely
    because it tested whether the previous token ended up capitalised rather than whether
    it was actually absent from ordinary English."""
    assert format_stub("review the sarvam kiwi service") == "Review the Sarvam Kiwi service."


# ── retrieval and gating regressions ───────────────────────────────────────────

def test_a_very_short_span_is_not_matched_against_a_long_memory(apply_text, seeded):
    """Was: Jaro-Winkler is length-normalised and rewards a shared prefix, so the single
    letter "a" scored 0.74 against "aaditya" and was admitted as a candidate."""
    result = apply_text("Give a copy to the team.")
    assert not result.intervened


def test_function_words_glued_together_do_not_match_a_name(apply_text, seeded):
    """Was: "Ask Aditya" -> "@aaditya_k" and "I ate a" -> "Aaditya". Concatenating
    function words produces a string long enough to clear a length-normalised similarity
    threshold, so cold fuzzy matching must require the token counts to agree."""
    assert not apply_text("I ate a kiwi on the flight.").intervened
    assert apply_text("Ask Aditya to review the PR.").memory_aware_text == (
        "Ask Aaditya to review the PR."
    )


def test_a_multi_token_learned_variant_is_actually_reachable(apply_text, seeded):
    """Was: the query-side n-gram window was sized from canonical forms only, all of which
    are one token. Multi-token wrong forms like "Cuban Eighties" could therefore never be
    generated as a span, so a capability the seed demonstrably taught did nothing."""
    assert apply_text("The Cuban Eighties cluster is down.").memory_aware_text == (
        "The Kubernetes cluster is down."
    )


def test_a_single_function_word_cannot_carry_the_context_gate(apply_text, seeded):
    """Was: the learned context profile kept any token longer than two characters, so
    "the" counted as supporting evidence and by itself pushed a substitution over the bar,
    turning "post grease warnings near the fryer" into "Postgres warnings near the fryer"."""
    result = apply_text("We need to post grease warnings near the fryer.")
    assert not result.intervened


def test_a_candidate_memory_inhibits_others_but_never_itself(apply_text, seeded, conn, th):
    """Was two bugs in one place. First, a confirmed memory rewrote a *different* real
    colleague's correctly-spelled name, because weak evidence for "Aditya Ghosh" was
    ignored entirely. Then the fix over-reached and a candidate memory blocked its own
    correction."""
    assert not apply_text("Aditya Ghosh approved the budget.").intervened

    created = mem_mod.create(
        conn, canonical_form="Zorvex", word_type="product",
        evidence_type="naming_frame", th=th, excerpt="candidate only",
    )
    mem_mod.add_variant(conn, created["id"], "Zorvecks", kind="asr_error")
    result = apply_text("Deploy Zorvecks to staging.")
    codes = {c.reason_code for c in result.candidates}
    assert "BLOCKED_SPAN_IS_CANDIDATE_CANONICAL" not in codes


def test_migrations_apply_atomically(config):
    """Was: the migrator wrapped executescript() in an explicit BEGIN, but executescript
    commits any open transaction before it runs, so the DDL executed unprotected and the
    subsequent COMMIT raised 'cannot commit - no transaction is active'."""
    conn = db.connect(config.db_path)
    assert db.migrate(conn) == ["001_init"]
    assert db.migrate(conn) == []            # idempotent
    assert "001_init" in db.applied_versions(conn)
    conn.close()


def test_the_database_can_be_used_from_several_threads(config):
    """Was: the API shared one connection across FastAPI's threadpool, which SQLite
    rejects outright with 'SQLite objects created in a thread can only be used in that
    same thread'."""
    import threading

    conn = db.connect(config.db_path)
    db.migrate(conn)
    conn.close()

    errors: list[Exception] = []

    def work() -> None:
        try:
            c = db.connect(config.db_path)
            c.execute("SELECT COUNT(*) FROM word_memories").fetchone()
            c.close()
        except Exception as exc:  # pragma: no cover - only on regression
            errors.append(exc)

    threads = [threading.Thread(target=work) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors


def test_eval_counters_accumulate(config):
    """Was: the runner zeroed a counter immediately before incrementing it, so the
    application metrics were computed from mostly-empty counts."""
    from kivi.eval.metrics import ApplyCounters

    counters = ApplyCounters()
    for _ in range(3):
        counters.correct_intervention += 1
    assert counters.correct_intervention == 3
    assert counters.total == 3
