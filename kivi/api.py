"""HTTP API, and the single process that also serves the demo interface.

One process, no build step, no second server: the reviewer runs one command. Every route
returns the reasoning alongside the result, because "understand why the system did or did
not intervene" is a requirement of the brief, not a debug feature.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db
from . import learning
from . import memory as mem_mod
from . import pipeline
from .config import Config, ConfigError, load_config
from .formatter import format_stub
from .llm import SarvamClient
from .lexicon import stats as lexicon_stats

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

_state: dict[str, Any] = {}


def get_config() -> Config:
    return _state["config"]


_tls = threading.local()


def get_conn() -> sqlite3.Connection:
    """One SQLite connection per worker thread.

    FastAPI runs sync endpoints in a threadpool, and a single shared connection raises
    "SQLite objects created in a thread can only be used in that same thread". Rather than
    serialising every request behind a global lock, each thread opens its own connection to
    the same file; WAL mode plus PRAGMA busy_timeout makes that safe for one writer and
    many readers, which is exactly this application's shape.
    """
    conn = getattr(_tls, "conn", None)
    if conn is None:
        conn = db.connect(get_config().db_path)
        _tls.conn = conn
    return conn


def get_client() -> SarvamClient | None:
    return _state.get("client")


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    conn = db.connect(config.db_path)
    applied = db.migrate(conn)
    _state["config"] = config
    _state["conn"] = conn
    if applied:
        print(f"[kivi] applied migrations: {', '.join(applied)}")
    if config.llm_available:
        _state["client"] = SarvamClient(config)
        print(f"[kivi] Sarvam client configured (model={config.llm_model})")
    else:
        print("[kivi] no SARVAM_API_KEY: running fully deterministic (this is a supported mode)")
    print(f"[kivi] db={config.db_path}")
    yield
    client = _state.get("client")
    if client:
        client.close()
    conn.close()


app = FastAPI(
    title="Kivi phonetic memory",
    version="0.1.0",
    description="The words Kivi keeps: learning, retrieving and applying one person's vocabulary.",
    lifespan=lifespan,
)


@app.exception_handler(ConfigError)
async def _config_error(_request, exc: ConfigError):
    return JSONResponse(status_code=500, content={"error": "configuration", "detail": str(exc)})


# ----------------------------------------------------------------------------------------
# Schemas
# ----------------------------------------------------------------------------------------

WordType = Literal[
    "person", "org", "product", "project", "term", "acronym", "handle", "place", "preference"
]


class ObservationIn(BaseModel):
    """One thing that happened, from which the system may or may not learn.

    At least one text field is required. `user_edited_text` is the strongest signal there
    is: it means the person fixed our output.
    """

    asr_text: str | None = None
    formatted_text: str | None = None
    user_edited_text: str | None = None
    app_context: str | None = Field(
        default=None,
        description="Window title / surface the person was dictating into, "
                    "e.g. 'Slack - #kivi-eng'. Weak corroborating evidence only.",
    )
    user_id: str = "default"


class FormatIn(BaseModel):
    asr_text: str


class MemoryAwareIn(BaseModel):
    formatted_text: str | None = None
    asr_text: str | None = None
    app_context: str | None = None
    user_id: str = "default"
    apply_mode: Literal["deterministic", "prompt"] | None = None
    learn_from_this: bool = Field(
        default=False,
        description="Also treat this request as an observation to learn from. Off by "
                    "default so that evaluating the system cannot alter its own memory.",
    )


class MemoryIn(BaseModel):
    canonical_form: str = Field(min_length=1, max_length=120)
    word_type: WordType = "term"
    gloss: str | None = None
    observed_forms: list[str] = Field(
        default_factory=list,
        description="Known wrong forms, e.g. ['kiwi'] for canonical 'Kivi'.",
    )
    user_id: str = "default"


class MemoryPatch(BaseModel):
    canonical_form: str | None = None
    word_type: WordType | None = None
    gloss: str | None = None
    status: Literal["candidate", "confirmed"] | None = None


class ResetIn(BaseModel):
    reseed: bool = Field(default=False, description="Replay the committed seed observations after clearing.")


# ----------------------------------------------------------------------------------------
# Health / stats
# ----------------------------------------------------------------------------------------

@app.get("/api/health")
def health(check_model: bool = Query(False, description="Make one tiny live model call.")):
    config, conn = get_config(), get_conn()
    out: dict[str, Any] = {
        "status": "ok",
        "config": config.describe(),
        "migrations_applied": sorted(db.applied_versions(conn)),
        "lexicon": lexicon_stats(),
        "memory_counts": {
            row["status"]: row["n"]
            for row in db.query(
                conn, "SELECT status, COUNT(*) AS n FROM word_memories GROUP BY status"
            )
        },
    }
    if check_model:
        client = get_client()
        if client is None:
            out["model_check"] = {"ok": False, "detail": "SARVAM_API_KEY is not set"}
        else:
            result = client.health()
            out["model_check"] = {
                "ok": result.ok,
                "detail": result.error or (result.text or "").strip()[:80],
                "usage": result.usage.as_dict(),
            }
    return out


@app.get("/api/stats")
def stats():
    config, conn = get_config(), get_conn()
    return {
        "storage": db.storage_stats(conn, config.db_path),
        "decisions": db.row_to_dict(
            db.query_one(
                conn,
                """
                SELECT COUNT(*) AS decisions,
                       COALESCE(SUM(applied_count), 0)   AS applied,
                       COALESCE(SUM(abstained_count), 0) AS abstained,
                       COALESCE(SUM(noop_count), 0)      AS noop,
                       COALESCE(SUM(llm_calls), 0)       AS llm_calls,
                       COALESCE(SUM(llm_cost_inr), 0)    AS llm_cost_inr,
                       COALESCE(AVG(retrieval_ms), 0)    AS avg_retrieval_ms,
                       COALESCE(AVG(total_ms), 0)        AS avg_total_ms
                FROM decisions
                """,
            )
        ),
        "learning": {
            row["outcome"]: row["n"]
            for row in db.query(
                conn, "SELECT outcome, COUNT(*) AS n FROM learning_decisions GROUP BY outcome"
            )
        },
    }


# ----------------------------------------------------------------------------------------
# Observations and the three stages
# ----------------------------------------------------------------------------------------

@app.post("/api/observations")
def post_observation(body: ObservationIn):
    """Feed the system something that happened. Returns every learning decision, including refusals."""
    if not any([body.asr_text, body.formatted_text, body.user_edited_text]):
        raise HTTPException(422, "one of asr_text, formatted_text or user_edited_text is required")
    config, conn = get_config(), get_conn()
    outcome = learning.ingest_observation(
        conn,
        th=config.thresholds,
        asr_text=body.asr_text,
        formatted_text=body.formatted_text,
        user_edited_text=body.user_edited_text,
        app_context=body.app_context,
        user_id=body.user_id,
    )
    return {
        "interaction_id": outcome.interaction_id,
        "summary": outcome.summary(),
        "decisions": outcome.proposals,
    }


@app.post("/api/format")
def post_format(body: FormatIn):
    """Stage 2 only. A stand-in for Kivi's formatting LM; see kivi/formatter.py."""
    return {
        "asr_text": body.asr_text,
        "formatted_text": format_stub(body.asr_text),
        "note": "deterministic stand-in for Kivi's formatting model, not Kivi's formatter",
    }


@app.post("/api/memory-aware-format")
def post_memory_aware(body: MemoryAwareIn):
    """Stage 3: the memory-aware transcript, plus the full reasoning behind it."""
    if not body.formatted_text and not body.asr_text:
        raise HTTPException(422, "one of formatted_text or asr_text is required")
    config, conn = get_config(), get_conn()
    mode = body.apply_mode or config.apply_mode
    client = get_client()
    if mode == "prompt" and client is None:
        raise HTTPException(
            400,
            "apply_mode='prompt' needs SARVAM_API_KEY. Use 'deterministic', which needs no key.",
        )

    interaction_id: int | None = None
    if body.learn_from_this:
        outcome = learning.ingest_observation(
            conn, th=config.thresholds, asr_text=body.asr_text,
            formatted_text=body.formatted_text, app_context=body.app_context,
            user_id=body.user_id, kind="format_request",
        )
        interaction_id = outcome.interaction_id

    result = pipeline.memory_aware_format(
        conn, config,
        formatted_text=body.formatted_text,
        asr_text=body.asr_text,
        app_context=body.app_context,
        user_id=body.user_id,
        apply_mode=mode,
        client=client,
        interaction_id=interaction_id,
    )
    return pipeline.explain(result)


@app.get("/api/interactions")
def get_interactions(limit: int = Query(50, le=500)):
    conn = get_conn()
    return {
        "interactions": db.rows_to_dicts(
            db.query(conn, "SELECT * FROM interactions ORDER BY id DESC LIMIT ?", (limit,))
        )
    }


# ----------------------------------------------------------------------------------------
# Memory inspection and management
# ----------------------------------------------------------------------------------------

@app.get("/api/memories")
def get_memories(
    user_id: str = "default",
    status: str | None = None,
    word_type: str | None = None,
    search: str | None = None,
    limit: int = Query(500, le=1000),
):
    conn = get_conn()
    memories = mem_mod.list_memories(
        conn, user_id, status=status, word_type=word_type, search=search, limit=limit
    )
    return {"count": len(memories), "memories": memories}


@app.get("/api/memories/{memory_id}")
def get_memory(memory_id: int):
    """A memory with its variants, its evidence, and its full audit trail."""
    full = mem_mod.get_full(get_conn(), memory_id)
    if full is None:
        raise HTTPException(404, f"no memory {memory_id}")
    return full


@app.post("/api/memories", status_code=201)
def create_memory(body: MemoryIn):
    """Add a memory by hand. This is authoritative evidence (E3), so it starts confirmed."""
    config, conn = get_config(), get_conn()
    from .text import normalize_key

    if mem_mod.find_live(conn, body.user_id, normalize_key(body.canonical_form)):
        raise HTTPException(409, f"a live memory already exists for {body.canonical_form!r}")

    created = mem_mod.create(
        conn,
        canonical_form=body.canonical_form,
        word_type=body.word_type,
        evidence_type="manual_entry",
        th=config.thresholds,
        user_id=body.user_id,
        excerpt="added by hand in the memory inspector",
        gloss=body.gloss,
    )
    for form in body.observed_forms:
        if form.strip():
            mem_mod.add_variant(conn, int(created["id"]), form.strip(), kind="asr_error")
    return mem_mod.get_full(conn, int(created["id"]))


@app.patch("/api/memories/{memory_id}")
def patch_memory(memory_id: int, body: MemoryPatch):
    """Edit a memory. Changing the canonical form supersedes rather than overwrites."""
    config, conn = get_config(), get_conn()
    if mem_mod.get(conn, memory_id) is None:
        raise HTTPException(404, f"no memory {memory_id}")
    try:
        updated = mem_mod.update(
            conn, memory_id, th=config.thresholds,
            canonical_form=body.canonical_form, word_type=body.word_type,
            gloss=body.gloss, status=body.status,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return mem_mod.get_full(conn, int(updated["id"]))


@app.delete("/api/memories/{memory_id}")
def delete_memory(memory_id: int, reason: str = "deleted by the user"):
    """Soft delete: stops affecting output immediately, stays inspectable."""
    conn = get_conn()
    if mem_mod.get(conn, memory_id) is None:
        raise HTTPException(404, f"no memory {memory_id}")
    mem_mod.soft_delete(conn, memory_id, reason=reason)
    return mem_mod.get_full(conn, memory_id)


@app.post("/api/memories/{memory_id}/restore")
def restore_memory(memory_id: int):
    config, conn = get_config(), get_conn()
    if mem_mod.get(conn, memory_id) is None:
        raise HTTPException(404, f"no memory {memory_id}")
    mem_mod.restore(conn, memory_id, config.thresholds)
    return mem_mod.get_full(conn, memory_id)


# ----------------------------------------------------------------------------------------
# Why did it do that?
# ----------------------------------------------------------------------------------------

@app.get("/api/decisions")
def get_decisions(limit: int = Query(50, le=500)):
    conn = get_conn()
    return {
        "decisions": db.rows_to_dicts(
            db.query(conn, "SELECT * FROM decisions ORDER BY id DESC LIMIT ?", (limit,))
        )
    }


@app.get("/api/decisions/{decision_id}")
def get_decision(decision_id: int):
    """The complete trace: every span considered, every score, every gate, every reason."""
    trace = pipeline.decision_trace(get_conn(), decision_id)
    if trace is None:
        raise HTTPException(404, f"no decision {decision_id}")
    return trace


@app.get("/api/learning-decisions")
def get_learning_decisions(
    outcome: str | None = None,
    limit: int = Query(100, le=1000),
):
    """Why words were — and were not — learned."""
    conn = get_conn()
    sql = "SELECT * FROM learning_decisions"
    params: list[Any] = []
    if outcome:
        sql += " WHERE outcome = ?"
        params.append(outcome)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    return {"learning_decisions": db.rows_to_dicts(db.query(conn, sql, params))}


# ----------------------------------------------------------------------------------------
# Reset
# ----------------------------------------------------------------------------------------

@app.post("/api/reset")
def post_reset(body: ResetIn | None = None):
    """Deterministic reset to empty state, optionally replaying the committed seed."""
    from .seed import load_seed, replay_seed

    config, conn = get_config(), get_conn()
    body = body or ResetIn()
    deleted = db.reset(conn)
    seeded: dict[str, Any] | None = None
    if body.reseed:
        seeded = replay_seed(conn, config, load_seed())
    return {
        "status": "reset",
        "rows_deleted": deleted,
        "reseeded": seeded,
        "memory_count": db.query_one(conn, "SELECT COUNT(*) AS n FROM word_memories")["n"],
    }


# ----------------------------------------------------------------------------------------
# Static demo interface (mounted last so /api/* wins)
# ----------------------------------------------------------------------------------------

if WEB_DIR.exists():
    @app.get("/")
    def index():
        return FileResponse(WEB_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
