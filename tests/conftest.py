"""Shared fixtures.

Every test gets its own database file, so no test can see another's state and the whole
suite is order-independent.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

# The API module reads configuration at import/startup time, so the database location has
# to be set before anything from `kivi` is imported.
_TMP = Path(tempfile.mkdtemp(prefix="kivi-tests-"))
os.environ.setdefault("KIVI_DB_PATH", str(_TMP / "api.db"))
os.environ.setdefault("KIVI_APPLY_MODE", "deterministic")
os.environ.setdefault("KIVI_USE_LLM_ADJUDICATOR", "0")
# A key in the developer's real .env must not turn these tests into live network calls.
os.environ["SARVAM_API_KEY"] = ""

from kivi import db, learning, memory as mem_mod  # noqa: E402
from kivi.config import Config, Thresholds, load_config  # noqa: E402
from kivi.seed import load_seed, replay_seed  # noqa: E402


@pytest.fixture
def config(tmp_path: Path) -> Config:
    cfg = load_config()
    return Config(
        db_path=tmp_path / "kivi.db",
        llm_api_key=None,
        llm_model=cfg.llm_model,
        llm_base_url=cfg.llm_base_url,
        llm_timeout_s=cfg.llm_timeout_s,
        apply_mode="deterministic",
        use_llm_adjudicator=False,
        thresholds=Thresholds(),
    )


@pytest.fixture
def conn(config: Config):
    connection = db.connect(config.db_path)
    db.migrate(connection)
    yield connection
    connection.close()


@pytest.fixture
def th(config: Config) -> Thresholds:
    return config.thresholds


@pytest.fixture
def seeded(conn, config):
    """The committed seed, replayed through the real learning policy."""
    replay_seed(conn, config, load_seed())
    return conn


@pytest.fixture
def observe(conn, th):
    def _observe(**kwargs):
        return learning.ingest_observation(conn, th=th, **kwargs)

    return _observe


@pytest.fixture
def find(conn):
    from kivi.text import normalize_key

    def _find(canonical: str):
        row = db.query_one(
            conn,
            "SELECT * FROM word_memories WHERE normalized_key = ? ORDER BY id DESC LIMIT 1",
            (normalize_key(canonical),),
        )
        return db.row_to_dict(row)

    return _find


@pytest.fixture
def apply_text(conn, config):
    from kivi import pipeline

    def _apply(formatted: str, **kwargs):
        return pipeline.memory_aware_format(conn, config, formatted_text=formatted, **kwargs)

    return _apply
