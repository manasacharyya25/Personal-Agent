-- Phase 1 Reddit ingestion (2026-08-29)

CREATE TABLE IF NOT EXISTS pa_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pa_reddit_sources (
    id SERIAL PRIMARY KEY,
    subreddit TEXT NOT NULL UNIQUE,
    category_id INTEGER NOT NULL REFERENCES pa_categories (id),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 0,
    added_by TEXT,
    last_seen_post_id TEXT,
    last_seen_created_at TIMESTAMPTZ,
    pagination_state JSONB,
    last_scanned_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS pa_reddit_search_queries (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    time_filter TEXT NOT NULL DEFAULT 'week',
    category_id INTEGER NOT NULL REFERENCES pa_categories (id),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 0,
    added_by TEXT,
    last_seen_post_id TEXT,
    last_seen_created_at TIMESTAMPTZ,
    pagination_state JSONB,
    last_scanned_at TIMESTAMPTZ,
    UNIQUE (query, time_filter)
);

CREATE TABLE IF NOT EXISTS pa_ingestion_jobs (
    id SERIAL PRIMARY KEY,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    last_error TEXT,
    posts_seen INTEGER NOT NULL DEFAULT 0,
    posts_inserted INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pa_reddit_discovered_posts (
    id SERIAL PRIMARY KEY,
    reddit_post_id TEXT NOT NULL UNIQUE,
    subreddit TEXT,
    author TEXT,
    title TEXT,
    body TEXT,
    url TEXT,
    created_at TIMESTAMPTZ,
    metadata JSONB,
    first_discovered_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pa_reddit_post_discovery_method (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES pa_reddit_discovered_posts (id),
    discovery_method TEXT NOT NULL,
    discovery_query TEXT NOT NULL,
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    job_id INTEGER REFERENCES pa_ingestion_jobs (id),
    UNIQUE (post_id, discovery_method, discovery_query)
);

INSERT INTO pa_categories (name)
VALUES ('RhoQ'), ('ThoughtSpace'), ('Job'), ('AI')
ON CONFLICT (name) DO NOTHING;

-- Example sources / searches (edit or insert your own):
-- INSERT INTO pa_reddit_sources (subreddit, category_id, added_by)
-- SELECT 'fitness', id, 'seed' FROM pa_categories WHERE name = 'RhoQ'
-- ON CONFLICT (subreddit) DO NOTHING;
--
-- INSERT INTO pa_reddit_search_queries (query, time_filter, category_id, added_by)
-- SELECT 'fitness community', 'week', id, 'seed' FROM pa_categories WHERE name = 'RhoQ'
-- ON CONFLICT (query, time_filter) DO NOTHING;
