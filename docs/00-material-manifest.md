# Phase 0 — Material & Environment Manifest

Status legend: **VERIFIED** = I opened/ran it myself. **ASSUMED** = reasonable inference. **UNKNOWN** = not available.

## A. Assignment material

| Resource | Type | Location | Access | Verified? | Relevance | Impact if missing |
|---|---|---|---|---|---|---|
| Kivi_Backend_Full_Stack_Task_Clean_Cover.pdf | Task brief, 6pp | ~/Downloads | read | **VERIFIED** (full text extracted) | **PRIMARY — this is the assignment** | none, we have it |
| Kivi by Sarvam Job Description.pdf | JD, 5pp | ~/Downloads | read | **VERIFIED** | Role context: "architect voice-first systems", agentic, production code | low |
| Kivi_Golden_Goose_Task_Final.pdf | *Different role's* task, 7pp | ~/Downloads | read | **VERIFIED** | Cross-reference only. Confirms product facts; its requirements are NOT mine | see Finding F1 |
| Kivi production implementation | source | — | — | **UNKNOWN** | brief states explicitly it will not be provided | must not fabricate it |
| Kivi ASR model | model | — | — | **UNKNOWN** | brief: not required to build | ASR output is an *input* to my system |
| Kivi's formatting LM / Styles | model+prompt | — | — | **UNKNOWN** | brief: formatted output is provided as input | I supply a clearly-labelled stand-in formatter |
| Hidden benchmark / private user corpus | data | — | — | **UNKNOWN** | brief states explicitly none will be provided | I must author the dataset and gold labels |
| heykivi.ai / existing app | web | internet | reachable | not inspected yet | Dictionary feature behaviour | low; brief is self-contained |
| Existing repo / starter code / screenshots / sample data | — | — | — | **UNKNOWN** (working dir was empty) | greenfield | none |

## B. Environment (all VERIFIED by execution)

| Component | Status |
|---|---|
| Working dir | `/Users/roshan/Documents/Personal/shrikant` — was **empty**, not a git repo |
| OS | macOS 26.6.2, arm64 |
| Python | system `3.9.6` (EOL) **and** Homebrew `python3.12` → `3.12.13` at `/opt/homebrew/bin/python3.12` |
| Node / npm | `v24.18.0` / `11.16.0`; `node:sqlite` importable |
| SQLite | CLI `3.51.0`; python `sqlite3` module links lib `3.53.4` |
| Docker | **ABSENT** → containerised review method is not testable here, so it will not be the primary method |
| Postgres/MySQL client | **ABSENT** |
| git / gh | `2.50.1` / `gh` authenticated as `Nbplanet-633` |
| Network | pypi 200, npmjs 200, api.anthropic.com 405-to-GET (i.e. reachable) |
| **LLM credentials** | **NONE.** No `ANTHROPIC_*`/`OPENAI_*`/`SARVAM_*`/etc. in env; no `~/.anthropic`; nothing in `~/.zshrc` |
| Free disk | 818 GiB |

## C. Findings that change the plan

**F1 — The "~500 records" target is not in my brief.** It appears in the *Golden Goose* brief ("Create or obtain approximately 500 transcript-like records"), together with the "we will run your pipeline on our own internal 500-dictation corpus / documented corpus-import procedure" requirement. The Backend brief has **neither**. It says only: the evaluation must go substantially beyond the example, include non-intervention cases, be reproducible, and preserve inputs / expected / actual / memory-state / reason per case.

→ Consequence: dataset size is a means, not a target. I will build to *coverage of the taxonomy* and report exact composition. ~500 cases is a fine by-product; zero filler. A documented import path is cheap insurance and I'll include it, but it is not the review method.

**F2 — The brief tells me where memory is applied.** p.3: "how the relevant memory should be found and **placed into the formatting prompt** when the person speaks again." That is a direct architectural signal: retrieval feeds the formatting stage; it is not post-hoc find-and-replace. My design must honour it (and can still measure a replace-only baseline against it).

**F3 — Kivi already ships a "Dictionary" (p.2), and the brief's origin story is that the team spent a long time deciding "what belonged inside it, what did not."** So the product I am building is not "add a dictionary." It is: *the Dictionary that fills itself from ordinary use, with evidence, and knows when to keep quiet.* Precision and abstention are the product, not coverage.

**F4 — Independent definition of scope, from the Golden Goose brief p.2:** "Styles determine how that speech should become written language, while **phonetic memory helps Kivi recognise the words that belong to the person using it.**" This confirms: word-level identity is mine; sentence-level style, tone, punctuation and formatting conventions are **Styles' job, not mine**. I will state that exclusion explicitly rather than quietly absorbing formatting wins into my metrics.

**F5 — No LLM key present.** Blocking for one design decision (see Phase 2 open question).

**F6 — Reviewer is a coding agent** that "will not infer missing setup, repair the application, or contact you." It *may* install declared dependencies and *may* provide model credentials — "may", not "will".

→ **The system must be fully functional and fully evaluable with no LLM key.** Any LLM use must be an optional, measured layer with a deterministic fallback. This is forced by the brief, and it conveniently doubles as the baseline-vs-improved comparison the evaluation needs.

## D. Exact requirement extraction (from the Backend brief only)

Part One — build:
1. R1 Three transcript stages must exist and be distinguishable: ASR output, formatted output, memory-aware output.
2. R2 Decide + implement: what deserves to change future behaviour; what to do when evidence is weak or wrong.
3. R3 Learning through *ordinary use*.
4. R4 Durable storage; change; removal.
5. R5 Retrieval, and placement of retrieved memory into the formatting prompt.
6. R6 Runnable demo permitting: supply observations → inspect memory state → supply new ASR + formatted → see memory-aware result → understand why it did or did not intervene → reset and repeat.
7. R7 Show discovered cases beyond the single example; state what the system distinguishes and where it deliberately does nothing.

Part Two — prove:
8. R8 Define success; author data, cases, expected behaviour.
9. R9 Must include both intervention and deliberate non-intervention.
10. R10 Per case preserve: inputs, expected, actual, relevant memory state, decision reason.
11. R11 Report useful interventions **separately from** unnecessary/incorrect ones.
12. R12 Include latency, model usage, cost, DB growth *wherever they matter*.
13. R13 Reproducible; individual cases inspectable; conclusions verifiable.
14. R14 Post-hoc cherry-picked successes are explicitly not an evaluation.

Submission — repo must contain: source; runnable demo; **schema and migrations**; **reproducible seed data**; complete evaluation + dataset; **generated results committed**; README (product, architecture, decisions, limitations, AI use); RUN.md (primary review method declared first, then the 10 enumerated items). `.env.example` if a key is used; no committed credentials.
