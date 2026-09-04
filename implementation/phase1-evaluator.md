# Phase 1 — Evaluator

Scores discovered Reddit posts. It does not scrape and does not send replies.

**Stack:** one master prompt template + per-category data in Postgres. Mean of criterion scores (not weighted).

## Idea

Categories are **use cases** (Job Search, User Acquisition, RhoQ Creator, …). Each has its own prompt, examples, and criteria. Search queries and subreddits stay linked with `category_id`; they **inherit purpose from the category**. No `purpose` on `pa_reddit_search_queries`.

Inactive categories are skipped.

## Master template

File: `apps/evaluator/prompts/system.md`

Slots filled at run time. The template never names a product.

```text
You are an evaluator. Score this post using only the category instructions below.
Return JSON with a score (0-5) for each criterion, and a short reason.

CATEGORY PROMPT
{prompt}

PURPOSE
{purpose}

CRITERIA
{metrics as numbered list: label — definition}

EXAMPLES
{examples}

POST
subreddit / title / body / url
```

## Category columns (`pa_categories`)

| Column | Role |
|---|---|
| `name` | Job Search, User Acquisition, … |
| `purpose` | Why it exists (dashboard + template) |
| `prompt` | Category instruction (“Is this someone looking for a workout plan?”) |
| `examples` | Short good/bad snippets |
| `evaluation_metrics` | JSON list: `{ key, label, definition }` |
| `active` | If false, do not evaluate |

Example metric:

```json
{ "key": "role_clarity", "label": "Role Clarity", "definition": "Is the job title clearly defined?" }
```

No weights. **Mean** of the criterion scores is computed in code.

A category is **ready** to evaluate when `active`, `prompt` is non-empty, and `evaluation_metrics` has at least one row.

## Which categories for a post

Every **ready** category. A fitness post is scored separately against Job Search, User Acquisition, etc. Low means on the wrong use case is expected.

One LLM call per `(post, category)`. Upsert `pa_post_evaluations` on `(post_id, category_id)`.

## `pa_post_evaluations`

| Column | Role |
|---|---|
| `post_id` | `pa_reddit_discovered_posts` |
| `category_id` | use case |
| `scores` | `{ "role_clarity": 4, ... }` |
| `mean_score` | arithmetic mean of those scores |
| `reason` | short text |
| `evaluated_at` | |
| `job_id` | `pa_ingestion_jobs` with `job_type = evaluate` |

## Run

```text
python -m apps.extraction.main --migrate
python -m apps.evaluator.main
python -m apps.evaluator.main --limit 20
```

Needs `LLM_API_KEY` (and optional `LLM_MODEL`).

## Out of this pass

- Weighted scores
- Purpose on search queries
- RAG / knowledge bases in the evaluator
- Showing scores on Overview (still mock)
- Per-post chat drafts
