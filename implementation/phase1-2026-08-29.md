# Phase 1 — 2026-08-29 — Reddit scraper

This note captures the scraper design we locked in. It does not replace `Phase1.md` (overall slice). Evaluator, knowledge ingest, and the chat dashboard are still later.

**Stack for this piece:** Playwright (Chromium) + Postgres. The bot stores everything it sees. It does not score relevance.

## Tables (`pa_` prefix)

| Table | Role |
|---|---|
| `pa_categories` | Labels: RhoQ, ThoughtSpace, Job, AI (add/remove later in UI) |
| `pa_reddit_sources` | Subreddits to scan. **One** `category_id`. Checkpoints on this row. |
| `pa_reddit_search_queries` | Keyword searches. **One** `category_id`. Same checkpoint columns. |
| `pa_reddit_discovered_posts` | One row per Reddit post. `unique(reddit_post_id)` |
| `pa_reddit_post_discovery_method` | How that post was found. Same post can be found by many subreddits/searches. |
| `pa_ingestion_jobs` | One row per run. `job_type` starts as `reddit`; later other sources share this table. |

No join tables. A source or search query has a single category.

### Checkpoints (on each source and each search query)

- `last_seen_post_id`
- `last_seen_created_at`
- `pagination_state` (jsonb, next page + newest post seen this run)
- `last_scanned_at`

If the process crashes, the next run resumes from checkpoint / pagination instead of starting over. Re-inserts are harmless.

### Job status (`pa_ingestion_jobs`)

`pending` → `running` → `completed` | `failed`

Plus `started_at`, `completed_at`, `last_error` so a later dashboard can show e.g. “Reddit ingestion failed 8 minutes ago because Chromium crashed.”

## Discovery

1. **Subreddit scan** — active rows in `pa_reddit_sources` (e.g. `/new`).
2. **Keyword search** — active rows in `pa_reddit_search_queries`, with a time filter.

Each find writes:

1. `INSERT` into `pa_reddit_discovered_posts` … `ON CONFLICT (reddit_post_id) DO NOTHING`
2. `INSERT` into `pa_reddit_post_discovery_method` … `ON CONFLICT DO NOTHING` (post + method + query)

## Scraper rules (must-have)

- **Checkpointing** — per subreddit and per search; resume after crash
- **Dedup** — unique Reddit post id; multiple discoveries still recorded
- **Idempotency** — running the same job twice is a no-op for existing rows
- **Pagination** — do not assume one page; store next-page state
- **Rate limiting** — delay between requests; no parallel Chromium tabs
- **Retries** — network/page failures, bounded (not an infinite loop)
- **Browser lifecycle** — start browser → run job → close browser

Playwright only. No official Reddit API for this bot.

## How to run

```text
pip install -e .
playwright install chromium
python -m apps.extraction.main --migrate
```

Add a subreddit (categories are seeded: RhoQ, ThoughtSpace, Job, AI):

```sql
INSERT INTO pa_reddit_sources (subreddit, category_id, added_by)
SELECT 'fitness', id, 'manual' FROM pa_categories WHERE name = 'RhoQ';
```

Then: `python -m apps.extraction.main`

## Out of this file

- Dashboard to CRUD categories/subreddits (later)
- Evaluator / agent chat
- Actually posting on Reddit
