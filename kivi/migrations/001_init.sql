-- 001_init.sql — Kivi phonetic memory, initial schema.
--
-- Design note: the schema IS the design here, so it is hand-written SQL rather than
-- ORM models. Every table below exists because a requirement in docs/01-failure-taxonomy.md
-- or docs/02-design.md forces it; the comment on each says which.
--
-- Only two columns in the whole schema hold JSON, and both are noted inline with a reason.

-- ---------------------------------------------------------------------------
-- interactions — provenance. Every memory must point at the moment it came from
-- (RULE 4: every learned word has a reason), and every correction must be replayable.
-- ---------------------------------------------------------------------------
CREATE TABLE interactions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           TEXT    NOT NULL DEFAULT 'default',
    kind              TEXT    NOT NULL CHECK (kind IN ('observation', 'format_request', 'seed', 'eval')),
    asr_text          TEXT,               -- stage 1: raw ASR (an INPUT to this system; we do not build ASR)
    formatted_text    TEXT,               -- stage 2: after the formatting LM (input, or our stand-in formatter)
    memory_aware_text TEXT,               -- stage 3: what this system produced
    user_edited_text  TEXT,               -- if the user fixed our output: this is E2 evidence, the strongest ordinary-use signal
    -- app_context is the window title / surface string an OS client can actually supply,
    -- e.g. "Slack — #kivi-eng" or "VS Code — kivi-backend/README.md". Tokenised for E5
    -- (weak corroboration) only. One flat column, not a JSON bag, because we only ever
    -- treat it as a bag of words.
    app_context       TEXT,
    created_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX idx_interactions_user_created ON interactions (user_id, created_at);

-- ---------------------------------------------------------------------------
-- word_memories — the memory itself. A typed canonical SPAN (1..4 tokens), not a token:
-- forced by taxonomy A7 ("Aaditya Labs") and A8 ("sarvam kiwi").
-- ---------------------------------------------------------------------------
CREATE TABLE word_memories (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          TEXT    NOT NULL DEFAULT 'default',

    -- The exact output string. Case, punctuation and joining are DATA, not derivable
    -- (taxonomy A4 "OpenAI"/"GitHub", A9 "@aaditya_k").
    canonical_form   TEXT    NOT NULL,
    normalized_key   TEXT    NOT NULL,    -- case/punct/diacritic-folded; retrieval tier 1 (indexed)
    phonetic_key     TEXT    NOT NULL,    -- sound-alike code; retrieval tier 2 (indexed)
    token_count      INTEGER NOT NULL CHECK (token_count BETWEEN 1 AND 4),

    -- Gates context: a `person` memory and a `product` memory need different evidence
    -- to fire (taxonomy N1-N4). `preference` is taxonomy A11 — two valid spellings where
    -- only this user's choice exists.
    word_type        TEXT    NOT NULL CHECK (word_type IN
                       ('person','org','product','project','term','acronym','handle','place','preference')),

    -- Retrieval FILTERS on this. Deletion (N9), supersession (N10) and weak evidence (N11)
    -- must actually take effect, so status is a query predicate, not a display field.
    status           TEXT    NOT NULL CHECK (status IN ('candidate','confirmed','superseded','deleted')),
    confidence       REAL    NOT NULL CHECK (confidence BETWEEN 0.0 AND 1.0),

    gloss            TEXT,                -- one short description ("colleague at Sarvam"). The only free-text field.

    occurrence_count INTEGER NOT NULL DEFAULT 0,   -- E4 repetition evidence needs counts...
    first_seen       TEXT,
    last_seen        TEXT,                          -- ...across SEPARATE interactions

    superseded_by    INTEGER REFERENCES word_memories (id) ON DELETE SET NULL,  -- history, not destruction (§13)

    created_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at       TEXT
);
-- Uniqueness applies only to LIVE memories, so a superseded/deleted row can keep its
-- old form on record without blocking a new memory for the same word.
CREATE UNIQUE INDEX idx_memories_live_unique
    ON word_memories (user_id, normalized_key, word_type)
    WHERE status IN ('candidate', 'confirmed');
CREATE INDEX idx_memories_norm   ON word_memories (user_id, normalized_key);
CREATE INDEX idx_memories_phon   ON word_memories (user_id, phonetic_key);
CREATE INDEX idx_memories_status ON word_memories (user_id, status);

-- ---------------------------------------------------------------------------
-- memory_variants — the forms a canonical has been observed AS.
-- A separate table, not a JSON column, because these are looked up BY INDEX on every
-- request and each carries its own count: a join key, not a payload.
-- ---------------------------------------------------------------------------
CREATE TABLE memory_variants (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id          INTEGER NOT NULL REFERENCES word_memories (id) ON DELETE CASCADE,
    variant_form       TEXT    NOT NULL,   -- as observed, surface preserved
    variant_normalized TEXT    NOT NULL,
    variant_phonetic   TEXT    NOT NULL,

    -- CRITICAL distinction, and the reason this column exists:
    --   'orthographic' — same referent, different spelling (grey/gray, Bengaluru/Bangalore).
    --                    Substitution is meaning-preserving, so it needs little context.
    --   'asr_error'    — the machine mis-heard; the variant denotes something ELSE
    --                    (kiwi vs Kivi). Substitution CHANGES meaning, so if the variant
    --                    is an ordinary English word it demands strong context (N1-N3).
    --   'alias'        — the user's own shorthand for the canonical.
    --   'canonical'    — the canonical itself, stored so lookup is uniform.
    kind               TEXT    NOT NULL CHECK (kind IN ('orthographic','asr_error','alias','canonical')),

    observation_count  INTEGER NOT NULL DEFAULT 0,
    first_seen         TEXT,
    last_seen          TEXT,
    created_at         TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (memory_id, variant_normalized)
);
CREATE INDEX idx_variants_norm ON memory_variants (variant_normalized);
CREATE INDEX idx_variants_phon ON memory_variants (variant_phonetic);
CREATE INDEX idx_variants_mem  ON memory_variants (memory_id);

-- ---------------------------------------------------------------------------
-- memory_evidence — WHY a memory exists. The evidence ladder E1-E8 (docs/02-design.md).
-- ---------------------------------------------------------------------------
CREATE TABLE memory_evidence (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id      INTEGER NOT NULL REFERENCES word_memories (id) ON DELETE CASCADE,
    interaction_id INTEGER REFERENCES interactions (id) ON DELETE SET NULL,
    evidence_type  TEXT    NOT NULL CHECK (evidence_type IN
                     ('manual_entry','user_spelling','user_edit','repetition',
                      'naming_frame','app_context','irrealis','llm_only')),
    evidence_class TEXT    NOT NULL CHECK (evidence_class IN
                     ('authoritative','corroborating','suggestive','weak','insufficient')),
    weight         REAL    NOT NULL,
    excerpt        TEXT,                  -- the exact words that constituted the evidence
    created_at     TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX idx_evidence_mem ON memory_evidence (memory_id);

-- ---------------------------------------------------------------------------
-- memory_events — append-only audit of every status/confidence movement, so
-- "why did confidence change" (§8) and "old state stays inspectable" (§13) are answerable.
-- ---------------------------------------------------------------------------
CREATE TABLE memory_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id       INTEGER NOT NULL REFERENCES word_memories (id) ON DELETE CASCADE,
    event           TEXT    NOT NULL CHECK (event IN
                      ('created','reinforced','promoted','demoted','updated',
                       'superseded','deleted','restored','variant_added')),
    from_status     TEXT,
    to_status       TEXT,
    from_confidence REAL,
    to_confidence   REAL,
    reason_code     TEXT    NOT NULL,
    reason_text     TEXT,
    evidence_id     INTEGER REFERENCES memory_evidence (id) ON DELETE SET NULL,
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX idx_events_mem ON memory_events (memory_id, created_at);

-- ---------------------------------------------------------------------------
-- learning_decisions — every extraction ATTEMPT and its outcome, including refusals.
-- Without this, "why was it NOT learned" is unanswerable and memory RECALL is unmeasurable.
-- ---------------------------------------------------------------------------
CREATE TABLE learning_decisions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id     INTEGER REFERENCES interactions (id) ON DELETE CASCADE,
    surface_form       TEXT    NOT NULL,   -- what was seen
    proposed_canonical TEXT,               -- what it would have become
    word_type          TEXT,
    evidence_type      TEXT,
    outcome            TEXT    NOT NULL CHECK (outcome IN
                         ('confirmed','candidate','reinforced','superseded','rejected')),
    reason_code        TEXT    NOT NULL,
    reason_text        TEXT,
    memory_id          INTEGER REFERENCES word_memories (id) ON DELETE SET NULL,
    created_at         TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX idx_learning_interaction ON learning_decisions (interaction_id);
CREATE INDEX idx_learning_outcome     ON learning_decisions (outcome);

-- ---------------------------------------------------------------------------
-- decisions — one row per memory-aware format request. Carries the honest cost/latency
-- numbers the brief asks to be measured (R12).
-- ---------------------------------------------------------------------------
CREATE TABLE decisions (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id        INTEGER REFERENCES interactions (id) ON DELETE CASCADE,
    apply_mode            TEXT    NOT NULL CHECK (apply_mode IN ('deterministic','prompt')),
    asr_text              TEXT,
    formatted_text        TEXT    NOT NULL,
    memory_aware_text     TEXT    NOT NULL,
    retrieval_ms          REAL    NOT NULL DEFAULT 0,
    adjudication_ms       REAL    NOT NULL DEFAULT 0,
    apply_ms              REAL    NOT NULL DEFAULT 0,
    total_ms              REAL    NOT NULL DEFAULT 0,
    spans_considered      INTEGER NOT NULL DEFAULT 0,
    candidates_considered INTEGER NOT NULL DEFAULT 0,
    applied_count         INTEGER NOT NULL DEFAULT 0,
    abstained_count       INTEGER NOT NULL DEFAULT 0,
    noop_count            INTEGER NOT NULL DEFAULT 0,
    llm_calls             INTEGER NOT NULL DEFAULT 0,
    llm_tokens_in         INTEGER NOT NULL DEFAULT 0,
    llm_tokens_out        INTEGER NOT NULL DEFAULT 0,
    llm_cost_inr          REAL    NOT NULL DEFAULT 0,
    created_at            TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX idx_decisions_interaction ON decisions (interaction_id);

-- ---------------------------------------------------------------------------
-- decision_candidates — the full retrieval trace: every span considered, every score,
-- every gate, and the reason for the action taken. This is §41 observability, and it
-- records NO-OPS and ABSTENTIONS too, because otherwise precision cannot be computed.
-- ---------------------------------------------------------------------------
CREATE TABLE decision_candidates (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id      INTEGER NOT NULL REFERENCES decisions (id) ON DELETE CASCADE,
    memory_id        INTEGER REFERENCES word_memories (id) ON DELETE SET NULL,
    span_text        TEXT    NOT NULL,
    span_start       INTEGER NOT NULL,
    span_end         INTEGER NOT NULL,
    span_token_count INTEGER NOT NULL,
    match_tier       TEXT    NOT NULL CHECK (match_tier IN ('exact','variant','phonetic','fuzzy','llm')),
    lexical_score    REAL    NOT NULL DEFAULT 0,
    phonetic_score   REAL    NOT NULL DEFAULT 0,
    context_score    REAL    NOT NULL DEFAULT 0,
    required_context REAL    NOT NULL DEFAULT 0,   -- the bar this span had to clear, and why it was set there
    final_score      REAL    NOT NULL DEFAULT 0,
    is_ordinary_word INTEGER NOT NULL DEFAULT 0,   -- the N1-N3 prior, from the vendored lexicon
    action           TEXT    NOT NULL CHECK (action IN ('applied','abstained','noop','blocked')),
    reason_code      TEXT    NOT NULL,
    reason_text      TEXT,
    -- Diagnostic breakdown of the individual context signals, for the "why" panel.
    -- JSON because it is a variable-shaped display payload that is never queried by key.
    signals          TEXT,
    created_at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX idx_dc_decision ON decision_candidates (decision_id);
CREATE INDEX idx_dc_action   ON decision_candidates (action);

-- ---------------------------------------------------------------------------
-- eval_runs / eval_results — evaluation is a first-class part of the assignment, so its
-- output is queryable state, not only files. Per-case rows keep inputs, expected, actual,
-- memory state and reason together (R10).
-- ---------------------------------------------------------------------------
CREATE TABLE eval_runs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    split        TEXT    NOT NULL,
    system       TEXT    NOT NULL,          -- 'kivi' or a named baseline
    config_json  TEXT    NOT NULL,
    n_cases      INTEGER NOT NULL DEFAULT 0,
    metrics_json TEXT,
    started_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    finished_at  TEXT
);

CREATE TABLE eval_results (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id         INTEGER NOT NULL REFERENCES eval_runs (id) ON DELETE CASCADE,
    case_id        TEXT    NOT NULL,
    category       TEXT    NOT NULL,
    passed         INTEGER NOT NULL,
    failure_class  TEXT,
    expected_text  TEXT,
    actual_text    TEXT,
    expected_action TEXT,
    actual_action  TEXT,
    reason_code    TEXT,
    memory_state   TEXT,                   -- JSON snapshot of the memories relevant to THIS case
    latency_ms     REAL,
    decision_id    INTEGER,
    created_at     TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX idx_eval_results_run  ON eval_results (run_id);
CREATE INDEX idx_eval_results_pass ON eval_results (run_id, passed);
