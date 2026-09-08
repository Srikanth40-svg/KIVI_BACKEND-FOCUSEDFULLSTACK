"""Unit tests: text handling, phonetics, the lexicon prior, and the formatter stand-in."""

from __future__ import annotations

import pytest

from kivi.formatter import format_stub
from kivi.lexicon import is_ordinary_word, rank, span_ordinariness
from kivi.phonetics import (
    jaro_winkler,
    kivi_code,
    metaphone_compact,
    phonetic_similarity,
    soundex,
)
from kivi.text import (
    apply_morphology,
    is_metalinguistic,
    is_irrealis,
    match_case,
    morphology_candidates,
    normalize_compact,
    normalize_key,
    rewrite,
    spans,
    tokenize,
)


# ── tokenisation ───────────────────────────────────────────────────────────────

def test_tokenizer_keeps_internal_apostrophe_but_not_quotes():
    assert [t.text for t in tokenize("Kivi's flow")] == ["Kivi's", "flow"]
    assert [t.text for t in tokenize("'Cursor' is odd")] == ["Cursor", "is", "odd"]


def test_tokenizer_keeps_handles_and_dotted_names_whole():
    got = [t.text for t in tokenize("DM @aaditya_k about sarvam.ai and kivi-backend")]
    assert "@aaditya_k" in got and "sarvam.ai" in got and "kivi-backend" in got


def test_normalisation_never_loses_the_surface_form():
    assert normalize_key("Sarvam Kivi") == "sarvam kivi"
    assert normalize_compact("open ai") == "openai" == normalize_compact("OpenAI")
    assert normalize_key("Ādityā") == "aditya"
    assert normalize_compact("@aaditya_k") == "aadityak"


def test_rewrite_preserves_everything_outside_the_edits():
    text = "Ask Aditya to review the Sarvam Kiwi service."
    a, b = text.index("Aditya"), text.index("Kiwi")
    out = rewrite(text, [(a, a + len("Aditya"), "Aaditya"), (b, b + len("Kiwi"), "Kivi")])
    assert out == "Ask Aaditya to review the Sarvam Kivi service."


def test_spans_are_bounded_by_the_requested_width():
    assert {s.token_count for s in spans("a b c d e", max_tokens=3)} == {1, 2, 3}


# ── morphology ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "token,expected_stem,expected_suffix",
    [
        ("kiwis", "kiwi", "plural"),
        ("kiwi's", "kiwi", "possessive"),
        ("OpenAIs", "OpenAI", "plural"),
    ],
)
def test_morphology_offers_the_uninflected_reading(token, expected_stem, expected_suffix):
    readings = morphology_candidates(token)
    assert (expected_stem, expected_suffix) in [(m.stem, m.suffix) for m in readings]


def test_morphology_always_offers_the_token_unchanged_first():
    assert morphology_candidates("boss")[0].stem == "boss"


def test_inflection_is_reattached_with_english_orthography():
    assert apply_morphology("Kivi", "possessive") == "Kivi's"
    assert apply_morphology("Kivi", "plural") == "Kivis"
    assert apply_morphology("EPD", "possessive") == "EPD's"


def test_canonical_casing_wins_except_when_shouting():
    assert match_case("OpenAI", "open") == "OpenAI"
    assert match_case("Kivi", "KIWI") == "KIVI"


# ── phonetics ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "a,b",
    [
        ("Kivi", "kiwi"),          # the brief's own case
        ("Aaditya", "Aditya"),     # long-vowel romanisation
        ("Karthik", "Kartik"),     # aspirated consonant
        ("Sumeet", "Sumit"),
        ("Vishal", "Wishal"),      # v/w merger
        ("Redis", "red is"),       # one token heard as two
        ("Postgres", "post grease"),
        ("OpenAI", "open ai"),
        ("Anoop", "Anup"),
    ],
)
def test_kivi_code_unifies_forms_that_should_match(a, b):
    assert kivi_code(a) == kivi_code(b)


@pytest.mark.parametrize(
    "a,b",
    [
        ("Kivi", "kitty"),
        ("Kivi", "give"),
        ("Aaditya", "additive"),
        ("Aaditya", "Aditya to"),   # regression: see test_regressions
    ],
)
def test_kivi_code_separates_forms_that_must_not_match(a, b):
    assert kivi_code(a) != kivi_code(b)


def test_kivi_code_beats_both_baselines_on_the_indic_set():
    """The encoder has to earn its place over the obvious alternatives."""
    pairs = [
        ("Kivi", "kiwi"), ("Aaditya", "Aditya"), ("Karthik", "Kartik"),
        ("Sumeet", "Sumit"), ("Vishal", "Wishal"), ("Redis", "red is"),
        ("PyTorch", "pie torch"), ("Postgres", "post grease"), ("OpenAI", "open ai"),
        ("Kshatriya", "Kshatria"), ("Anoop", "Anup"), ("Bengaluru", "Bengalooru"),
    ]
    scores = {
        name: sum(1 for a, b in pairs if fn(a) == fn(b))
        for name, fn in (("soundex", soundex), ("metaphone", metaphone_compact), ("kivi", kivi_code))
    }
    assert scores["kivi"] > scores["soundex"]
    assert scores["kivi"] > scores["metaphone"]


def test_phonetic_similarity_is_graded_not_binary():
    assert phonetic_similarity(kivi_code("Kubernetes"), kivi_code("cuban eighties")) > 0.8
    assert phonetic_similarity("ABC", "ABC") == 1.0
    assert phonetic_similarity("", "ABC") == 0.0


def test_jaro_winkler_rewards_a_shared_opening():
    assert jaro_winkler("aaditya", "aditya") > jaro_winkler("aaditya", "xditya")


# ── the ordinary-word prior ────────────────────────────────────────────────────

@pytest.mark.parametrize("word", ["kiwi", "cursor", "slack", "linear", "arc", "apple", "notion"])
def test_collision_words_are_recognised_as_ordinary_english(word):
    assert is_ordinary_word(word)


@pytest.mark.parametrize("word", ["aditya", "kivi", "sarvam", "kubernetes", "kshatriya"])
def test_personal_vocabulary_is_not_ordinary_english(word):
    assert not is_ordinary_word(word)


def test_frequency_rank_separates_famous_nouns_from_private_ones():
    assert rank("friday") < 30_000        # globally common
    assert rank("google") < 30_000
    assert rank("sarvam") >= 30_000       # absent from the top 30k


def test_a_span_is_ordinary_only_if_every_token_is():
    assert span_ordinariness(["add", "it"])[0] is True
    assert span_ordinariness(["sarvam", "kiwi"])[0] is False


def test_span_ordinariness_reports_the_commonest_token():
    _, min_rank = span_ordinariness(["add", "it"])
    assert min_rank == min(rank("add"), rank("it"))


# ── context cues ───────────────────────────────────────────────────────────────

def test_quoted_and_cued_mentions_are_metalinguistic():
    text = "The word 'kiwi' has four letters."
    span = next(s for s in spans(text, 1) if s.text == "kiwi")
    assert is_metalinguistic(text, span)


def test_ordinary_use_is_not_metalinguistic():
    text = "Ship the Kiwi update on Friday."
    span = next(s for s in spans(text, 1) if s.text == "Kiwi")
    assert not is_metalinguistic(text, span)


def test_hypothetical_mentions_are_detected():
    text = "We might call the new service Kivali if legal agrees."
    span = next(s for s in spans(text, 1) if s.text == "Kivali")
    assert is_irrealis(text, span)


# ── the formatter stand-in ─────────────────────────────────────────────────────

def test_formatter_reproduces_the_briefs_stage_two():
    assert (
        format_stub("ask aditya to review the sarvam kiwi service")
        == "Ask Aditya to review the Sarvam Kiwi service."
    )


def test_formatter_does_no_personal_vocabulary_work():
    """Stage 2 must not fix personal words, or stage 3 would prove nothing."""
    out = format_stub("review the sarvam kiwi service")
    assert "Kivi" not in out
