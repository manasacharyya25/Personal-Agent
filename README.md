# Personal Agent

Phase 1 scope lives in `Implementation/Phase1.md`.

Learning experiments from FastAPI / RAG are archived in `source/` and still exist at the repo root until we remove them. Do not treat root `main.py` as the product entrypoint.

## Phase 1 layout

- `apps/agent` — FastAPI (dashboard API + per-post chat)
- `apps/extraction` — Reddit scraper
- `apps/evaluator` — lead + job matching
- `knowledge/` — RhoQ, ThoughtSpace, personal skills
- `dashboard/frontend` — React UI
- `ingestion/` — chunk / embed knowledge docs
