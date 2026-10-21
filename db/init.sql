-- Call logs. Each row stores the full transcript JSON (schemas/transcript.schema.json).
CREATE TABLE IF NOT EXISTS calls (
    call_id         TEXT PRIMARY KEY,
    prompt_version  TEXT NOT NULL,
    mode            TEXT NOT NULL CHECK (mode IN ('text', 'voice')),
    customer_phone  TEXT NOT NULL,
    outcome         TEXT NOT NULL,
    started_at      TIMESTAMPTZ NOT NULL,
    ended_at        TIMESTAMPTZ,
    transcript      JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS calls_outcome_idx ON calls (outcome);
CREATE INDEX IF NOT EXISTS calls_prompt_version_idx ON calls (prompt_version);
