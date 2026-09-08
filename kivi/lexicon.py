"""The ordinary-English-word prior — this system's main defence against false corrections.

The question a correction engine must answer before overwriting a word is not "does this
sound like something I know" but:

    **does this token already have a legitimate reading in ordinary English?**

If it does, overwriting it can destroy text the person said correctly, which is the worst
failure this product has (taxonomy N1-N3: "I ate a kiwi", "move the cursor", "cut me some
slack", "linear regression"). If it does not, the risk of intervening is low.

Two vendored artefacts answer it, and neither is a hand-written blocklist:

  * `en_ordinary_words.txt` — lowercase headwords of Webster's Second International
    (public domain) intersected with the 60k most frequent web tokens. An all-lowercase
    dictionary headword is a common noun/verb/adjective, never a proper noun, which is
    precisely the distinction needed.
  * `en_freq_top30k.tsv` — frequency ranks, so the bar can scale with how common the word
    is. Overwriting "it" (rank 16) must be far harder than overwriting "kiwi" (rank 16,870).

Measured separation on the words that matter:
    kiwi 16,870 / cursor 9,912 / slack 17,781 / linear 3,317 / arc 5,327  -> ordinary
    aditya 59,648 / kivi 223,283 / sarvam absent / kubernetes absent      -> not ordinary
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .text import normalize_key

LEXICON_DIR = Path(__file__).resolve().parent.parent / "data" / "lexicon"
ORDINARY_PATH = LEXICON_DIR / "en_ordinary_words.txt"
FREQ_PATH = LEXICON_DIR / "en_freq_top30k.tsv"

# Rank assigned to a token that is absent from the frequency list: effectively "never seen".
ABSENT_RANK = 10**9


class LexiconMissing(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _ordinary_words() -> frozenset[str]:
    if not ORDINARY_PATH.exists():
        raise LexiconMissing(
            f"Missing vendored lexicon {ORDINARY_PATH}. It is committed to the repository; "
            "if it is absent the checkout is incomplete."
        )
    words = {
        line.strip()
        for line in ORDINARY_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    return frozenset(words)


@lru_cache(maxsize=1)
def _ranks() -> dict[str, int]:
    if not FREQ_PATH.exists():
        raise LexiconMissing(
            f"Missing vendored lexicon {FREQ_PATH}. It is committed to the repository; "
            "if it is absent the checkout is incomplete."
        )
    ranks: dict[str, int] = {}
    for line in FREQ_PATH.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        try:
            ranks[parts[1]] = int(parts[0])
        except ValueError:
            continue
    return ranks


def rank(word: str) -> int:
    """Frequency rank (1 = most common). ABSENT_RANK if unlisted."""
    return _ranks().get(normalize_key(word).replace(" ", ""), ABSENT_RANK)


def is_ordinary_word(word: str) -> bool:
    """Does this single token have a legitimate ordinary-English reading?"""
    return normalize_key(word).replace(" ", "") in _ordinary_words()


def span_ordinariness(tokens: list[str] | tuple[str, ...]) -> tuple[bool, int]:
    """Ordinariness of a whole span.

    A span counts as ordinary only when **every** token in it is an ordinary word: that is
    what makes "add it" (both ordinary, min rank 16) a protected phrase while "sarvam kiwi"
    (only "kiwi" is ordinary) stays open to correction. Returns (is_ordinary, min_rank),
    where the minimum rank is the commonest token in the span and therefore the strongest
    reason for caution.
    """
    if not tokens:
        return False, ABSENT_RANK
    if not all(is_ordinary_word(t) for t in tokens):
        return False, min((rank(t) for t in tokens), default=ABSENT_RANK)
    return True, min(rank(t) for t in tokens)


def stats() -> dict[str, int]:
    return {"ordinary_words": len(_ordinary_words()), "ranked_words": len(_ranks())}
