"""A stand-in for Kivi's formatting language model (transcript stage 2).

**This is explicitly not Kivi's formatter.** The brief states that Kivi's implementation
will not be provided, and that the formatted transcript is an *input* to the problem being
solved here — the demo and the evaluation both accept a formatted string directly. This
module exists only so the demo can start from raw ASR text when no formatted version is
supplied, and so the three stages are always visible.

It does sentence casing, terminal punctuation and proper-noun casing. It deliberately does
**no** personal-vocabulary work: if it did, the boundary between stage 2 and stage 3 would
blur and the demo would prove nothing.

Known limitation, stated rather than hidden: casing an unfamiliar proper noun correctly is
genuinely a language-model job. The heuristic here capitalises tokens absent from ordinary
English, plus ordinary tokens that continue a proper-noun compound. That gets
"ask aditya to review the sarvam kiwi service" to "Ask Aditya to review the Sarvam Kiwi
service.", matching the brief's example, but it will not match a real LM everywhere.
"""

from __future__ import annotations

import re

from .lexicon import is_ordinary_word
from .text import rewrite, tokenize

# Words that are absent from the ordinary-English list but must never be capitalised.
_NEVER_CAPS = {
    "ok", "okay", "pm", "am", "etc", "vs", "http", "https", "www", "dont", "cant",
    "wont", "im", "ive", "id", "ill", "thats", "whats", "lets", "its", "theres",
}

_TERMINAL = {".", "!", "?", ":", ";"}


def format_stub(asr_text: str) -> str:
    """Approximate stage 2 deterministically. No personal vocabulary involved."""
    text = re.sub(r"\s+", " ", asr_text or "").strip()
    if not text:
        return ""

    toks = tokenize(text)
    edits: list[tuple[int, int, str]] = []
    # Tracks whether the PREVIOUS token was itself absent from ordinary English, not
    # merely whether it ended up capitalised. Using the latter let the compound rule
    # chain indefinitely, so "sarvam kiwi service" became "Sarvam Kiwi Service".
    prev_was_nondictionary = False

    for idx, tok in enumerate(toks):
        word = tok.text
        low = word.lower()
        new = word
        nondictionary = low.isalpha() and len(low) > 2 and not is_ordinary_word(low)

        if low == "i" or low.startswith("i'"):
            new = "I" + word[1:]
        elif idx == 0:
            new = word[:1].upper() + word[1:]
        elif low in _NEVER_CAPS:
            new = word
        elif nondictionary:
            new = word[:1].upper() + word[1:]
        elif prev_was_nondictionary and low.isalpha() and len(low) > 2:
            # One token of proper-noun compounding: "Sarvam kiwi" -> "Sarvam Kiwi",
            # while the following ordinary word stays lowercase.
            new = word[:1].upper() + word[1:]

        prev_was_nondictionary = nondictionary and idx > 0
        if new != word:
            edits.append((tok.start, tok.end, new))

    out = rewrite(text, edits)
    if out and out[-1] not in _TERMINAL:
        out += "."
    return out


FORMATTING_SYSTEM_PROMPT = (
    "You convert raw speech-recognition output into clean written text. "
    "Fix punctuation, capitalisation and sentence structure. Remove filler words and "
    "false starts. Do not add information, do not answer the content, and do not change "
    "any proper noun's spelling. Return only the corrected text."
)


def formatting_messages(asr_text: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": FORMATTING_SYSTEM_PROMPT},
        {"role": "user", "content": asr_text},
    ]


MEMORY_AWARE_SYSTEM_PROMPT = (
    "You are producing the final text of a dictation for one specific person. "
    "You are given the formatted transcript and a short list of that person's personal "
    "vocabulary, already retrieved and verified by a memory system.\n\n"
    "Apply the listed substitutions where the transcript refers to those things, "
    "preserving grammar, possessives and plurals. Change nothing else: no rewording, no "
    "punctuation changes, no new information. If a listed word appears in the transcript "
    "in an ordinary everyday sense rather than as the personal term, leave it alone.\n\n"
    "Return only the final text."
)


def memory_aware_messages(formatted_text: str, memory_block: str) -> list[dict[str, str]]:
    """The brief's "placed into the formatting prompt" path (docs/00 finding F2)."""
    return [
        {"role": "system", "content": MEMORY_AWARE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Personal vocabulary relevant to this transcript:\n{memory_block}\n\n"
                f"Formatted transcript:\n{formatted_text}"
            ),
        },
    ]
