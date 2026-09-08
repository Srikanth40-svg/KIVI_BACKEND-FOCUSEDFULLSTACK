"""Tokenisation, normalisation and morphology.

Normalisation rule for the whole system: **normalising never destroys information.**
The canonical surface form and every observed surface form are stored verbatim; the
folded strings produced here are only ever used as *lookup keys* and *comparison
inputs*. That is what keeps taxonomy A4 ("OpenAI", "GitHub") and A9 ("@aaditya_k")
representable at all.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# A word token: an optional @/# sigil, then letters/digits/apostrophes, optionally
# joined by internal hyphens or dots (so "kivi-backend", "sarvam.ai", "@aaditya_k"
# and "U.S." survive as single tokens rather than being shredded).
# A token may CONTAIN an apostrophe ("Kivi's") but must not begin with one: with "'"
# in the leading character class, the span for 'Cursor' swallowed the surrounding
# quotes, so is_quoted() never saw them and the metalinguistic veto never fired.
# An apostrophe counts only BETWEEN letters, so "Kivi's" is one token while the quotes
# around 'Cursor' are not part of it. A trailing apostrophe is therefore left in the text
# untouched, which is also right for a plural possessive: the span "Kivis" is rewritten
# and the following "'" simply stays where it was.
_WORD_BODY = r"[0-9A-Za-z_À-ɏ](?:[0-9A-Za-z_À-ɏ]|'(?=[0-9A-Za-z_À-ɏ]))*"
_TOKEN_RE = re.compile(rf"[@#]?{_WORD_BODY}(?:[-.]{_WORD_BODY})*")

_APOSTROPHES = "'’ʼ‘"
_QUOTE_CHARS = "\"'‘’“”"

# Cues that the span is being talked ABOUT rather than used (taxonomy N7).
_METALINGUISTIC_CUES = {
    "word", "words", "spelled", "spelt", "spelling", "spell", "letter", "letters",
    "pronounce", "pronounced", "pronunciation", "literally", "typo", "misspelled",
}

# Cues that a mention is hypothetical, so it asserts nothing about the world (evidence E7).
_IRREALIS_CUES = {
    "might", "maybe", "may", "could", "would", "perhaps", "possibly", "probably",
    "if", "suppose", "supposing", "considering", "thinking", "hypothetically",
    "imagine", "should", "someday", "eventually", "planning",
}


@dataclass(frozen=True)
class Token:
    text: str      # surface, verbatim
    start: int     # char offset into the source string
    end: int
    index: int     # position among word tokens


def tokenize(text: str) -> list[Token]:
    return [
        Token(text=m.group(0), start=m.start(), end=m.end(), index=i)
        for i, m in enumerate(_TOKEN_RE.finditer(text))
    ]


def fold_diacritics(s: str) -> str:
    """Aditya vs Ādityā: fold combining marks for the KEY only, never the stored form."""
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def normalize_key(s: str) -> str:
    """Case/diacritic/punctuation-folded lookup key. Multi-token spans keep single spaces.

    "Sarvam Kivi" -> "sarvam kivi";  "@aaditya_k" -> "aadityak";  "Kivi's" -> "kivis"
    """
    s = fold_diacritics(s).lower()
    s = re.sub(r"[^0-9a-z]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def normalize_compact(s: str) -> str:
    """Like normalize_key but with spaces removed too.

    Needed for taxonomy A4, where the only difference between the heard and canonical
    forms is where the space is: "open ai" -> "openai" == "OpenAI" -> "openai".
    """
    return normalize_key(s).replace(" ", "")


# --------------------------------------------------------------------------------------
# Morphology (taxonomy A10): apply the canonical stem, PRESERVE the inflection.
# "kiwis dashboard" must become "Kivi's dashboard", not "Kivi dashboard".
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Morphology:
    stem: str      # the token with its inflection removed
    suffix: str    # '' | 'possessive' | 'plural' | 'plural_possessive'


def morphology_candidates(token: str) -> list[Morphology]:
    """Every plausible (stem, inflection) reading of a token, uninflected reading first.

    Deliberately does NOT decide which reading is correct. An earlier version guessed a
    single answer with hand-written suffix rules and got "kiwis" and "OpenAIs" wrong,
    because both end in "is" and were caught by the guard protecting "analysis"/"basis".

    Guessing here is the wrong shape: only the matcher knows whether a stem corresponds
    to something in memory. So this enumerates readings and retrieval picks the one that
    actually matches, which cannot mis-fire — an inflection is only ever stripped when
    doing so reveals a real memory.
    """
    out = [Morphology(stem=token, suffix="")]
    low = token.lower()

    for apo in _APOSTROPHES:
        if low.endswith(apo + "s") and len(token) > 2:          # Kivi's
            out.append(Morphology(stem=token[:-2], suffix="possessive"))
        elif low.endswith("s" + apo) and len(token) > 2:        # the Kivis' logo
            out.append(Morphology(stem=token[:-2], suffix="plural_possessive"))

    if len(low) > 3 and low.endswith("es"):
        out.append(Morphology(stem=token[:-2], suffix="plural"))
    if len(low) > 2 and low.endswith("s") and not low.endswith("ss"):
        out.append(Morphology(stem=token[:-1], suffix="plural"))

    seen: set[tuple[str, str]] = set()
    unique: list[Morphology] = []
    for m in out:
        key = (m.stem, m.suffix)
        if m.stem and key not in seen:
            seen.add(key)
            unique.append(m)
    return unique


def apply_morphology(canonical: str, suffix: str) -> str:
    """Re-attach an inflection to a canonical form, using English orthography."""
    if suffix == "":
        return canonical
    if suffix == "possessive":
        return canonical + ("'" if canonical.lower().endswith("s") else "'s")
    plural = canonical + ("es" if canonical.lower().endswith(("s", "x", "z", "ch", "sh")) else "s")
    if suffix == "plural":
        return plural
    if suffix == "plural_possessive":
        return plural + "'"
    return canonical


def match_case(canonical: str, observed: str) -> str:
    """Respect SHOUTING, otherwise the canonical's own casing wins.

    The canonical form is authoritative about its own case ("OpenAI", "iPhone", "EPD"),
    so we do NOT re-case it to match the observed token. The single exception is an
    all-caps observed token in an all-caps stretch of text.
    """
    if observed.isupper() and len(observed) > 1 and not canonical.isupper():
        return canonical.upper()
    return canonical


# --------------------------------------------------------------------------------------
# Span construction and rewriting
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Span:
    text: str                # verbatim source slice
    start: int
    end: int
    token_start: int         # index into the token list
    token_count: int
    tokens: tuple[str, ...]


def spans(text: str, max_tokens: int = 4) -> list[Span]:
    """Every contiguous n-gram of word tokens, 1 <= n <= max_tokens.

    Bounded by what memory actually stores: callers pass the largest token_count present
    in the memory table, so the window never widens beyond something that could match.
    """
    toks = tokenize(text)
    out: list[Span] = []
    for n in range(1, max_tokens + 1):
        for i in range(0, len(toks) - n + 1):
            first, last = toks[i], toks[i + n - 1]
            out.append(
                Span(
                    text=text[first.start:last.end],
                    start=first.start,
                    end=last.end,
                    token_start=i,
                    token_count=n,
                    tokens=tuple(t.text for t in toks[i:i + n]),
                )
            )
    return out


def rewrite(text: str, edits: list[tuple[int, int, str]]) -> str:
    """Apply (start, end, replacement) edits to `text`. Non-overlapping, right-to-left.

    Everything outside the edited spans is preserved byte-for-byte: this system changes
    words, and must never quietly reflow the rest of the sentence.
    """
    for start, end, replacement in sorted(edits, key=lambda e: -e[0]):
        text = text[:start] + replacement + text[end:]
    return text


# --------------------------------------------------------------------------------------
# Context cues
# --------------------------------------------------------------------------------------

def is_quoted(text: str, start: int, end: int) -> bool:
    """Is the span wrapped in quotes? ("the word 'kiwi' has four letters")"""
    before = text[:start].rstrip()
    after = text[end:].lstrip()
    return bool(before) and before[-1] in _QUOTE_CHARS and bool(after) and after[0] in _QUOTE_CHARS


def is_metalinguistic(text: str, span: Span, window: int = 3) -> bool:
    """Is the span being discussed AS a word, rather than used? (taxonomy N7)"""
    if is_quoted(text, span.start, span.end):
        return True
    toks = tokenize(text)
    lo = max(0, span.token_start - window)
    preceding = {t.text.lower() for t in toks[lo:span.token_start]}
    return bool(preceding & _METALINGUISTIC_CUES)


def is_irrealis(text: str, span: Span, window: int = 6) -> bool:
    """Is the mention hypothetical? "I MIGHT call it Aaditya" (evidence class E7)."""
    toks = tokenize(text)
    lo = max(0, span.token_start - window)
    preceding = {t.text.lower() for t in toks[lo:span.token_start]}
    return bool(preceding & _IRREALIS_CUES)


def context_tokens(text: str, span: Span | None = None, window: int = 8) -> set[str]:
    """Lowercased word tokens around a span (or the whole text), for context scoring."""
    toks = tokenize(text)
    if span is None:
        return {t.text.lower() for t in toks}
    lo = max(0, span.token_start - window)
    hi = min(len(toks), span.token_start + span.token_count + window)
    return {
        t.text.lower()
        for t in toks[lo:hi]
        if not (span.token_start <= t.index < span.token_start + span.token_count)
    }
