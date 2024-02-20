CREATE SCHEMA IF NOT EXISTS openai;

CREATE TABLE IF NOT EXISTS openai.threads
(
    id         text PRIMARY KEY UNIQUE,
    metadata_info   JSON,
    expired_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '30 minutes',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

