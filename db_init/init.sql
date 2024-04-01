CREATE SCHEMA IF NOT EXISTS openai;

CREATE TABLE IF NOT EXISTS openai.threads
(
    id         text PRIMARY KEY UNIQUE,
    metadata_info   JSON,
    expired_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '10 minutes',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS openai.tokens
(
    access_token    TEXT PRIMARY KEY UNIQUE,
    refresh_token   TEXT,
    token_type      TEXT,
    expires_in      NUMERIC,
    scope           TEXT,
    expires_at      TIMESTAMP WITH TIME ZONE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
