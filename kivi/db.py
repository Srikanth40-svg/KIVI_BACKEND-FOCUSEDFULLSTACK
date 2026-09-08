"""SQLite access and a small real migrator.

Why SQLite: a single person's word memory has no concurrency story that needs a server,
the brief blesses embedded databases, and choosing it removes a native build step and a
running service from the reviewer's path. Foreign keys and WAL are on.

Why hand-rolled migrations instead of Alembic: there is exactly one schema file and the
migrator is ~30 lines. Adding a migration framework would be complexity that has not
earned its place (RULE 16).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False because the API serves sync endpoints from a threadpool.
    # Each thread still gets its OWN connection (see kivi/api.py): sharing one across
    # threads is what SQLite actually forbids, and WAL plus a busy timeout is what makes
    # several connections to one file safe.
    conn = sqlite3.connect(
        str(path), isolation_level=None, check_same_thread=False
    )  # autocommit; transactions are managed explicitly
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version    TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )


def applied_versions(conn: sqlite3.Connection) -> set[str]:
    _ensure_migrations_table(conn)
    return {r["version"] for r in conn.execute("SELECT version FROM schema_migrations")}


def migration_files() -> list[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def migrate(conn: sqlite3.Connection) -> list[str]:
    """Apply every unapplied migration in filename order. Returns versions applied."""
    done = applied_versions(conn)
    newly: list[str] = []
    for path in migration_files():
        version = path.stem
        if version in done:
            continue
        sql = path.read_text(encoding="utf-8")
        # DDL in SQLite is transactional, so a broken migration must leave no partial
        # schema. The BEGIN/COMMIT has to live INSIDE the script: executescript() commits
        # any open transaction before it runs, so wrapping the call in conn.execute("BEGIN")
        # silently leaves the DDL unprotected.
        escaped = version.replace("'", "''")
        script = (
            "BEGIN;\n"
            f"{sql}\n"
            f"INSERT INTO schema_migrations (version) VALUES ('{escaped}');\n"
            "COMMIT;\n"
        )
        try:
            conn.executescript(script)
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        newly.append(version)
    return newly


# Order matters: children before parents so FK constraints hold during a reset.
_RESET_ORDER = [
    "eval_results",
    "eval_runs",
    "decision_candidates",
    "decisions",
    "learning_decisions",
    "memory_events",
    "memory_evidence",
    "memory_variants",
    "word_memories",
    "interactions",
]


def reset(conn: sqlite3.Connection) -> dict[str, int]:
    """Delete all application data, keeping the schema. Deterministic (§36).

    Returns rows deleted per table so the reviewer can see it actually happened.
    """
    deleted: dict[str, int] = {}
    conn.execute("BEGIN")
    try:
        for table in _RESET_ORDER:
            before = conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            conn.execute(f"DELETE FROM {table}")
            deleted[table] = before
        # Reset AUTOINCREMENT counters so a reset+replay produces identical ids,
        # which is what makes the whole journey reproducible.
        conn.execute("DELETE FROM sqlite_sequence")
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    return deleted


def storage_stats(conn: sqlite3.Connection, db_path: str | Path) -> dict[str, Any]:
    """Database growth, measured rather than guessed (R12)."""
    page_count = conn.execute("PRAGMA page_count").fetchone()[0]
    page_size = conn.execute("PRAGMA page_size").fetchone()[0]
    counts = {t: conn.execute(f"SELECT COUNT(*) AS n FROM {t}").fetchone()["n"] for t in _RESET_ORDER}
    file_bytes = Path(db_path).stat().st_size if Path(db_path).exists() else 0
    return {
        "file_bytes": file_bytes,
        "page_bytes": page_count * page_size,
        "page_count": page_count,
        "page_size": page_size,
        "row_counts": counts,
    }


def query(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
    return list(conn.execute(sql, tuple(params)))


def query_one(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
    return conn.execute(sql, tuple(params)).fetchone()


def insert(conn: sqlite3.Connection, table: str, values: dict[str, Any]) -> int:
    cols = ", ".join(values)
    marks = ", ".join("?" for _ in values)
    cur = conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", tuple(values.values()))
    return int(cur.lastrowid)


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]
