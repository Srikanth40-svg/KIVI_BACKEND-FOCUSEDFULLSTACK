# Phases 2–5 — Product, memory, learning policy, retrieval, backend

## Phase 2 — Product position and the memory abstraction

### The product in one sentence

> **Phonetic memory is the set of words whose *written identity* belongs to this person** — learned
> from evidence produced by ordinary use, applied only when the surrounding context agrees, and
> silent the rest of the time.

Kivi already has a Dictionary that a person fills in by hand. This system is **the Dictionary that
fills itself, keeps its reasons, and knows when to keep quiet.**

### What it learns / what it refuses to learn

| Learns | Refuses |
|---|---|
| Words with a *personal written identity*: names, projects, products, internal acronyms, handles, and the user's settled choice between two valid spellings | Any word whose correct form is already determined by general English or by Kivi's Styles |
| Only on evidence of strength ≥ *suggestive*, and only **acts** on ≥ *corroborated* | Anything supported solely by an LLM's opinion (rule), or by a hypothetical mention |
| Spans of 1–4 tokens | Sentence-level punctuation, casing conventions, number/date formatting — **that is Styles' job (F4)** |

### Primary user value

The brief's own framing: one wrong word makes an otherwise excellent transcript feel impersonal.
So the value is not throughput of corrections — it is **the absence of the jarring word**, achieved
without ever corrupting a word the person actually said correctly. That asymmetry (a false
correction is worse than a missed one, because it damages *correct* text and erodes trust in
everything else on the page) drives every threshold in this system.

### The unit of memory: a typed span

Taxonomy classes A7/A8 ("Aaditya Labs", "sarvam kiwi") rule out a token dictionary. Classes
A4/A9 ("OpenAI", "@aaditya_k") rule out storing anything but the literal surface string.
So a memory is:

**a canonical surface span (1–4 tokens) + a type + the observed forms it has been mistaken for
+ the evidence that created it + a status.**

### Field-by-field justification (`word_memories`)

Only fields that a specific requirement forces are present. What each one buys:

| Field | Forced by | Why it exists |
|---|---|---|
| `canonical_form` | A4, A9 | The exact output string. Case, punctuation and joining are **data**, not derivable. |
| `normalized_key` | retrieval tier 1 | Case/punct/diacritic-folded key for indexed exact lookup. |
| `phonetic_key` | A1, A2, A6 | Indexed sound-alike lookup; the only way "cuban eighties" reaches "Kubernetes". |
| `token_count` | A7, A8 | Bounds the n-gram window at query time; without it retrieval can't know how wide to look. |
| `word_type` | N1–N4 | Gates context. A `person` memory and a `product` memory need different evidence to fire. |
| `status` | N9, N10, N11 | `candidate` / `confirmed` / `superseded` / `deleted`. Retrieval filters on it — deletion and weak evidence must actually take effect. |
| `confidence` | §8 | Numeric promotion state, separate from status so movement inside a status is visible. |
| `superseded_by` | §13 | Lets "actually it's Aditya" replace knowledge **without destroying history**. |
| `gloss` | adjudication | One short human/LLM-readable description ("colleague at Sarvam"). Optional; the only free-text field. |
| `occurrence_count`, `first_seen`, `last_seen` | E4 | Repetition evidence needs counts across *separate* interactions. |
| `created_at`, `updated_at`, `deleted_at` | R4 | Durability + soft delete. |

**Deliberately absent, with reasons:** no embedding vector (must earn its place by measurement —
see Phase 4); no IPA/pronunciation field (there is no source of truth for it and no measured need);
no per-memory prompt text (memories are data, prompts are code); no free-form JSON blob.

`memory_variants` is a separate table (not a JSON column) because variants are **looked up by
index** on every request and each carries its own count — that is a join key, not a payload.

## Phase 3 — Learning policy

### The evidence ladder

Every observation produces zero or more *candidate extractions*, each with a typed evidence
record. Weights (initial values; tuned on dev only, never on holdout):

| Evidence | Class | Weight / effect |
|---|---|---|
| `manual_entry` | E3 authoritative | confidence 1.00 → **confirmed** immediately |
| `user_spelling` — "actually, spell it Aaditya" | E1 authoritative | 0.95 → **confirmed** immediately |
| `user_edit` — observed diff of the user fixing Kivi's output | E2 authoritative | 0.90 → **confirmed** immediately |
| `repetition` — same form in N separate interactions | E4 corroborating | +0.18 each, capped 0.85 |
| `naming_frame` — "the company is called Aaditya Labs" | E6 suggestive | base 0.40 → **candidate** |
| `app_context` — repo/channel/window name agrees | E5 weak | +0.05, total contribution capped at 0.10; **can never cross the confirm line alone** |
| `irrealis` — "I *might* call it Aaditya" | E7 insufficient | **rejected, logged with reason** |
| `llm_only` — model proposed it, nothing corroborates | E8 insufficient | **rejected by rule** (§8) |

### Status machine

```
                     authoritative evidence (E1/E2/E3)
        ┌──────────────────────────────────────────────┐
        │                                              ▼
   (none) ──E6──▶ candidate ──confidence ≥ 0.70──▶ confirmed
                      │                              │   │
                      │                    contradicting authoritative
                      │                      evidence │   │ user delete
                      ▼                              ▼   ▼
                   rejected                    superseded  deleted
                 (logged, inert)             (inert, kept)  (inert, kept)
```

**Only `confirmed` memories may change text.** `candidate` memories are visible in the UI and
inert in the pipeline — that is class N11, and it is the whole answer to "what should the product
do when its evidence is weak."

### Why it was *not* learned is a first-class record

Every extraction attempt writes a row to `learning_decisions` with an outcome
(`confirmed` / `candidate` / `rejected`) and an enumerated reason. Without this, memory **recall**
is unmeasurable and rule 4 ("every learned word must have a reason") is unenforceable. It also
makes the §7 probes inspectable rather than asserted.

## Phase 4 — Retrieval architecture

Deliberately **no vector database, and no embeddings** in the default path. Justification, stated
up front and then measured: the query is "which stored span could this heard span *be*", which is
a surface/sound identity question, not a semantic-similarity question. Embeddings answer a
different question, cost a model call, and cannot distinguish `Kivi` from `kiwi` — they would
place them *closer* together. Phase 11 measures a similarity-only baseline to confirm this rather
than assert it.

### Four-tier cascade, cheapest first

| Tier | Method | Catches |
|---|---|---|
| 1 | exact `normalized_key` / `variant_normalized` (indexed) | already-known misspellings, A4 |
| 2 | `phonetic_key` equality (indexed) | A1, A2, A6, A12 |
| 3 | bounded fuzzy — Jaro-Winkler ≥ 0.72 within a phonetic/length block | novel ASR errors |
| 4 | *(optional)* LLM adjudication, **only** for spans left in the uncertain band | N12, hard context calls |

Query-side spans are all n-grams of length 1..max(`token_count`) present in memory, so the window
is bounded by what is actually stored.

### The context gate — separate from, and independent of, the similarity gate

This is the part that makes it a product rather than a fuzzy-replace. A candidate must pass
similarity **and** context. Context score combines:

1. **Ordinary-word prior (the N1–N3 defense).** Is the *heard* span a legitimate ordinary English
   word? Decided by the vendored lexicon: Webster's lowercase headwords ∩ top-60k frequency.
   `kiwi`, `cursor`, `slack`, `linear` → yes. `aditya`, `kivi`, `kubernetes`, `redis` → no.
   If yes, the required context score rises with the word's frequency: common words demand strong
   positive evidence before they may be overwritten.
2. **Learned co-occurrence profile.** Terms seen near the memory in its own evidence interactions
   ("service", "review", "deploy" for `Kivi`).
3. **Type-specific triggers.** `person` → "ask/tell/met/email/@"; `product` → "service/ship/deploy/repo/PR".
4. **Metalinguistic / quotation veto** (N7) and app-context bonus (E5).

Two memories within 0.08 of each other on final score ⇒ **abstain as ambiguous** (N12) rather
than silently pick.

### Application — two modes, both measured

- **`prompt` mode** honours the brief's explicit hint (F2): retrieved memories are placed into the
  formatting prompt and the LM produces the memory-aware output. Requires a model key.
- **`deterministic` mode** applies span replacements directly, preserving morphology (A10:
  `kiwis` → `Kivi's`, not `Kivi`). Requires nothing, always available (F6).

Both are exposed and both are evaluated, which turns the brief's hint into a measured comparison
instead of a guess.

## Phase 5 — Backend and data model

- **SQLite** via Python's stdlib `sqlite3`. Justified: single-user word memory has no concurrency
  story needing a server; the brief blesses embedded DBs; and it removes a native build and a
  running service from the reviewer's path. `WAL` + foreign keys on.
- **Real numbered SQL migrations** applied by a small migrator against a `schema_migrations`
  table. No ORM — the schema *is* the design here and should be readable as SQL.
- **Tables:** `interactions`, `word_memories`, `memory_variants`, `memory_evidence`,
  `memory_events`, `learning_decisions`, `decisions`, `decision_candidates`, `eval_runs`,
  `eval_results`. Each exists because a requirement above forces it.
- **One process** serves the JSON API and a no-build vanilla SPA, so the reviewer runs one command.
- **Reset** truncates in FK-safe order and re-runs seed from a committed JSONL — deterministic and
  documented (§36).

### Reason codes (enumerated, not free text)

So that the evaluation can aggregate *why*, not just *whether*:

`APPLIED_VARIANT_EXACT`, `APPLIED_PHONETIC_CONTEXT_OK`, `APPLIED_FUZZY_CONTEXT_OK`,
`NOOP_ALREADY_CANONICAL`, `ABSTAIN_ORDINARY_WORD_CONTEXT_WEAK`, `ABSTAIN_BELOW_SIMILARITY`,
`ABSTAIN_MEMORY_CANDIDATE_ONLY`, `ABSTAIN_MEMORY_DELETED`, `ABSTAIN_MEMORY_SUPERSEDED`,
`ABSTAIN_AMBIGUOUS_COMPETING`, `ABSTAIN_METALINGUISTIC`, `ABSTAIN_LLM_DECLINED`.
