# Phase 1 — Evaluator

Scores discovered Reddit posts. It does not scrape and does not send replies.

**Stack:** per-category evaluator prompt + examples in Postgres. No shared system prompt. Mean of returned score numbers (not weighted).

## Idea

Categories are **use cases** (Job Search, User Acquisition, RhoQ Creator, …). Each has purpose (dashboard only), an evaluator prompt, and examples. Search queries and subreddits stay linked with `category_id`; they inherit purpose from the category.

Inactive categories are skipped.

## Prompt sent to the model

No master template. One user message, three parts:

```text
{evaluator_prompt}

## EXAMPLES
{examples}

## POST TO EVALUATE
{title}

{body}
```

Empty examples (and the EXAMPLES heading) are omitted. Purpose, subreddit, and URL are not included.

Put scoring rules and output shape in the category’s evaluator prompt. The client still asks the API for JSON and stores `scores` plus `reason` when present.

## Category columns (`pa_categories`)

| Column | Role |
|---|---|
| `name` | Job Search, User Acquisition, … |
| `purpose` | Why it exists (dashboard only) |
| `prompt` | Evaluator prompt |
| `examples` | Short good/bad snippets |
| `active` | If false, do not evaluate |

A category is **ready** to evaluate when `active` and `prompt` is non-empty.

## Which categories for a post

Only the category on the **source that found the post** — `pa_reddit_sources.category_id` for a subreddit scrape, or `pa_reddit_search_queries.category_id` for a search. Discovery rows in `pa_reddit_post_discovery_method` are the join.

If the same post was found two ways with **different** categories, it is scored once per category. Same category twice is one eval.

Skip if that category is not ready. One LLM call per `(post, category)`. Upsert `pa_post_evaluations` on `(post_id, category_id)`.

## `pa_post_evaluations`

| Column | Role |
|---|---|
| `post_id` | `pa_reddit_discovered_posts` |
| `category_id` | use case |
| `scores` | JSON object of numeric scores |
| `mean_score` | arithmetic mean of those numbers |
| `reason` | short text |
| `evaluated_at` | |
| `job_id` | `pa_ingestion_jobs` with `job_type = evaluate` |

## Run

Preview prompts without calling the LLM (up to 10 posts, mixed subreddit and search sources):

```text
python -m apps.evaluator.main --dump-prompts
```

Files go to `output/evaluator-prompts/` (gitignored). Each file is the exact prompt that would be sent to the model.

Score posts:

```text
python -m apps.extraction.main --migrate
python -m apps.evaluator.main
python -m apps.evaluator.main --limit 20
```

Scoring uses local Ollama (`LLM_MODEL` and `OLLAMA_BASE_URL` in `.env`). `--dump-prompts` does not.

## Out of this pass

- Weighted scores
- Purpose on search queries
- RAG / knowledge bases in the evaluator
- Showing scores on Overview — live list ranked by `mean_score`
- Per-post chat drafts
