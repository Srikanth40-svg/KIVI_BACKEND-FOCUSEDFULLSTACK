# Phase 18 — Hostile review

Written as a Sarvam reviewer looking for reasons to reject this. Scores are mine and
deliberately ungenerous; anything below 9 gets a weakness, the objection I expect, and
whether I fixed it or chose not to. Nothing here is scored 10 without evidence in the
repository.

| Dimension | Score | One-line verdict |
|---|---|---|
| Product clarity | 9 | The P3 argument makes the product's reason to exist explicit. |
| Memory design | 9 | Span-based, typed, evidenced; every column justified in the schema. |
| Learning policy | 9 | Typed evidence ladder; refusals are first-class and logged. |
| Correction quality | 9 | Precision 1.000 on both splits, measured. |
| Contextual accuracy | 8 | Strong, but sentence-initial position is a known blind spot. |
| False-positive control | 10 | 0 false interventions on 76 must-not-change cases, vs 25 for baselines. |
| Retrieval | 8 | Fast and justified; tier 4 untested at large vocabulary. |
| Persistence | 9 | Real migrations, indexes, constraints, audit trail. |
| Update / delete | 9 | Supersession preserves history; deletion takes effect immediately. |
| Backend quality | 8 | Clean and typed, but `learning.py` is doing too much. |
| API quality | 9 | Deterministic, documented, returns reasoning with every result. |
| Testing | 9 | 154 tests, one regression test per bug found. |
| Evaluation | 9 | Structurally independent labels, holdout discipline, failures published. |
| Dataset quality | 7 | Well-targeted and honest, but small, synthetic, and single-author. |
| Reproducibility | 9 | One command, no credentials, verified from a clean clone. |
| UX | 8 | Purpose-built and explanatory; not a polished consumer surface. |
| Performance | 9 | 0.99 ms retrieval, measured with percentiles. |
| Cost | 10 | Zero by default, and cost is computed from published prices when a key is set. |

---

## Dataset quality — 7

**Weakness.** 182 cases, entirely synthetic, authored by one person — the same person who
built the system. No real dictation, no second annotator, no inter-annotator agreement.

**Why it matters.** The most likely way this whole submission is wrong is that my *idea* of
what should be corrected differs from what real Kivi users want. A dataset I wrote cannot
detect that. Perfect precision on my own labels is a weaker claim than it looks.

**Likely objection.** "You scored 1.000 against your own opinions."

**Root cause.** No user data was available, and the brief says none would be provided.

**Fixed?** Partly, and deliberately not fully.
- Mitigated: gold labels are structurally independent of the *system* (the generator
  imports nothing from `kivi`), the holdout is a different persona, negative cases
  outnumber positive ones on dev (61 vs 57), and I published two cases where **my own label
  was wrong** rather than quietly correcting them.
- Not mitigated: it is still one author's judgment. I did not inflate the count to look
  more thorough — padding a single-author dataset makes it larger, not more valid, and the
  Backend brief asks for coverage rather than volume. I would rather state the limitation
  than disguise it.

**Measured result.** 38 categories on dev, 19 on holdout, 6 scenarios, both intervention
and non-intervention classes populated. Composition is reported exactly in `summary.json`
rather than described.

## Contextual accuracy — 8

**Weakness.** Sentence-initial position destroys the case signal, which is the single most
informative context feature. "Kiwi users are reporting slow dictation." is not corrected.

**Likely objection.** "Your best signal is just capitalisation from the previous stage."

**Response, honestly.** Partly true, and I think defensible: the formatting stage has
already made a proper-noun judgment and throwing that away would be wasteful. But it means
the gate leans on an upstream component I did not build and cannot rely on in production.
The learned co-occurrence profile and type cues are the independent half, and they are
weaker.

**Fixed?** No. A fix needs sentence-level part-of-speech evidence, and guessing would trade
a zero false-intervention rate for two recall points. Recorded as limitation 1.

## Retrieval — 8

**Weakness.** Tier 4 is a bounded linear scan over the confirmed vocabulary. Measured at
0.99 ms mean for ~30 forms; **never tested at 10,000**.

**Likely objection.** "This does not scale."

**Response.** The schema already carries the phonetic index that a prefix-blocked query
would use, and one person's personal vocabulary is genuinely small — that is the shape of
the problem, not an assumption I need. But I have not measured it, so I claim nothing.

**Fixed?** No. Building an index I cannot show is needed would be complexity that has not
earned its place. Stated as untested rather than implied to work.

## Backend quality — 8

**Weakness.** `kivi/learning.py` is ~600 lines and holds four extractors, the shape
filters, type inference, variant classification and the policy engine. It is the file I
would split first.

**Likely objection.** "This module has more than one reason to change."

**Fixed?** No — a refactor at this stage would risk the measured behaviour for no
measurable gain, and the seams are already visible (each extractor is a pure function
returning `Proposal`s, so splitting is mechanical). Flagged rather than rushed.

## UX — 8

**Weakness.** The interface is an engineer's instrument: it shows scores, bars, reason
codes and JSON signal dumps. A real user would not want this.

**Response.** Deliberate. The brief asks that a reviewer can *understand why the system did
or did not intervene*, which is a debugging requirement, and the guided journey is built
for exactly that reading. The consumer surface for this feature is Kivi's existing
Dictionary; what is missing there is not visualisation but the self-filling behaviour
underneath, which is what this builds.

**Fixed?** N/A — the audience is the reviewer.

## Objections I expect that I think are wrong

**"The corrections are hardcoded for the brief's example."**
Step 1 of the guided journey wipes the database and step 2 runs the brief's own sentence
through empty memory: it passes through untouched. `test_nothing_happens_when_memory_is_empty`
asserts it. The seed is a list of *observations* replayed through the real policy, not a
list of memories, so if the policy changed the seeded state would change with it. There is
no branch anywhere keyed on a demo word.

**"Precision 1.000 means the thresholds are tuned to the test set."**
They are tuned on dev, which is the point of having a dev split — and the holdout, a
different persona with no shared vocabulary, also reports precision 1.000 and a 0.0
false-intervention rate. More to the point: when the holdout surfaced two real misses, I
**did not fix them**, precisely so the holdout stays unbiased. That decision is in the
README limitations and in `04-failure-analysis.md`.

**"There's no LLM, so this isn't really an AI system."**
The deterministic core is a decision, not an omission, and it is measured: the two
baselines share the same memory state and lose on both precision and recall. The LLM
adjudicator is implemented, documented per call site, and confined to the uncertain band —
and it is honestly reported as **NOT MEASURED** live, because no key was set for the
committed run. Choosing a mechanism that needs no model for the parts a model does not do
better is the engineering judgment the brief asks for.

**"Only 182 evaluation cases."**
Addressed above at score 7, and worth being precise: the "~500 records" figure belongs to
the *Golden Goose* brief, a different role's task. The Backend brief asks for cases that
test the product claim, include deliberate non-intervention, and are reproducible. I would
rather have 61 negative cases I can defend than 500 I generated to hit a number.

## The single biggest risk in this submission

Not a bug — the dataset. Every headline number is measured against labels I wrote. The
system is internally consistent, structurally honest about where those labels came from,
and unusually forthcoming about its failures; but if my judgment about what a Kivi user
wants corrected is wrong, the evaluation would not tell me. The first thing I would do with
real dictation logs is re-label a sample blind and re-run — the harness already supports it,
since a dataset is just a JSONL file and a scenario.
