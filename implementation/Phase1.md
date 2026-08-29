# Phase 1 — Knowledge, Reddit, Evaluator, Agent

This is the first slice of the personal agent. It is smaller than `Handoff.md`. Later platforms (LinkedIn, Instagram, X, Slack, Playwright actors) wait until this loop works.

**Stack:** FastAPI, LangChain, React, Postgres (pgvector).

Existing FastAPI / RAG learning modules are archived under `source/`. They are not wired into this tree. Root copies are still there until we choose to remove them. `learning/` notes stay as-is.

## What we are building

```text
knowledge/*.md  →  ingest (chunk + embed)  →  documents table
                                                      ↓
Reddit scraper  →  reddit_posts (everything seen)
                                                      ↓
                 evaluator (LLM + 3 knowledge bases)
                                                      ↓
                 relevant posts only
                                                      ↓
            React dashboard          FastAPI agent chat
            (list posts)             (one thread per post)
```

1. Three knowledge bases (markdown → embeddings).
2. One Reddit scraper. It stores every post it sees. It does not decide relevance.
3. Evaluator reads scraped posts, reasons with the LLM against the knowledge bases, and keeps what is relevant (RhoQ lead, ThoughtSpace lead, or job fit).
4. FastAPI agent + React UI: dashboard lists relevant posts; chat is one thread per post for drafting replies, onboarding messages, or job applications.

Sending drafts on Reddit is not in Phase 1.

## In scope

| Piece | Where |
|---|---|
| RhoQ knowledge | `knowledge/rhoq/knowledgebase.md` |
| ThoughtSpace knowledge | `knowledge/thoughtspace/knowledgebase.md` |
| Personal skillset | `knowledge/personal/skills.md` |
| Knowledge ingest | `ingestion/` |
| Reddit extraction | `apps/extraction/` + `packages/integrations/reddit.py` |
| Lead + job matching | `apps/evaluator/` |
| Chat + dashboard API | `apps/agent/` |
| React UI | `dashboard/frontend/` |

## Out of scope (not created)

- Actor / write bots (actually posting or applying)
- LinkedIn, Instagram, X, Slack, WhatsApp, Upwork, Playwright
- Vercel / Supabase product analytics
- Job queue package
- A second API under `dashboard/api/` — `apps/agent` is the API

## Phase 1 tree

```text
Implementation/
└── Phase1.md

apps/
├── agent/                 FastAPI: list posts, chat per post, drafts
├── extraction/            Reddit scraper
└── evaluator/             Lead matcher + job matcher

packages/
├── database/
├── llm/                   LangChain client, embeddings, reasoning
├── prompts/shared/
├── common/
└── integrations/reddit.py

knowledge/
├── rhoq/knowledgebase.md
├── thoughtspace/knowledgebase.md
└── personal/skills.md

ingestion/
dashboard/frontend/        React
migrations/
tests/
source/                    archived learning code (not used yet)
```

## Build order (when we start writing code)

1. Finish the three knowledge markdown files, then ingest.
2. Chat that can answer from those KBs.
3. React shell talking to the agent.
4. Reddit scrape → store all posts.
5. Evaluator → relevant posts on the dashboard.
6. Per-post chat drafts (reply / onboarding / application).

## Success

Ingest three knowledge files, scrape Reddit, evaluate, open the UI, see relevant posts, click one, get a draft from the right knowledge base.
