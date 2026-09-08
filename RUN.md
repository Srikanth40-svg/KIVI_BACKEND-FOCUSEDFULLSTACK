# How to Run Kivi

## Run It Locally

One Python process serves both the JSON API and the demo interface. There is no build

step, no second server, no container, and no credentials are required — the complete

system and the complete evaluation run offline.

> Prefer a walkthrough? [HOW_TO_RUN.md](HOW_TO_RUN.md) is the same thing as numbered

> steps with the expected output of each one.

>

> A model key is optional and enables two extra, separately-measured modes. Everything the

> submission claims can be verified without one. See [§10](#10-optional-model-credentials).

---

## 1. What You Need

| Requirement | Version | Notes |

|---|---|---|

| Python | 3.10 minimum, 3.11+ recommended | Verified on 3.12.13. 3.10 is a hard floor: PEP 604 unions are evaluated at runtime. |

| SQLite | bundled with Python | No server to install. Verified against SQLite 3.53.4. |

| make | optional | Every target is also given as a plain command below. |

Nothing else. No Docker, no Node, no database server, no compiler — every dependency is

pure Python and there are five of them.

Check this first — on macOS python3 is often the system Python 3.9, which is too

old and fails with a confusing pydantic error rather than an obvious one:



python3 --version      # must print 3.10.x or newer



If it shows Python 3.9 or older, use a newer Python when creating the virtual environment.



python3.12 -m venv .venv        # or /opt/homebrew/bin/python3.12, or python3.11, etc.



Kivi checks this at import and refuses to start with a message naming the fix, so you

cannot get a half-working install.

## 2. Environment Variables

None are required. The defaults are correct for a local review.

| Variable | Default | Meaning |

|---|---|---|

| KIVI_DB_PATH | ./kivi.db | SQLite file location |

| KIVI_APPLY_MODE | deterministic | how stage 3 is produced; prompt needs a key |

| KIVI_USE_LLM_ADJUDICATOR | 0 | optional LLM tie-breaker; needs a key |

| SARVAM_API_KEY | *(empty)* | optional. See [§10](#10-optional-model-credentials) |

| KIVI_LLM_MODEL | sarvam-105b | only used when a key is set |

| KIVI_LLM_BASE_URL | https://api.sarvam.ai/v1 | only used when a key is set |

You only need .env if you want to use the optional API key:



cp .env.example .env



## 3. Install the Dependencies



py -3.12 -m venv .venv

.\.venv\Scripts\pip.exe install --upgrade pip

.\.venv\Scripts\pip.exe install -r requirements.txt



You can also use make install if you have make installed.

> All commands below use .\.venv\Scripts\python.exe explicitly, so you never need to activate

> the virtualenv.

## 4. Set Up the Database



.\.venv\Scripts\python.exe -m kivi migrate     # creates kivi.db, applies migrations

.\.venv\Scripts\python.exe -m kivi seed        # replays the committed seed observations



You can also use make seed.

The seed command loads 26 example observations and creates 19 memories, including 15 confirmed memories.

These figures are deterministic: verified identical across repeated runs and across

Python 3.9 and 3.12.



replayed 26 seed observations

learning outcomes: {'confirmed': 14, 'rejected': 14, 'candidate': 5, 'reinforced': 8}

  id  canonical              type       status      conf  variants

  ...

   1  Kivi                   product    confirmed   0.90  Kiwi[asr_]

   2  Aaditya                person     confirmed   0.95  Aditya[asr_]



The seed is a list of observations, not a list of memories. It is replayed through the

real learning policy, so the state you see was earned by evidence exactly as a real user's

would be. Nothing is inserted directly into the memory table.

## 5. Start the App



.\.venv\Scripts\python.exe -m uvicorn kivi.api:app --port 8000



You can also use make run.

## 6. Open the Website

<http://localhost:8000>

Interactive API documentation: <http://localhost:8000/docs>

## 7. What to Try in the App

The Guided journey tab does all of this in twelve ordered steps, each one a real API

call. If you only do one thing, do that. Manually:

The brief's example. Go to *Three stages*, click the the brief's example chip,

   press Run all three stages. You should see:

   ```

   1 · ASR output      ask aditya to review the sarvam kiwi service

   2 · Formatted       Ask Aditya to review the Sarvam Kiwi service.

   3 · Memory-aware    Ask Aaditya to review the Sarvam Kivi service.

   ```

   The changed words are highlighted, and the panel below names the memory behind each

   correction, its match tier, its similarity scores, and the context bar it had to clear.

Deliberate non-intervention. Click a kiwi you can eat → Run. The text comes

   back untouched, and the *Abstained* section explains that kiwi is an ordinary English

   word (frequency rank 16,870) whose context did not reach the required bar.

A generic word that collides with a product. Click a generic cursor → Run.

   Cursor is a learned product memory, but "Move the cursor to the end of the line" is

   left alone.

A different person with the same-sounding name. Click a different Aditya → Run.

   Aditya Ghosh is a second colleague, so the Aditya inside that name is protected.

A two-word mis-hearing. Click a two-word mishearing → Run.

   "The Cuban Eighties cluster" becomes "The Kubernetes cluster".

Teach it something. Go to *Teach*, click a correction, press **Ingest

   observation**. Then click a hypothetical and ingest that too — it is refused, with

   the reason given.

Inspect memory. Go to *Memory*, click any row. You get the evidence that created

   it, its confidence history, the wrong forms it answers to, and the context terms it

   learned. Use Change spelling… to supersede it (the old form is kept and starts being

   corrected), or Delete (it stops affecting output immediately).

Why it did not learn. Go to *Why not learned* to see every refused extraction with

   its reason.

You can also do the main actions from the terminal:



.\.venv\Scripts\python.exe -m kivi apply --asr "ask aditya to review the sarvam kiwi service"

.\.venv\Scripts\python.exe -m kivi apply --formatted "I ate a kiwi on the flight."

.\.venv\Scripts\python.exe -m kivi memories

.\.venv\Scripts\python.exe -m kivi memory 1          # evidence + full audit trail

.\.venv\Scripts\python.exe -m kivi decision 1        # replay a stored decision

.\.venv\Scripts\python.exe -m kivi observe --formatted "..." --edited "..."

.\.venv\Scripts\python.exe -m kivi stats



## 8. Run the Tests and Evaluation



.\.venv\Scripts\python.exe -m kivi eval --split both



You can also use make eval.

Runs the full system and three baselines over both splits. Takes a few seconds and makes

no network calls unless a key is configured. Also available:



.\.venv\Scripts\python.exe -m kivi eval --split dev --system kivi

.\.venv\Scripts\python.exe -m kivi eval --split holdout



Run the test suite too (154 tests, ~1.5 s):



.\.venv\Scripts\python.exe -m pytest



## 9. Where the Results Are Saved

Everything lands in eval/results/, and the committed copies are the ones produced by

the command above:

| File | Contents |

|---|---|

| report.md | the readable report: composition, metrics, baseline comparison, latency, storage |

| summary.json | every metric as data, plus the environment the numbers came from |

| cases-\<split>-\<system>.jsonl | one row per case: inputs, expected, actual, relevant memory state, decision reason, latency |

| failures-\<split>.md | every failing case in full, with the system's own reasoning |

| eval-\<split>.db | the SQLite database the run built, left behind for inspection |

To inspect an individual case:



.\.venv\Scripts\python.exe -c "

import json

for line in open('eval/results/cases-dev-kivi.jsonl'):

    r = json.loads(line)

    if r['case_id'] == 'neg-fruit-01':

        print(json.dumps(r, indent=2))"



Or query the evaluation database directly:



sqlite3 eval/results/eval-dev.db \\

  "SELECT action, reason_code, span_text, context_score, required_context

   FROM decision_candidates ORDER BY id LIMIT 20;"



## 10. Optional Sarvam API Key

The system is fully functional and fully evaluable with no key. A key adds two modes,

both reported separately so it is always clear which numbers came from where:

- KIVI_USE_LLM_ADJUDICATOR=1 — the LLM adjudicates only the spans whose context score

  sits inside an uncertain band around the bar. Confident cases never reach it.

- KIVI_APPLY_MODE=prompt — retrieved memories are placed into the formatting prompt and

  the model writes the final text (the path the brief hints at).

Architecture note: Sarvam is used selectively for uncertain cases, while deterministic
rules remain responsible for the final memory application. The LLM is an adjudication layer,
not a free-form rewriting engine and not a source of durable memory. A live spot-check confirmed
one Sarvam call on an uncertain request while the final decision remained mode=deterministic;
the call recorded 210 input tokens, 80 output tokens, about 1.65 seconds of latency, and
₹0.012005 cost.

To enable:



cp .env.example .env

\# then set exactly one variable:

\#   SARVAM_API_KEY=sk_xxxxxxxx

.\.venv\Scripts\python.exe -m kivi check          # verifies the key with one tiny live call
To verify the optional adjudicator without running the full evaluation, use one uncertain case:

.\.venv\Scripts\python.exe -m kivi apply --formatted "Please check the Cuban Eighties deployment."

Look for adjudication_ms and model usage with calls: 1. The decision should still report
mode=deterministic, showing that Sarvam adjudicated the uncertainty while deterministic rules
remained responsible for the final application. This live spot-check uses API credits.



The variable is named SARVAM_API_KEY and nothing else is required. Get one at

<https://dashboard.sarvam.ai>. Cost is computed from Sarvam's published per-token prices

and reported in rupees in decisions.llm_cost_inr and in the evaluation report.

The .env file is ignored by git, so the key should not be committed.

## 11. Reset the Project



.\.venv\Scripts\python.exe -m kivi reset --reseed     # clear everything, replay the seed

.\.venv\Scripts\python.exe -m kivi reset              # clear everything, leave memory empty



Or: make reset · or in the interface: Reset + reseed / Wipe empty

· or over HTTP: curl -X POST localhost:8000/api/reset -d '{"reseed":true}' -H 'Content-Type: application/json'

Reset deletes every application row in foreign-key-safe order and resets the

AUTOINCREMENT counters, so a reset followed by a reseed reproduces **identical memory

ids and confidences**. That is what makes the guided journey repeatable. The schema and

the applied-migrations table are left intact.

To completely start over, including the database file:



make clean && make seed



---

## If Something Goes Wrong

| Symptom | Cause and fix |

|---|---|

| python3 not found | Make sure Python 3.10+ is installed, then use py on Windows. |

| RuntimeError: Kivi needs Python 3.10 or newer | Delete .venv, recreate it with Python 3.10+, and reinstall the dependencies. |

| TypeError: Unable to evaluate type annotation 'str \| None' | Same cause, seen if the guard is bypassed. Python is older than 3.10. |

| Missing vendored lexicon .../en_ordinary_words.txt | The checkout is incomplete. Both files under data/lexicon/ are committed and required. |

| KIVI_APPLY_MODE=prompt needs a model key | Either set SARVAM_API_KEY in .env, or use the default deterministic mode. |

| Port 8000 in use | .\.venv\Scripts\python.exe -m uvicorn kivi.api:app --port 8848 (any port). |

| Memory list is empty | Run .\.venv\Scripts\python.exe -m kivi seed, or press Seed in the interface. |