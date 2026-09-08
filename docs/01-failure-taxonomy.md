# Phase 1 — The word-level problem

The brief gives one example and says it "establishes the three transcript levels, not the boundaries
of the problem." So the first job is to find the boundaries.

Method: I worked backwards from *why* a word can be wrong after good ASR and good formatting.
There are only three underlying reasons, and they generate every class below:

- **P1 — The word is not in the language model's world.** A private name, an internal project, a
  handle. ASR must emit *something*, so it emits the nearest thing it knows.
- **P2 — The word is in the world, but with the wrong identity.** The sound maps to a common
  word or a more frequent spelling, and the frequent reading wins. (`kiwi` beats `Kivi`;
  `Aditya` beats `Aaditya`.)
- **P3 — The word is in the world with more than one correct rendering, and only this person
  knows which one they mean.** `grey/gray`, `Bengaluru/Bangalore`, `Aditya/Aaditya`.

P3 is the one that justifies the whole product. A better ASR model or a bigger global dictionary
fixes some of P1 and P2. Nothing but personal memory fixes P3, because there is no correct
answer to look up — only *this user's* answer. **This is the claim the evaluation must test.**

---

## 1. Positive classes — memory should intervene

| # | Class | Underlying | ASR / formatted | Memory-aware | Note |
|---|---|---|---|---|---|
| A1 | Personal name heard as a common word | P2 | "ask **kiwi** to review" | "ask **Kivi** to review" | the brief's class |
| A2 | Personal name heard as its *frequent* romanisation | P3 | "**Aditya**" | "**Aaditya**" | Indian-English core case; both spellings valid |
| A3 | Product / project name heard as a common word | P2 | "the sarvam **kiwi** service" | "the Sarvam **Kivi** service" | the brief's class |
| A4 | Brand orthography: splitting / casing / joining | P2 | "**open ai**", "**git hub**", "**post gres**" | "**OpenAI**", "**GitHub**", "**Postgres**" | canonical form carries case *and* joining |
| A5 | Personal acronym | P1 | "send it to **e p d**" | "send it to **EPD**" | must distinguish personal from generic (see C3) |
| A6 | Technical jargon heard as ordinary words | P1/P2 | "**cuban eighties**", "**red is**", "**pie torch**" | "**Kubernetes**", "**Redis**", "**PyTorch**" | multi-token → single token |
| A7 | Multi-word entity | P1 | "**aditya labs** raised" | "**Aaditya Labs** raised" | span, not token |
| A8 | Multi-word entity where only one token is wrong | P2 | "**sarvam kiwi**" | "**Sarvam Kivi**" | needs partial-span matching |
| A9 | Handle / identifier / non-lexical string | P1 | "at **aditya** underscore k" | "**@aaditya_k**" | strict surface form, no natural-language rules |
| A10 | Morphological variant of a personal word | P2 | "**kiwis** dashboard" | "**Kivi's** dashboard" | apply canonical stem, **preserve** the inflection |
| A11 | Two valid spellings, user has a settled preference | **P3** | "the **grey** theme", "**Bangalore** office" | "the **gray** theme", "**Bengaluru** office" | **the class only personal memory can fix** |
| A12 | Transliterated / code-switched proper noun | P3 | "**kshatriya**", "**bengaluru**" | user's chosen romanisation | Sarvam-relevant; kept modest, not overclaimed |

## 2. Negative classes — memory must deliberately do nothing

The brief asks for these explicitly, and Kivi's own origin story ("one incorrect word could still
make an otherwise excellent transcript feel impersonal") means a *wrong* correction is worse than
a missed one: it corrupts text the user actually said correctly. Non-intervention is a feature.

| # | Class | Memory held | Input | Correct output | Why |
|---|---|---|---|---|---|
| N1 | Homophone used in its ordinary sense | `Kivi` (product) | "I ate a **kiwi**" | unchanged | context is fruit, not software |
| N2 | Personal word collides with a generic technical word | `Cursor` (the editor) | "move the **cursor** left" | unchanged | both readings real |
| N3 | Personal word collides with a common English word | `Slack`, `Linear`, `Arc`, `Notion` | "cut me some **slack**", "**linear** regression" | unchanged | high-frequency trap |
| N4 | A *different* real person with the standard spelling | `Aaditya` (colleague) | "**Aditya** Birla Group" | unchanged | the memory is about one person |
| N5 | Coincidental phonetic proximity | `Aaditya` | "**add it** to the list" | unchanged | naive fuzzy matching fires here |
| N6 | Sub-threshold similarity | `Kivi` | "the **kitty** is asleep", "**give** me a minute" | unchanged | threshold must be justified, not tuned to the demo |
| N7 | Metalinguistic / quoted use | `Kivi` | "the word '**kiwi**' has four letters" | unchanged | the word is the object, not a reference |
| N8 | Already correct | `Kivi` | "the **Kivi** service" | unchanged, **and logged as no-op** | must not churn text or inflate "corrections" |
| N9 | Memory deleted | `Kivi` (deleted) | "the **kiwi** service" | unchanged | deletion must actually take effect |
| N10 | Memory superseded | `Aaditya` → `Aditya` | "**Aaditya**" | "**Aditya**" (new canonical) | old form must stop winning |
| N11 | Candidate not yet confirmed | `Kivi` (candidate) | "the **kiwi** service" | unchanged | weak evidence must not act |
| N12 | Two memories compete | `Kivi`, `Kiwi Foods` (client) | "the **kiwi** deck" | abstain or pick with reason | ambiguity must be visible, not silently resolved |
| N13 | Out of scope: sentence-level formatting | — | "five pm" → "5 PM" | **not my job** | Styles owns this; excluded from my metrics |

## 3. Learning-evidence classes — when is it allowed to learn?

The brief: "decide ... which observations deserve to change its future behaviour, and what the
product should do when its evidence is weak or wrong." So evidence is typed and ranked, and the
rank determines whether a word can act.

| # | Evidence | Strength | Rationale |
|---|---|---|---|
| E1 | Explicit spelling instruction — "actually, spell it Aaditya", "A-A-D-I-T-Y-A" | **authoritative** | the user is telling us the answer |
| E2 | User edits Kivi's output — observed diff `kiwi → Kivi` | **authoritative** | strongest signal available from ordinary use |
| E3 | Manual Dictionary entry | **authoritative** | explicit intent |
| E4 | Repeated consistent occurrence across *separate* interactions | **corroborating** | needs a threshold + consistency, never a single count |
| E5 | Application context (repo name, channel `#kivi-eng`, window title) | **weak / corroborating only** | can never promote on its own |
| E6 | Single occurrence in a naming frame — "the company is called Aaditya Labs" | **suggestive** | a real assertion, but one shot |
| E7 | Single occurrence in a hypothetical/irrealis frame — "I **might** call it Aaditya" | **insufficient** | not a fact about the world yet |
| E8 | An LLM proposed it and nothing else supports it | **insufficient, by rule** | a model's suggestion is not evidence |

The four probes in the master prompt fall out of this cleanly and become test cases:
"I met someone named Aaditya" → E6, suggestive → **candidate**;
"I might call it Aaditya" → E7 → **learn nothing**;
"The company is called Aaditya Labs" → E6 on a multi-word span → **candidate**;
"Actually, spell it Aaditya" → E1 → **confirmed immediately**.

## 4. What this taxonomy forces the design to have

Each of these is a requirement derived above, not a feature chosen up front:

1. A11/P3 ⇒ memory is **per-user preference**, not a global correctness table.
2. A7/A8 ⇒ the unit of memory is a **span (1..n tokens)**, not a token.
3. A10 ⇒ matching must be **morphology-preserving**; normalisation must not destroy the observed form.
4. A4/A9 ⇒ the canonical form is a **literal surface string** (case, punctuation, joining are data).
5. N1–N3, N7, N12 ⇒ a **context gate** is mandatory, separate from the similarity gate.
6. N5/N6 ⇒ similarity thresholds must be **measured**, and phonetic vs. character similarity must be told apart.
7. N8 ⇒ no-ops must be **recorded as decisions**, or precision is unmeasurable.
8. N9/N10/N11 ⇒ **status** is part of retrieval, not a display field.
9. E1–E8 ⇒ **typed evidence with strength**, and a promotion policy that authoritative evidence can shortcut.
10. E8 ⇒ the LLM may **propose and adjudicate**, but may not **promote**.
11. R10/R11 ⇒ every decision, including abstentions, needs a **persisted, inspectable reason**.
