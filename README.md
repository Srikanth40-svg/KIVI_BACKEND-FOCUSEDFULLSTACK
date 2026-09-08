# The Words Kivi Keeps

A word-level memory system for Kivi: it learns the words that belong to one person, applies

them when the sentence really refers to them, and stays quiet the rest of the time.

**To run it**

**[RUN.md](RUN.md)** for the precise reference version. Primary review method is local;

no credentials are needed.

```

ASR output      ask aditya to review the sarvam kiwi service

Formatted       Ask Aditya to review the Sarvam Kiwi service.

Memory-aware    Ask Aaditya to review the Sarvam Kivi service.

```

That output comes from database state earned by evidence, not from a rule about this

sentence. With an empty database the same input passes through untouched — the guided

journey in the interface demonstrates exactly that, in order, as step 1 and step 2.

---

## Headline results

Measured by `python -m kivi eval --split both`; the committed numbers are that command's

own output. Full report: [`eval/results/report.md`](eval/results/report.md).

| | **Kivi** (dev) | `exact` baseline | `fuzzy` baseline | **Kivi** (holdout) |

|---|---|---|---|---|

| correction precision | **1.000** | 0.636 | 0.157 | **1.000** |

| correction recall | **0.965** | 0.737 | 0.281 | **0.889** |

| **false interventions** | **0** | **24** | **46** | **0** |

| missed interventions | 2 | 15 | 1 | 2 |

| correct silences | 61 | 37 | 15 | 15 |

| exact text accuracy | **0.983** | 0.670 | 0.263 | **0.939** |

| memory precision / recall | 1.00 / 1.00 | — | — | 1.00 / 1.00 |

- **The context gate is what the system is.** Matching alone (`fuzzy`) gets 75.4% of its

  no-change cases wrong. A dictionary replace (`exact`) gets 39.3% wrong. Gating brings

  that to **zero while also raising recall** — 0.965 against 0.737.

- **The holdout is a different person's vocabulary**, learned from its own observations,

  sharing no words, wrong forms or contexts with the seed or the dev split. Precision and

  false-intervention rate hold exactly; recall drops 7.6 points, for one identified reason.

- **Latency**: retrieval mean **0.99 ms**, p95 1.43 ms; end-to-end mean 1.07 ms (n=118).

- **Model usage and cost**: **zero.** The default configuration makes no model calls.

- **Storage**: **172 KB** for 19 memories *including* all 37 evidence rows, 77 audit

  events, 41 learning decisions and 26 source interactions — about 9 KB per remembered

  word, with its complete provenance.

## The problem, as I understood it

The brief gives one example and says it "establishes the three transcript levels, not the

boundaries of the problem". So I started by asking why a word can still be wrong *after*

good ASR and good formatting. There are only three reasons:

- **P1** The word isn't in the model's world — a private name, an internal project, a

  handle. ASR must emit something, so it emits the nearest thing it knows.

- **P2** The word is in the world with the **wrong identity** — the sound maps to a

  commoner word or a more frequent spelling, and frequency wins. `kiwi` beats `Kivi`.

- **P3** The word has **more than one correct rendering**, and only this person knows

  which. `grey`/`gray`, `Bengaluru`/`Bangalore`, `Aditya`/`Aaditya`.

**P3 is what justifies the product.** A better ASR model or a bigger global dictionary

eventually absorbs much of P1 and P2. Nothing but personal memory fixes P3, because there

is no correct answer to look up — only *this user's* answer. That is the claim, so that is

what the evaluation is built to test.

From there I built a taxonomy of **12 positive classes**, **13 negative classes** and

**8 evidence types** ([docs/01-failure-taxonomy.md](docs/01-failure-taxonomy.md)). It is

worth reading before the code: every design decision below is derived from a row in it.

A sample of what the system distinguishes, all verified in the test suite:

| Input | Output | Why |

|---|---|---|

| "Ship the **Kiwi** update on Friday." | "Ship the **Kivi** update…" | product context; `kiwi` is a learned wrong form |

| "I ate a **kiwi** on the flight." | *unchanged* | ordinary English word, lower case, no supporting context |

| "Move the **cursor** to the end." | *unchanged* | `Cursor` is a known product, but this is the caret |

| "**Aditya Ghosh** approved the budget." | *unchanged* | a *different* colleague; the wider name protects the token |

| "The **Cuban Eighties** cluster is down." | "The **Kubernetes** cluster…" | a two-token mis-hearing collapsing onto one term |

| "**Kiwi's** onboarding flow is confusing." | "**Kivi's** onboarding…" | canonical stem applied, possessive preserved |

| "The word **'kiwi'** has four letters." | *unchanged* | the word is the object of the sentence |

| "We need to **post grease** warnings near the fryer." | *unchanged* | `Post Grease` is a learned wrong form of `Postgres`, but nothing here supports it |

| "Use the **grey** background." | "Use the **gray** background." | a settled personal spelling preference (P3) |

### Where it deliberately does nothing

Non-intervention is a feature, not a gap. The brief's own origin story is that *one*

incorrect word makes an otherwise excellent transcript feel impersonal — and a false

correction is strictly worse than a missed one, because it damages text the person said

correctly and undermines trust in everything else on the page. That asymmetry sets every

threshold in the system. Concretely, it stays silent when:

the heard word has a legitimate ordinary-English reading and nothing supports the personal

one · the memory is only a *candidate* · the memory was deleted or superseded · two

memories are equally good answers · the word is being quoted or discussed · the text is

already correct · nothing similar enough exists.

Each of those is a distinct, enumerated reason code, recorded per decision.

## Architecture

```

                       ┌─────────────────────────────────────────┐

  observation ────────▶│ LEARNING                                │

  (asr / formatted /   │  4 extractors → typed evidence (E1–E8)  │

   the person's edit / │  → confidence policy → status           │

   window title)       │  every refusal logged with its reason   │

                       └───────────────┬─────────────────────────┘

                                       ▼

                       ┌─────────────────────────────────────────┐

                       │ SQLite: word_memories, memory_variants, │

                       │ memory_evidence, memory_events,         │

                       │ learning_decisions, interactions        │

                       └───────────────┬─────────────────────────┘

                                       ▼

 formatted text ──────▶┌─────────────────────────────────────────┐

                       │ RETRIEVAL   4 tiers, cheapest first     │

                       │   exact → variant → phonetic → fuzzy    │

                       └───────────────┬─────────────────────────┘

                                       ▼

                       ┌─────────────────────────────────────────┐

                       │ CONTEXT GATE                            │

                       │   the bar: how much is at stake, and    │

                       │            how certain the identity is  │

                       │   the evidence: learned co-occurrence,  │

                       │            type cues, app context, case │

                       │   [optional] LLM adjudicates only the   │

                       │              genuinely uncertain band   │

                       └───────────────┬─────────────────────────┘

                                       ▼

                     memory-aware text + a persisted decision trace

                     (every span, every score, every reason —

                      including the ones it declined to act on)

```

One Python process serves the API and the interface. Roughly 3,500 lines of Python, five

runtime dependencies, no build step.

## The memory model

A memory is **a canonical surface span (1–4 tokens), typed, plus the forms it has been

mistaken for, plus the evidence that created it, plus a status.**

Spans rather than tokens because "Aaditya Labs" and "sarvam kiwi" cannot be expressed

otherwise. The canonical form is a literal surface string because case, punctuation and

joining are *data*, not derivable: no rule produces `OpenAI` or `@aaditya_k`.

Every column exists because a taxonomy row forces it — the justification is inline in

[`kivi/migrations/001_init.sql`](kivi/migrations/001_init.sql), which is worth reading as

the design document it is. Deliberately **absent**: any embedding vector (must earn its

place by measurement — see below), any pronunciation field (no source of truth, no measured

need), and any free-form JSON blob. Only two columns in the schema hold JSON, and both are

variable-shaped display payloads that are never queried by key.

`memory_variants` is a separate table rather than a JSON column because variants are looked

up **by index** on every request and each carries its own count: a join key, not a payload.

Its `kind` column carries the distinction that makes the whole gate work:

- `orthographic` — same referent, different spelling (`grey`/`gray`). Substitution is

  meaning-preserving, so it needs no situational support.

- `asr_error` — the machine mis-heard; the variant denotes something *else*

  (`kiwi` vs `Kivi`). Substitution changes meaning, so it must earn context.

## The learning policy

The hard part is not storing words. It is **refusing to store most of them.** Every

proposal must arrive attached to a typed piece of evidence:

| Evidence | Class | Effect |

|---|---|---|

| manual entry | authoritative | confidence 1.00 → confirmed immediately |

| spoken spelling — "actually, spell it Aaditya" | authoritative | 0.95 → confirmed |

| the person edits our output | authoritative | 0.90 → confirmed |

| repetition across *separate* interactions | corroborating | +0.18 each, capped at 0.85 |

| a naming frame — "the company is called…" | suggestive | 0.40 → **candidate only** |

| application context (window title, channel) | weak | +0.05, capped at 0.10 total |

| a hypothetical — "I *might* call it Aaditya" | insufficient | **refused, with the reason logged** |

| an LLM proposed it and nothing corroborates | insufficient | **refused by rule** |

Two rules do most of the work:

**Only `confirmed` memories may change text.** A candidate is visible in the interface and

inert in the pipeline. That is the answer to "what should the product do when its evidence

is weak".

**An LLM may adjudicate, but may never promote.** A model's suggestion is evidence class

E8, which the policy rejects outright. Nothing becomes durable because a language model

thought so.

Repetition is allowed to create memories at all only because of an asymmetry worth naming:

- **curative** memories come from a correction. Something was wrong, we were told, we fix it.

- **prophylactic** memories come from repetition of a word ASR *already gets right*

  (`Sarvam`, `Kshatriya`, `EPD`). Nothing is broken yet. Storing them makes the casing

  canonical and gives the word a phonetic key, so the *next* mis-hearing is catchable —

  and because the observed form was already correct, learning it can never itself introduce

  an error.

Whether a repeated word could plausibly be private vocabulary is decided by **measured

frequency**, not a hand-written blocklist: `friday` ranks 939 in general web English,

`january` 194, `google` 949, `john` 372 — all excluded. `aditya`, `sarvam`, `kivi`,

`kubernetes`, `epd` are absent from the top 30,000 entirely.

Every extraction attempt — including every refusal — writes a `learning_decisions` row.

Without it, "why was this not learned" is unanswerable and memory recall is unmeasurable.

## Retrieval

**No vector database and no embeddings**, and the reason is not budget. The question is

"which stored span could this heard span *be*" — an identity question about surface and

sound. Embeddings answer semantic relatedness, and on this exact problem they answer it

*backwards*: `Kivi` and `kiwi` are semantically unrelated (a product and a fruit) yet they

are the pair that must be linked, while `kiwi` and `mango` are close and must never be.

Four tiers, cheapest first. Tiers 1–3 are indexed SQL `IN` queries built from every span at

once, so the cost is a constant number of round-trips regardless of sentence length. Tier 4

needs a scan, bounded by a cheap blocking filter and by one person's vocabulary being

small — measured at **0.99 ms mean, 1.43 ms p95**, so it has not needed anything cleverer.

The phonetic encoder is tuned for the romanisation variation that dominates Indian-English

dictation: long-vowel collapse (`aa`/`ee`/`oo`), aspirated-consonant collapse

(`kh`/`gh`/`th`/`dh`/`ph`/`bh`), the v/w merger, and the `ksh`/`jn`/`gn` clusters. That it

is *better* than the obvious alternatives is measured, not assumed — on a 12-pair set of

real romanisation variants, exact-code agreement is **kivi_code 11, Soundex 9,

Metaphone 8**, and `kivi_code` uniquely both catches `Kivi`/`kiwi` and `Vishal`/`Wishal`

and correctly *rejects* `Kivi`/`coffee`, which Metaphone falsely matches. The comparison is

a test (`test_kivi_code_beats_both_baselines_on_the_indic_set`), so it cannot rot.

### The context gate

Similarity says a stored word *could* be the heard word. Context decides whether it *is*.

These are separate questions and the system keeps them separate — collapsing them is what

turns a memory system into a find-and-replace that mangles "I ate a kiwi".

The **bar** a substitution must clear depends on two things: how much damage a wrong

substitution would do, and how uncertain the identification is.

- An exactly-matched, meaning-preserving spelling variant → **0.0**. It cannot change what

  the sentence means.

- An exact match on a form the person themselves corrected, where the heard text is either

  not ordinary English or is capitalised mid-sentence → **0.0**. Identity is not in doubt,

  and the formatting stage already judged it a proper noun.

- An exact match where the heard form is an **ordinary English word in lower case** →

  **0.55**, or **0.75** if it is very common. This is the genuinely dangerous case:

  "I ate a kiwi", "move the cursor".

- A **cold** phonetic or fuzzy match → **0.45** minimum, rising to 0.55/0.75 on ordinary

  words. Here identity itself is a guess, and without this an unseen name was rewritten

  into a known one purely on spelling similarity — which is how a memory system starts

  renaming people.

The **evidence** side combines a co-occurrence profile the memory learned from its own

source interactions, cues appropriate to what kind of thing it is, the window title, and

whether the formatter capitalised the token mid-sentence. High-frequency words are excluded

from the learned profile by measured rank, because "the" appearing near a memory is not

evidence of anything.

Two memories within 0.08 of each other on one span ⇒ **abstain as ambiguous** and say so,

rather than picking the marginally higher score. But competing memories are not

*automatically* ambiguous: when the context genuinely resolves it, it resolves it.

## Technical decisions, and what was deliberately avoided

| Decision | Why |

|---|---|

| **SQLite** via the standard library | One person's word memory has no concurrency story needing a server. Removes a native build and a running service from the reviewer's path. WAL + per-thread connections + `busy_timeout`. |

| **Hand-written SQL migrations** | The schema *is* the design here and should be readable as SQL. The migrator is 30 lines; a migration framework would not have earned its place. |

| **No ORM** | Ten tables, all queried deliberately. |

| **No embeddings, no vector store** | Wrong tool for an identity question; measured against a similarity-only baseline instead of dismissed. |

| **No build step, vanilla SPA** | Every removed moving part is one fewer way a clean checkout fails. |

| **Deterministic by default** | The brief says the reviewing agent *may* provide credentials — "may". A system that stops working without one may not get reviewed. |

| **Vendored lexicons** | `/usr/share/dict/words` is macOS-only; depending on it would be a reproducibility trap. Both files are committed with their provenance. |

| Not built: microservices, queues, Docker, an agent framework, a dedicated vector DB, multi-tenancy, ASR | None would have improved a single measured number. |

### Where the LLM is used, and where it is not

Documented per call site in [`kivi/adjudicator.py`](kivi/adjudicator.py): purpose, input,

output, failure mode, budget, and fallback. In short — the optional adjudicator is consulted

**only** for spans whose context score sits inside an uncertain band around the bar, at most

one call per request, with strict JSON output and a seed. Any failure keeps the

deterministic verdict, so a failed model call can never turn an abstention into a

correction. Formatting has a deterministic stand-in

([`kivi/formatter.py`](kivi/formatter.py)) that does **no** personal-vocabulary work, because

if stage 2 fixed personal words the demo would prove nothing.

Sarvam is used selectively for uncertain cases, while deterministic rules remain responsible
for the final memory application. The LLM is an adjudication layer, not a free-form rewriting
engine and not a source of durable memory. A live check with KIVI_USE_LLM_ADJUDICATOR=1
confirmed one Sarvam call on an uncertain request while the final decision remained
mode=deterministic; that check recorded 210 input tokens, 80 output tokens, about 1.65 seconds
of latency, and ₹0.012005 cost.

## Evaluation methodology

Details in [docs/03-evaluation-spec.md](docs/03-evaluation-spec.md). The parts that matter:

**Gold labels are independent, structurally.** They are authored by hand in

[`eval/build_dataset.py`](eval/build_dataset.py), which **does not import or run the

system** — no `import kivi`, no database access. The runner only ever reads them, and it

refuses to start if a case is missing its expected result. One dataset consistency check

runs at load time: a case labelled "no intervention" whose expected text differs from its

input is rejected as a contradiction.

**Cases are grouped into scenarios, and every scenario is rebuilt from scratch** — reset,

replay the committed seed, replay the scenario's own setup. A case's result therefore cannot

depend on which cases ran before it.

**The 2×2 is the central table**, because the brief asks for useful interventions to be

reported separately from unnecessary ones:

|  | should change | should not change |

|---|---|---|

| **changed** | correct intervention | **false intervention** |

| **left alone** | missed intervention | correct silence |

A changed text counts as correct only if it equals the gold text *exactly* — changing the

right word to the wrong thing is a false intervention, not partial credit. Correct silences

are counted, not discarded: they are the denominator that makes false-intervention rate

mean anything, and they are most of real dictation.

**Three case kinds**, because the product makes three different claims: `apply` (the output

text and the intervention flag), `learn` (a word must end up in a specific status, or must

not exist), `state` (supersession links, deletion effects, counts).

**Composition** (exact, from `summary.json`): dev **142 cases** — 118 apply (57 should

change, 61 should not), 19 learn, 5 state, across 38 categories and 6 scenarios. Holdout

**40 cases** — 33 apply (18/15), 7 learn, 19 categories.

I did not pad this to a round number. The Backend brief asks for coverage of the product

claim, reproducibility, and both intervention and non-intervention — not volume. (The

"~500 records" figure some readers may expect is from the *Golden Goose* brief, a different

role's task; see [docs/00-material-manifest.md](docs/00-material-manifest.md) finding F1.)

Where one memory is tested in several sentences that is not padding: the context gate is

the mechanism under test, so the same word in a shipping context, a fruit context and a

quoted context are three genuinely different tests.

## Limitations

Stated plainly, with causes. All four remaining evaluation failures are here.

1. **Sentence-initial position loses the case signal** (2 dev misses). "Kiwi users are

   reporting slow dictation." is not corrected: the formatter capitalises every sentence

   start, so a capital there carries no information, and one weak cue ("users") does not

   reach the ordinary-word bar. Mid-sentence, the same word is corrected. Fixable with

   sentence-level part-of-speech evidence; not attempted, because guessing would trade the

   zero false-intervention rate for a couple of recall points.

2. **Multi-token case-only corrections need context they often lack** (2 holdout misses).

   "Amber rail signed the contract." is not corrected to "Amber Rail". Every token is

   ordinary English and the span is sentence-initial, so the bar sits at 0.75 against a

   context score of 0.45. **I deliberately did not fix this**: it was discovered on the

   holdout split, and tuning a threshold to fix a holdout failure is precisely the

   overfitting the holdout exists to detect. It is recorded here instead.

3. **Word-type inference from a single sentence is weak.** `Sumeet` and `Vishal` are typed

   `term` rather than `person`. The type only selects which cues count as support, so a

   wrong type costs *recall*, never precision — and the interface lets a user fix it in one

   click. This is the clearest place an LLM would earn its keep, and it is not yet measured.

4. **British spellings are missing from the ordinary-word lexicon.** `colour` is not in

   Webster's 2nd, so a `colour`→`color` preference is classified as an ASR error rather than

   a preference. Behaviour is still correct here, but the classification is wrong for the

   wrong reason.

5. **`llm_only` baseline: NOT MEASURED.** No model key was set for the committed run, so

   the "is durable memory needed at all, or is a good model enough" comparison is stated as

   unmeasured rather than estimated. Everything needed to run it is in the repository.

6. **The LLM adjudicator and `prompt` mode are implemented and unit-tested with fakes, but

   their live behaviour has been spot-checked with latency and cost measured; a systematic live benchmark is NOT MEASURED** for the same reason.

7. **Single user.** `user_id` exists on every row and is threaded through, but multi-tenancy

   is a stated non-goal: nothing is measured at more than one user.

8. **The formatter is a stand-in**, not Kivi's. It reproduces the brief's stage-2 example

   and does sentence casing, terminal punctuation and proper-noun casing; it will not match

   a real language model everywhere. The demo and the evaluation both accept a formatted

   string directly, which is how the brief frames it.

9. **Cold multi-token phonetic collapse is a stretch.** "cuban eighties" → "Kubernetes"

   works from a *learned* variant. Guessing it with no prior correction sits right at the

   admission threshold and is not reliable. The product answer is that the system learns it

   from one correction and is then exact forever.

## Honest status of every claim

| Claim | Status |

|---|---|

| Three stages, learning, retrieval, gating, application, explanation, update, delete, reset | **VERIFIED** — 154 tests, plus the measured evaluation |

| Metrics, latency, storage figures in this document | **VERIFIED** — emitted by `python -m kivi eval` |

| Encoder beats Soundex/Metaphone on the Indic set | **VERIFIED** — asserted in the test suite |

| Baseline comparison | **VERIFIED** — same cases, same memory state |

| Sarvam adjudicator + prompt mode | **IMPLEMENTED**, contract verified against published docs; **live behaviour NOT MEASURED** |

| `llm_only` baseline | **NOT MEASURED** |

| Kivi's production implementation | **UNKNOWN** and never guessed at. Not provided, per the brief. |

## AI use

This submission was built with **Claude Code (Claude Opus 5)** used as a pair-programming

agent throughout, at my direction. What that means concretely:

- **Mine:** the problem framing (the P1/P2/P3 decomposition and the argument that P3 is

  what justifies the product), the decision that non-intervention is the primary product

  quality, the evidence ladder and the "adjudicate but never promote" rule, the choice to

  keep the system deterministic by default, and the evaluation design — in particular

  keeping gold labels structurally independent and refusing to tune on the holdout.

- **AI-assisted:** essentially all of the implementation, the test suite, the dataset

  authoring, and this documentation, written iteratively against the design above.

- **AI-discovered:** many of the bugs in

  [docs/04-failure-analysis.md](docs/04-failure-analysis.md) surfaced from writing

  adversarial cases and reading the measured failures, rather than from inspection.

- **Not AI-generated:** no evaluation gold label was produced by running the system, and

  no metric in this repository was written by hand.

The corpus in `data/seed/` and `eval/datasets/` is synthetic and authored for this task. No

Kivi user data was used, and none was available.

## Repository map

```

kivi/                  the system

  migrations/001_init.sql   the schema, with each column's justification inline

  text.py                   tokenisation, normalisation, morphology

  phonetics.py              three encoders + similarity, so the choice can be measured

  lexicon.py                the ordinary-English prior — the false-positive defence

  memory.py                 CRUD, confidence, promotion, supersession, deletion

  learning.py               four extractors, the evidence ladder, every refusal

  retrieval.py              the four-tier cascade

  context.py                the gate: the bar, and the evidence

  apply.py                  no-ops, gating, ambiguity, overlap, rewriting

  pipeline.py               the three stages + the persisted decision trace

  formatter.py              a clearly-labelled stand-in for Kivi's formatting LM

  llm.py / adjudicator.py   the optional Sarvam client and the uncertain-band judge

  api.py / cli.py           HTTP API and command line

  eval/                     dataset loading, baselines, metrics, runner, report

web/                   the demo interface (no build step)

data/lexicon/          vendored word lists, with provenance

data/seed/             reproducible seed OBSERVATIONS (not memories)

eval/datasets/         dev.jsonl, holdout.jsonl, scenarios.json

eval/build_dataset.py  authors the dataset; imports nothing from kivi, by design

eval/results/          committed evaluation output

docs/                  material manifest, taxonomy, design, eval spec, failure analysis, review

tests/                 154 tests, including one regression test per bug found

```

Start with [docs/01-failure-taxonomy.md](docs/01-failure-taxonomy.md) for the reasoning, or

[HOW_TO_RUN.md](HOW_TO_RUN.md) to run it.