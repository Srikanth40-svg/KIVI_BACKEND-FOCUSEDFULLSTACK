# Phase 8 — Evaluation specification

Written before the dataset was authored, and before any metric was measured. The point of
writing it first is that "what counts as success" cannot then be chosen to flatter whatever
the system turned out to do.

## What success means

The product claim is: **Kivi learns the words that belong to this person, applies them when
the sentence really refers to them, and stays quiet otherwise.** Three claims, so three
things to measure:

1. **Did it learn the right words, at the right strength?** — memory precision / recall.
2. **Did it change the text when it should, and only then?** — the intervention 2×2.
3. **Can an engineer see why?** — every decision, including every abstention, must carry a
   persisted reason.

A fourth, non-negotiable requirement: **a false correction is a worse failure than a missed
one.** It damages text the person said correctly. So false-intervention rate is reported as
a first-class number, not folded into an accuracy average.

## The central table

|  | should change | should not change |
|---|---|---|
| **changed** | correct intervention | **false intervention** |
| **left alone** | missed intervention | correct silence |

Derived:

- `correction_precision` = correct / (all changes made)
- `correction_recall` = correct / (all changes that should have been made)
- `false_intervention_rate` = false / (false + correct silence) — of the texts it should
  have left alone, how often did it damage one
- `missed_intervention_rate` = missed / (all changes that should have been made)
- `exact_text_accuracy` = (correct + correct silence) / all cases

Two definitions stated because they are easy to fudge:

- A changed text counts as **correct only if it equals the gold text exactly.** Changing
  the right word to the wrong thing is a false intervention, not partial credit.
- **Correct silences are counted, not discarded.** They are the denominator that makes
  false-intervention rate meaningful, and they are the majority of real dictation.

## Metrics, and which ones were deliberately excluded

Measured: memory precision/recall · correction precision/recall · false-intervention rate ·
missed-intervention rate · exact text accuracy · contextual accuracy (by category) ·
update correctness · deletion correctness · multi-interaction learning · retrieval latency
· end-to-end latency · model calls · model cost in ₹ · database growth.

**Excluded, with reasons.** Word error rate — this system changes individual words, so WER
would be dominated by text it never touched and would move for reasons unrelated to memory.
Any measure of "corrections per transcript" — maximising it is precisely the wrong
objective. Semantic similarity of output to gold — it would score a wrong-but-plausible
name as nearly correct, when that is the exact failure being hunted.

## Case kinds

Three, because the product makes three different kinds of claim:

- **`apply`** — given a known memory state, the memory-aware output must equal the gold
  text and the intervention flag must match. Some cases additionally assert the *reason
  code*, so that being right for the wrong reason is caught.
- **`learn`** — given a sequence of observations, a named word must end in a specific
  status, or must be `absent`. This is where "did not learn" is tested as rigorously as
  "did learn".
- **`state`** — lifecycle invariants that are not about one word: supersession links,
  deletion events, counts.

## Scenarios: isolation and reproducibility

Every case names a **scenario**, which fixes the memory state it runs against. Before each
scenario the runner resets the database, replays the committed seed, then replays the
scenario's own setup and any explicit lifecycle operation (delete / supersede / demote).
Learn and state cases get a freshly rebuilt scenario each, because they mutate memory.

Consequence: **a case's result cannot depend on which cases ran before it**, and the whole
suite is order-independent. The evaluation also runs against its own database file, so
evaluating never disturbs the demo state a reviewer is looking at.

## Gold-label independence

Enforced structurally rather than promised:

- Gold labels live in `eval/build_dataset.py`, which **does not import or run the system.**
  There is no `import kivi` in it and no database access, so a label cannot have been copied
  from the system's own output.
- The runner only reads the dataset. Nothing in `kivi/eval/` writes to `eval/datasets/`.
- The loader **refuses to start** if a case is missing its expected result.
- One consistency check runs at load time: a case labelled `intervention: none` whose
  expected text differs from its input is rejected as a self-contradiction, and vice versa.

When the system disagrees with a label, that is reported as a failure. Two labels were
changed during development; both changes are recorded, with reasoning, in
[04-failure-analysis.md](04-failure-analysis.md) — including one where my original label was
simply wrong.

## The holdout, and the discipline attached to it

`holdout.jsonl` runs against a **different person's vocabulary**, taught from scratch by its
own observations. It shares no words, no wrong forms and no sentence contexts with either
the seed or the dev split — `Prathik`, `Zorvex`, `Nilima`, `Vercel`, `TensorFlow`, `Mumbai`,
`Amber Rail`, `@nilima_r`, `OKR`, `color`.

**No threshold in this system was chosen by looking at holdout results.** When the holdout
surfaced two genuine misses (multi-token case-only corrections), the fix was *not* applied,
because tuning to fix a holdout failure destroys the only unbiased estimate in the
repository. Those two failures are reported in the README's limitations instead. That is the
whole point of having a holdout, and spending it for two recall points would be a bad trade.

## Baselines

Complexity has to earn its place, so the simpler things run on the same cases against the
same memory state:

- **`exact`** — every learned wrong form is replaced wherever it appears, no context. This
  is what "just add a dictionary" actually does.
- **`fuzzy`** — exact plus phonetic and fuzzy matching, still no context gate. Isolates
  whether the *matching* or the *gating* is what matters.
- **`llm_only`** — no persistent memory: hand the sentence to a model and ask it to fix
  personal words. Tests the premise of the product itself. Requires a key; reported as
  **NOT MEASURED** when none is present rather than estimated.

Learn and state cases are reported for the full system only: the baselines implement no
learning policy, so scoring them there would produce numbers that look like failures but
mean nothing. Reason-code assertions likewise apply only to the full system — the baselines
have no notion of a reason, and holding them to one would be a rigged comparison.

## Per-case artefacts

For every case, `eval/results/cases-<split>-<system>.jsonl` preserves: the inputs, the
expected result, the actual result, the pass/fail outcome and its 2×2 classification, the
reason codes and reason texts, **the relevant memory state at the time**, the full candidate
trace with every score and gate, the latency, and the decision id for replay.

`failures-<split>.md` then lists every failing case in full — inputs, expected, actual, the
system's own reasoning, and the memory that was in play — grouped by category. Nothing is
summarised away, because the purpose of that file is that a reviewer can see exactly what
the system got wrong and what it thought it was doing.

## Reproducibility

`python -m kivi eval --split both` regenerates everything in `eval/results/`. The run
records its own environment in `summary.json`: Python version, platform, git SHA, the full
threshold set, and whether model credentials were present. Default configuration makes no
network calls, so the numbers are deterministic. Metrics that were not measured are written
as `not_measured` with a reason, never as zero.
