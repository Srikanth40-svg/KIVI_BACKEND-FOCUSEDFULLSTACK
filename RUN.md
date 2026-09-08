# How to Run Kivi

---

## Live Demo

A deployed version is available for convenience:

https://kivibackend-focusedfullstack-production.up.railway.app/

The live deployment is **not the primary review method**. The local checkout described below is the authoritative way to run and evaluate the submission.

---

## Quick Start

From a clean clone of the repository:

### 1. Create the virtual environment

On Windows:

```powershell
py -3.12 -m venv .venv
```

On macOS/Linux:

```bash
python3.12 -m venv .venv
```

Python **3.10 or newer** is required. Python 3.11+ is recommended.

### 2. Install dependencies

Windows:

```powershell
.\.venv\Scripts\pip.exe install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements.txt
```

macOS/Linux:

```bash
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

### 3. Initialize the database

Windows:

```powershell
.\.venv\Scripts\python.exe -m kivi migrate
.\.venv\Scripts\python.exe -m kivi seed
```

macOS/Linux:

```bash
.venv/bin/python -m kivi migrate
.venv/bin/python -m kivi seed
```

### 4. Start the application

Windows:

```powershell
.\.venv\Scripts\python.exe -m uvicorn kivi.api:app --port 8000
```

macOS/Linux:

```bash
.venv/bin/python -m uvicorn kivi.api:app --port 8000
```

Then open:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

### 5. Run the complete evaluation

Windows:

```powershell
.\.venv\Scripts\python.exe -m kivi eval --split both
```

macOS/Linux:

```bash
.venv/bin/python -m kivi eval --split both
```

### 6. Run the test suite

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS/Linux:

```bash
.venv/bin/python -m pytest
```

The repository contains **154 tests**.

---

## What the Reviewer Should Verify

The main review flow is:

```text
Clean checkout
     ↓
Install dependencies
     ↓
Initialize SQLite database
     ↓
Replay seed observations
     ↓
Start local application
     ↓
Open http://localhost:8000
     ↓
Run Guided Journey
     ↓
Run tests
     ↓
Run evaluation
```

The Guided Journey demonstrates the important behaviour of Kivi, including:

- Learning personal vocabulary
- Retrieving learned memories
- Applying corrections when context supports them
- Leaving ordinary words unchanged
- Handling similar names and words
- Handling multi-token mishearings
- Showing why a correction was made
- Showing why a correction was rejected
- Inspecting memory evidence and history

---

## Expected Example

The main example from the brief should produce:

```text
ASR output
ask aditya to review the sarvam kiwi service

Formatted
Ask Aditya to review the Sarvam Kiwi service.

Memory-aware
Ask Aaditya to review the Sarvam Kivi service.
```

A key non-intervention case is:

```text
I ate a kiwi on the flight.
```

This should remain unchanged because the context does not provide enough evidence to replace the ordinary English word `kiwi` with the learned personal word `Kivi`.

---

## Environment Variables

No environment variables are required for the primary review path.

The default configuration is:

| Variable | Default | Purpose |
|---|---|---|
| `KIVI_DB_PATH` | `./kivi.db` | SQLite database location |
| `KIVI_APPLY_MODE` | `deterministic` | Default final application mode |
| `KIVI_USE_LLM_ADJUDICATOR` | `0` | LLM adjudication disabled by default |
| `SARVAM_API_KEY` | Empty | Optional Sarvam API key |
| `KIVI_LLM_MODEL` | `sarvam-105b` | Optional model |
| `KIVI_LLM_BASE_URL` | `https://api.sarvam.ai/v1` | Optional API endpoint |

The primary review path intentionally uses the deterministic configuration so that the submission can be evaluated without credentials or external API access.

---

## Optional Sarvam Features

A Sarvam API key is **not required** to verify the main submission.

If a key is available, the optional LLM features can be tested separately.

### LLM adjudication

```text
KIVI_USE_LLM_ADJUDICATOR=1
```

The LLM is only used for uncertain cases.

### Prompt mode

```text
KIVI_APPLY_MODE=prompt
```

This enables the optional model-assisted formatting path.

The deterministic configuration remains the default and is the configuration used for the primary local review.

---

## Evaluation

Run:

```bash
python -m kivi eval --split both
```

The evaluation runs the Kivi system and the baselines over the development and holdout splits.

Results are written to:

```text
eval/results/
```

Important files include:

```text
eval/results/report.md
eval/results/summary.json
eval/results/cases-dev-kivi.jsonl
eval/results/cases-holdout-kivi.jsonl
eval/results/failures-dev.md
eval/results/failures-holdout.md
```

The evaluation does not require a model key in the default configuration.

---

## Resetting the Database

To reset and replay the seed:

```bash
python -m kivi reset --reseed
```

To clear the memory completely:

```bash
python -m kivi reset
```

A reset followed by a reseed produces deterministic memory IDs and confidence values, making the Guided Journey reproducible.

---

## If Something Goes Wrong

| Problem | Fix |
|---|---|
| Python version is too old | Use Python 3.10 or newer and recreate `.venv` |
| Dependencies are missing | Run `pip install -r requirements.txt` again |
| Memory list is empty | Run `python -m kivi seed` |
| Port 8000 is already in use | Start Uvicorn with another port, for example `--port 8848` |
| Prompt mode asks for an API key | Return to the default deterministic mode or configure `SARVAM_API_KEY` |
| Database is in a bad state | Run `python -m kivi reset --reseed` |

---

