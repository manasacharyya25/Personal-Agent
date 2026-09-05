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

First Reddit login: set `PLAYWRIGHT_HEADLESS=false`, sign in when the window waits, then later runs reuse `data/playwright-reddit`. Subreddit scans only keep posts from the last 24 hours. There is a 5–15s pause between saved posts.

## Dashboard

```text
uvicorn apps.agent.main:app --reload
cd dashboard/frontend
npm install
npm run dev
```

Open http://localhost:5173 — Overview and Chat are mock; Reddit config writes to the database.

## Evaluator

Fill purpose, evaluator prompt, and examples on each category (Reddit panel → Edit). Preview prompts without calling the LLM:

```text
python -m apps.evaluator.main --dump-prompts
```

Writes up to 10 mixed subreddit/search posts to `output/evaluator-prompts/`. Then score:

```text
python -m apps.evaluator.main --migrate
python -m apps.evaluator.main --limit 20
```

Scoring requires `LLM_API_KEY` in `.env`.

