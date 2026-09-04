-- Evaluator fields on categories + evaluation results

ALTER TABLE pa_categories
    ADD COLUMN IF NOT EXISTS purpose TEXT,
    ADD COLUMN IF NOT EXISTS prompt TEXT,
    ADD COLUMN IF NOT EXISTS examples TEXT,
    ADD COLUMN IF NOT EXISTS evaluation_metrics JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE;

CREATE TABLE IF NOT EXISTS pa_post_evaluations (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES pa_reddit_discovered_posts (id),
    category_id INTEGER NOT NULL REFERENCES pa_categories (id),
    scores JSONB NOT NULL,
    mean_score DOUBLE PRECISION NOT NULL,
    reason TEXT,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    job_id INTEGER REFERENCES pa_ingestion_jobs (id),
    UNIQUE (post_id, category_id)
);
