-- Wastelessia backend schema (PRD §5)

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()

-- Projects: maps an API key (proj_xxx) to a project_id.
CREATE TABLE IF NOT EXISTS projects (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  api_key     TEXT NOT NULL UNIQUE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Events: one row per tracked LLM call.
CREATE TABLE IF NOT EXISTS events (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id   UUID NOT NULL REFERENCES projects(id),
  timestamp    TIMESTAMPTZ NOT NULL,
  model        TEXT NOT NULL,
  tokens_in    INTEGER NOT NULL,
  tokens_out   INTEGER NOT NULL,
  cost_usd     NUMERIC(10, 6) NOT NULL,
  duration_ms  INTEGER,
  success      BOOLEAN NOT NULL DEFAULT TRUE,
  tag_team     TEXT,
  tag_feature  TEXT,
  tag_env      TEXT,
  tag_client   TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_project_timestamp ON events (project_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_events_tags ON events (project_id, tag_team, tag_feature);
