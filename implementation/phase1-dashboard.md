# Phase 1 — Dashboard

React shell + FastAPI (`apps/agent`). Left sidebar is the app switcher; more tabs come later without changing the layout.

**Live now:** Overview (scored posts) and Reddit config CRUD.  
**Mock now:** Chat.

## Shell

- Left panel: Overview, Reddit, Chat (active).
- Later (visible, disabled): LinkedIn, Instagram, X, Slack, Ops.
- Dark ops UI. Main canvas on the right.

API lives on the agent app, not a second `dashboard/api`. Frontend: `dashboard/frontend`.

## 1. Overview (live)

Lists `pa_post_evaluations` joined to posts, highest `mean_score` first. Filter by category. Expand body and open the Reddit URL.

Empty until the evaluator has written scores.

## 2. Edit Reddit (live)

Writes `pa_categories`, `pa_reddit_sources`, `pa_reddit_search_queries`.

**Categories first.** If there are zero categories:

- Subreddit form and list are disabled
- Search-query form and list are disabled
- User must create a category before anything else

Categories are **not** seeded. A first visit with an empty `pa_categories` table shows only the category form.

Adding a subreddit or search query **requires** a category. No default, no skip.

| Field | Subreddit | Search query |
|---|---|---|
| Name / query | required | required |
| Category | required | required |
| Time filter | — | `hour` `day` `week` `month` `year` `all` |
| Active | yes | yes |
| Priority | yes | yes |

Cannot delete a category that still has sources or searches attached.

## 3. Chat (mock)

Standalone agent thread. Fake replies. Not per-post yet. Layout should be easy to point at FastAPI later.


## 4. To run
```
uvicorn apps.agent.main:app --reload
cd dashboard/frontend && npm run dev
```

## Out of this pass

- Running the scraper from the UI
- Per-post chat / drafts
- Actor / posting

