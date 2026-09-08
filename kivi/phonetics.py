"""Phonetic encoding and string similarity.

Three encoders live here on purpose. The brief's instruction — and plain engineering
sense — is that an algorithm must earn its place by measurement, so `eval/` compares:

  * `soundex`               — the 1918 baseline, 4 characters, very lossy
  * `metaphone_compact`     — a compact consonant-class encoder in the Metaphone family
  * `kivi_code`             — the same idea, extended for the romanisation variation that
                              dominates Indian-English dictation

`kivi_code` exists because of taxonomy A2/A12: Indian names have many equally valid
romanisations ("Aditya"/"Aaditya", "Kartik"/"Karthik", "Sumit"/"Sumeet"), and ASR emits
whichever is most frequent in its training data. The extra rules over Metaphone are:
long-vowel collapse (aa/ee/oo/ii), aspirated-consonant collapse (kh/gh/th/dh/ph/bh/ch
-> unaspirated class), v/w merger, and the ksh/jn/gn clusters. Whether that is actually
better than plain Metaphone here is a measured question, answered in eval/results/.

Nothing in this module is a reimplementation-by-reference of a published algorithm:
`soundex` follows the standard rules, `metaphone_compact` is a deliberately compact
member of that family written for baseline comparison rather than a faithful port of
Lawrence Philips' Double Metaphone.
"""

from __future__ import annotations

import re

from .text import fold_diacritics

_VOWELS = set("aeiou")


def _prepare(s: str) -> str:
    """Lowercase, fold diacritics, keep letters only."""
    return re.sub(r"[^a-z]", "", fold_diacritics(s).lower())


# --------------------------------------------------------------------------------------
# Baseline 1: Soundex
# --------------------------------------------------------------------------------------

_SOUNDEX_CLASS = {
    **{c: "1" for c in "bfpv"},
    **{c: "2" for c in "cgjkqsxz"},
    **{c: "3" for c in "dt"},
    "l": "4",
    **{c: "5" for c in "mn"},
    "r": "6",
}


def soundex(s: str) -> str:
    w = _prepare(s)
    if not w:
        return ""
    first = w[0].upper()
    digits: list[str] = []
    prev = _SOUNDEX_CLASS.get(w[0], "")
    for ch in w[1:]:
        code = _SOUNDEX_CLASS.get(ch, "")
        if code and code != prev:
            digits.append(code)
        if ch not in "hw":       # h and w do not break a repetition run
            prev = code
    return (first + "".join(digits) + "000")[:4]


# --------------------------------------------------------------------------------------
# Baseline 2: a compact Metaphone-family encoder
# --------------------------------------------------------------------------------------

def metaphone_compact(s: str) -> str:
    w = _prepare(s)
    if not w:
        return ""
    out: list[str] = []
    i, n = 0, len(w)
    while i < n:
        ch = w[i]
        nxt = w[i + 1] if i + 1 < n else ""
        if ch in _VOWELS:
            if i == 0:
                out.append("A")           # only a leading vowel is retained
            i += 1
            continue
        if ch == nxt:                     # collapse doubled consonants
            i += 1
            continue
        if ch == "c":
            out.append("S" if nxt in "eiy" else "K")
        elif ch == "g":
            out.append("J" if nxt in "eiy" else "K")
        elif ch == "p":
            if nxt == "h":
                out.append("F")
                i += 1
            else:
                out.append("P")
        elif ch == "s":
            out.append("X" if nxt == "h" else "S")
            if nxt == "h":
                i += 1
        elif ch == "t":
            out.append("0" if nxt == "h" else "T")
            if nxt == "h":
                i += 1
        elif ch == "q":
            out.append("K")
        elif ch == "x":
            out.append("KS")
        elif ch == "z":
            out.append("S")
        elif ch == "v":
            out.append("F")
        elif ch == "h":
            pass                          # silent outside the digraphs handled above
        elif ch == "w" or ch == "y":
            pass                          # glides drop
        else:
            out.append(ch.upper())
        i += 1
    return "".join(out)


# --------------------------------------------------------------------------------------
# kivi_code — the encoder this system uses by default
# --------------------------------------------------------------------------------------

# Order matters: longest clusters first, so "chh" is seen before "ch" and "ksh" before "sh".
_CLUSTERS: list[tuple[str, str]] = [
    ("chh", "C"), ("ksh", "KS"), ("shh", "S"),
    ("kh", "K"), ("ch", "C"), ("th", "T"), ("dh", "D"),
    ("ph", "F"), ("bh", "B"), ("sh", "S"), ("zh", "S"), ("jh", "J"),
    ("ck", "K"), ("qu", "KV"), ("wr", "R"), ("kn", "N"), ("gn", "N"), ("jn", "N"),
    ("ng", "N"), ("nk", "NK"), ("tz", "S"), ("ts", "S"), ("ps", "S"),
]

# Single-consonant classes. Merges only where transcriptions genuinely alternate:
#   v/w   — "Kivi"/"Kiwi", "Vishal"/"Wishal"
#   c/k/q — hard c
#   s/z/x — sibilants
#   f/p+h — already handled by the cluster table
_SINGLES = {
    "v": "V", "w": "V",
    "c": "K", "k": "K", "q": "K",
    "s": "S", "z": "S", "x": "KS",
    "j": "J", "g": "G",
    "b": "B", "p": "P",
    "d": "D", "t": "T",
    "f": "F",
    "l": "L", "r": "R",
    "m": "M", "n": "N",
    "h": "", "y": "",
}


def kivi_code(s: str) -> str:
    """Phonetic code tuned for the romanisation variation in Indian-English dictation.

    Multi-token spans are encoded as a single run, which is what lets a two-word ASR
    error collapse onto a one-word memory ("cuban eighties" -> "Kubernetes").
    """
    w = _prepare(s)
    if not w:
        return ""

    # 1. Long vowels carry no information across romanisations: Aditya == Aaditya,
    #    Sumit == Sumeet, Anup == Anoop.
    w = re.sub(r"aa+", "a", w)
    w = re.sub(r"ee+", "i", w)
    w = re.sub(r"oo+", "u", w)
    w = re.sub(r"ii+", "i", w)
    w = re.sub(r"(.)\1+", r"\1", w)   # any other doubled letter collapses

    lead_vowel = "A" if w[0] in _VOWELS else ""

    out: list[str] = []
    i, n = 0, len(w)
    while i < n:
        # 'gh' is context-dependent in English and must be handled before the cluster
        # table: silent after a vowel ("eighties", "night", "though"), hard otherwise
        # ("Ghosh", "ghar"). Getting this wrong left a phantom G in "eighties" and broke
        # the "cuban eighties" -> "Kubernetes" collapse.
        if w.startswith("gh", i):
            if i > 0 and w[i - 1] in _VOWELS:
                pass                    # silent
            else:
                out.append("G")
            i += 2
            continue
        for cluster, code in _CLUSTERS:
            if w.startswith(cluster, i):
                out.append(code)
                i += len(cluster)
                break
        else:
            ch = w[i]
            if ch in _VOWELS:
                pass                    # interior vowels drop entirely
            else:
                out.append(_SINGLES.get(ch, ch.upper()))
            i += 1

    # NO final run-collapse on the finished code. Doubled *letters* are already collapsed
    # on the input above, so any repeated symbol left here comes from two genuinely
    # distinct consonants separated by dropped vowels. Collapsing those merged "Aditya to"
    # (ADTT) into "Aaditya" (ADT) and deleted the word "to" from the output.
    return lead_vowel + "".join(out)


ENCODERS = {
    "soundex": soundex,
    "metaphone_compact": metaphone_compact,
    "kivi_code": kivi_code,
}

DEFAULT_ENCODER = "kivi_code"


def encode(s: str, encoder: str = DEFAULT_ENCODER) -> str:
    return ENCODERS[encoder](s)


# --------------------------------------------------------------------------------------
# String similarity
# --------------------------------------------------------------------------------------

def jaro(a: str, b: str) -> float:
    if a == b:
        return 1.0
    la, lb = len(a), len(b)
    if la == 0 or lb == 0:
        return 0.0
    window = max(la, lb) // 2 - 1
    if window < 0:
        window = 0
    a_hit = [False] * la
    b_hit = [False] * lb
    matches = 0
    for i, ca in enumerate(a):
        lo = max(0, i - window)
        hi = min(i + window + 1, lb)
        for j in range(lo, hi):
            if not b_hit[j] and b[j] == ca:
                a_hit[i] = b_hit[j] = True
                matches += 1
                break
    if matches == 0:
        return 0.0
    transpositions = 0
    k = 0
    for i in range(la):
        if not a_hit[i]:
            continue
        while not b_hit[k]:
            k += 1
        if a[i] != b[k]:
            transpositions += 1
        k += 1
    t = transpositions / 2
    return (matches / la + matches / lb + (matches - t) / matches) / 3.0


def jaro_winkler(a: str, b: str, *, prefix_weight: float = 0.1) -> float:
    """Jaro with a shared-prefix bonus.

    Chosen over plain Levenshtein for the lexical tier because ASR errors on names
    overwhelmingly preserve the word opening ("Aditya"/"Aaditya", "Kivi"/"Kiwi"), and
    Jaro-Winkler rewards exactly that while staying length-normalised.
    """
    j = jaro(a, b)
    prefix = 0
    for ca, cb in zip(a, b):
        if ca != cb:
            break
        prefix += 1
        if prefix == 4:
            break
    return j + prefix * prefix_weight * (1 - j)


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def phonetic_similarity(a_code: str, b_code: str) -> float:
    """1.0 for identical codes, otherwise length-normalised edit similarity of the codes.

    Similarity rather than equality matters for multi-token ASR errors, where the code
    is close but not identical ("cuban eighties" -> KBNTS vs "Kubernetes" -> KBRNTS).
    """
    if not a_code or not b_code:
        return 0.0
    if a_code == b_code:
        return 1.0
    dist = levenshtein(a_code, b_code)
    return max(0.0, 1.0 - dist / max(len(a_code), len(b_code)))
