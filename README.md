# Personal Agent

Phase 1 scope lives in `Implementation/Phase1.md`.

Learning experiments from FastAPI / RAG are archived in `source/` and still exist at the repo root until we remove them. Do not treat root `main.py` as the product entrypoint.

## Phase 1 layout

- `apps/agent` — FastAPI (dashboard API + per-post chat)
- `apps/extraction` — Reddit scraper (Playwright)
- `apps/evaluator` — lead + job matching
- `knowledge/` — RhoQ, Thoughtspace, personal skills
- `dashboard/frontend` — React UI
- `ingestion/` — chunk / embed knowledge docs

Scraper design: `Implementation/phase1-2026-08-29.md`

## Reddit scraper

Copy `.env.example` to `.env` and set `DB_CONNECTION_STRING`.

```text
pip install -e .
playwright install chromium
python -m apps.extraction.main --migrate
```

Insert at least one row into `pa_reddit_sources` or `pa_reddit_search_queries`, then:

```text
python -m apps.extraction.main
```

