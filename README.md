# Personal Agent

Phase 1 scope lives in `Implementation/Phase1.md`.

Learning experiments from FastAPI / RAG are archived in `source/` and still exist at the repo root until we remove them. Do not treat root `main.py` as the product entrypoint.

## Phase 1 layout

- `apps/agent` — FastAPI (dashboard API + per-post chat)
- `apps/extraction` — Reddit scraper (Playwright)
- `apps/evaluator` — score posts against category criteria

Scraper: `Implementation/phase1-2026-08-29.md`  
Dashboard: `Implementation/phase1-dashboard.md`  
Evaluator: `Implementation/phase1-evaluator.md`
- `knowledge/` — RhoQ, Thoughtspace, personal skills
- `dashboard/frontend` — React UI
- `ingestion/` — chunk / embed knowledge docs

Scraper design: `Implementation/phase1-2026-08-29.md`  
Dashboard: `Implementation/phase1-dashboard.md`

## Reddit scraper

Copy `.env.example` to `.env` and set `DB_CONNECTION_STRING`.

```text
pip install -e .
playwright install chromium
python -m apps.extraction.main --migrate
python -m apps.extraction.main
```

## Dashboard

```text
uvicorn apps.agent.main:app --reload
cd dashboard/frontend
npm install
npm run dev
```

Open http://localhost:5173 — Overview and Chat are mock; Reddit config writes to the database.

## Evaluator

Fill purpose, prompt, examples, and criteria on each category (Reddit panel → Edit). Then:

```text
python -m apps.evaluator.main --migrate
python -m apps.evaluator.main --limit 20
```

Requires `LLM_API_KEY` in `.env`.

