# Kivi - Personal Word Memory for Better Transcripts

Kivi is a word-level memory system that learns the words and spellings that are important to one person.

The idea is simple: when ASR gets a personal name, company, project, or other word wrong, Kivi can learn the correct version from the user's corrections and use it the next time a similar mistake happens.

At the same time, Kivi is careful about when it should change something. If there isn't enough evidence, it leaves the text alone instead of making a guess.

## Live Demo

Try the deployed version here:

https://kivibackend-focusedfullstack-production.up.railway.app/

The demo shows the complete flow:

**ASR output → Formatted text → Memory-aware text**

For example:

```text
ASR output
ask aditya to review the sarvam kiwi service

Formatted
Ask Aditya to review the Sarvam Kiwi service.

Memory-aware
Ask Aaditya to review the Sarvam Kivi service.
```

The important part is that Kivi does not simply replace `kiwi` with `Kivi` everywhere.

It first checks the memory it has learned and the context of the sentence before making a correction.

If the memory is not strong enough, it stays silent.

---

## What I Was Trying to Solve

The problem I focused on is something that can still happen even when ASR and formatting are working reasonably well:

**Personal words can come out wrong.**

For example:

- `Kivi` → `kiwi`
- `Aaditya` → `Aditya`
- `Kubernetes` → `cuban eighties`

A general dictionary or a better ASR model may solve some of these cases, but personal vocabulary is different. The correct answer can depend on the individual user.

Kivi tries to solve this by learning from the user's own corrections and previous interactions.

## The Main Idea

I split the system into three main parts:

1. **Learning** — learn useful personal vocabulary from evidence.
2. **Retrieval** — find memories that could match what was heard.
3. **Context gating** — decide whether the memory should actually be applied.

The third part is especially important.

For example:

```text
I ate a kiwi on the flight.
```

should stay unchanged.

But:

```text
Ship the Kiwi update on Friday.
```

can become:

```text
Ship the Kivi update on Friday.
```

Kivi uses the surrounding context and the evidence stored with the memory to make this decision.

So the goal isn't just to correct more words.

**The goal is to correct the right words and leave the rest alone.**

---

## Results

The evaluation is based on separate development and holdout cases.

| Metric | Kivi (dev) | Exact baseline | Fuzzy baseline | Kivi (holdout) |
|---|---:|---:|---:|---:|
| Correction precision | **1.000** | 0.636 | 0.157 | **1.000** |
| Correction recall | **0.965** | 0.737 | 0.281 | **0.889** |
| False interventions | **0** | 24 | 46 | **0** |
| Exact text accuracy | **0.983** | 0.670 | 0.263 | **0.939** |

The result I care about most here is **zero false interventions** on both dev and holdout.

A wrong correction is worse than missing a correction because it changes text that may have been correct in the first place.

### Performance

- Retrieval mean: **0.99 ms**
- Retrieval p95: **1.43 ms**
- End-to-end mean: **1.07 ms**
- Default configuration uses **no model calls**
- Storage: **172 KB for 19 memories**, including their evidence and audit information

---

## How Kivi Learns

Kivi doesn't store every word it sees.

A memory needs evidence before it can affect the transcript.

Examples of stronger evidence include:

- Manual entry
- The user explicitly spelling a word
- The user correcting Kivi's output
- Repeated observations across different interactions

Weaker evidence can create a candidate, but a candidate cannot directly change text.

The main rule is:

> Only confirmed memories can change the transcript.

Another important rule is that an LLM can help with an uncertain decision, but it cannot create a permanent memory by itself.

---

## How Retrieval Works

Kivi does not use embeddings or a vector database.

Instead, it uses four retrieval levels:

```text
exact → variant → phonetic → fuzzy
```

The phonetic matching is designed around pronunciation variations that commonly appear in Indian-English dictation, including:

- `aa / ee / oo` vowel variations
- aspirated consonants such as `kh / gh / th / dh / ph / bh`
- `v / w` variations
- `ksh / jn / gn` clusters

The idea is to find words that may sound similar without treating every semantically similar word as a match.

For example, `Kivi` and `kiwi` need to be connected, while `kiwi` and `mango` should not be.

---

## Context Gating

Similarity alone is not enough.

Kivi separates two questions:

**Could this be the word I'm looking for?**

and

**Should I actually change it here?**

The context gate looks at things such as:

- learned word associations
- word type
- application context
- capitalization
- whether the word is an ordinary English word
- how confident the memory is

If two memories are almost equally good matches and the context cannot decide, Kivi abstains instead of guessing.

---

## Architecture

```text
                 ┌───────────────────────────┐
                 │         LEARNING          │
                 │                           │
                 │ ASR / formatted text /    │
                 │ user edits / context      │
                 │            │              │
                 │            ▼              │
                 │       typed evidence      │
                 └────────────┬──────────────┘
                              │
                              ▼
                 ┌───────────────────────────┐
                 │          SQLite           │
                 │                           │
                 │ memories + variants +     │
                 │ evidence + decisions      │
                 └────────────┬──────────────┘
                              │
                              ▼
                 ┌───────────────────────────┐
                 │        RETRIEVAL          │
                 │                           │
                 │ exact → variant →         │
                 │ phonetic → fuzzy          │
                 └────────────┬──────────────┘
                              │
                              ▼
                 ┌───────────────────────────┐
                 │       CONTEXT GATE        │
                 │                           │
                 │ Should this correction    │
                 │ actually be applied?      │
                 └────────────┬──────────────┘
                              │
                              ▼
                    Memory-aware transcript
```

The whole system runs as one Python application with a small number of dependencies and no frontend build step.

---

## Tech Stack

- Python
- SQLite
- Vanilla JavaScript
- HTTP API
- HTML/CSS
- Optional Sarvam LLM adjudication
- Pytest


---

## Running Locally

Run the evaluation with:

```bash
python -m kivi eval --split both
```

The repository contains **154 tests** covering the core pipeline, learning, memory, retrieval, context gating, API, and regression cases.

---


## Repository Structure

```text
kivi/
├── memory.py          Memory storage and lifecycle
├── learning.py        Learning and evidence policy
├── retrieval.py       Memory retrieval
├── context.py         Context gating
├── apply.py           Applying corrections
├── pipeline.py        End-to-end pipeline
├── formatter.py       Formatting stage
├── adjudicator.py     Optional Sarvam adjudication
├── api.py             HTTP API
└── cli.py             Command line interface

eval/                  Evaluation datasets and runners
tests/                 Test suite
web/                   Demo interface
docs/                  Design and evaluation documentation
data/                  Seed data and lexicons
```

---

## Limitations

There are still cases where Kivi deliberately chooses not to correct something.

For example:

- Sentence-initial words can lose useful capitalization information.
- Some multi-token case-only corrections need more context.
- Word-type inference from a single sentence is limited.
- British spellings are not fully represented in the current ordinary-word lexicon.
- The `llm_only` baseline has not been measured.
- A systematic live benchmark of the LLM adjudicator has not been performed.
- The current implementation is designed for a single user.

These are documented rather than hidden because understanding where the system fails is part of evaluating it properly.

---


If you want to understand the reasoning behind the implementation, start with:

- [`docs/01-failure-taxonomy.md`](https://github.com/Srikanth40-svg/KIVI_BACKEND-FOCUSEDFULLSTACK/blob/main/docs/01-failure-taxonomy.md)
- [`docs/02-design.md`](https://github.com/Srikanth40-svg/KIVI_BACKEND-FOCUSEDFULLSTACK/blob/main/docs/02-design.md)
- [`docs/03-evaluation-spec.md`](https://github.com/Srikanth40-svg/KIVI_BACKEND-FOCUSEDFULLSTACK/blob/main/docs/03-evaluation-spec.md)
- [`docs/04-failure-analysis.md`](https://github.com/Srikanth40-svg/KIVI_BACKEND-FOCUSEDFULLSTACK/blob/main/docs/04-failure-analysis.md)

---

**Author**  
Jadi Srikanth |
IIT Madras

