# Kivi phonetic memory.
#
# Every target here is also written out as a plain command in RUN.md, so a reviewer who
# would rather not use make is never blocked by it.

# Pick a Python that is actually new enough. Trusting plain `python3` is a trap: macOS
# ships 3.9 as `python3`, which builds a venv that installs fine and then fails at runtime.
# Override with `make PY=/path/to/python3.12 ...` if this guess is wrong.
PY ?= $(shell command -v python3.13 || command -v python3.12 || command -v python3.11 \
        || command -v python3.10 || command -v python3)
VENV := .venv
BIN := $(VENV)/bin
PORT ?= 8000

.PHONY: help install migrate seed reset run eval test check clean dataset all

help:
	@echo "make install   create .venv and install dependencies"
	@echo "make migrate   create/upgrade the SQLite database"
	@echo "make seed      replay the committed seed observations"
	@echo "make run       start the app (API + demo interface) on port $(PORT)"
	@echo "make eval      run the evaluation on dev + holdout, write eval/results/"
	@echo "make test      run the test suite"
	@echo "make check     validate configuration (and credentials, if any)"
	@echo "make reset     clear all data and replay the seed"
	@echo "make dataset   regenerate the evaluation dataset from eval/build_dataset.py"
	@echo "make all       install + migrate + seed + test + eval"

$(BIN)/python:
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --quiet --upgrade pip
	$(BIN)/pip install --quiet -r requirements.txt

install: $(BIN)/python
	@echo "installed into $(VENV)"

migrate: install
	$(BIN)/python -m kivi migrate

seed: migrate
	$(BIN)/python -m kivi seed

reset: install
	$(BIN)/python -m kivi reset --reseed

run: install
	$(BIN)/python -m uvicorn kivi.api:app --reload --port $(PORT)

eval: install
	$(BIN)/python -m kivi eval --split both

test: install
	$(BIN)/python -m pytest

check: install
	$(BIN)/python -m kivi check

dataset: install
	$(BIN)/python eval/build_dataset.py

all: install migrate seed test eval

clean:
	rm -f kivi.db kivi.db-wal kivi.db-shm
	rm -f eval/results/*.db eval/results/*.db-wal eval/results/*.db-shm
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache
