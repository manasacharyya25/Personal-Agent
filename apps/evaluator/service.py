import re
from itertools import zip_longest
from pathlib import Path

from apps.evaluator.models.PostEvaluationResult import PostEvaluationResult
from packages.common.logger import get_logger
from packages.database.database import Database
from packages.database.repositories import evaluations as eval_repo
from packages.database.repositories import jobs as job_repo
from packages.llm.client import LlmClient

logger = get_logger(__name__)


def _post_block(pair: dict) -> str:
    title = (pair.get("title") or "").strip()
    body = (pair.get("body") or "").strip()
    return "\n\n".join(part for part in (title, body) if part)


def build_prompt(pair: dict) -> str:
    prompt = (pair.get("prompt") or "").strip()
    examples = (pair.get("examples") or "").strip()
    post = _post_block(pair)
    sections = [prompt]
    if examples:
        sections.append(f"## EXAMPLES\n{examples}")
    if post:
        sections.append(f"## POST TO EVALUATE\n{post}")
    return "\n\n".join(section for section in sections if section)


def _slug(text: str, max_len: int = 40) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", (text or "").strip()).strip("._-")
    return (cleaned or "unknown")[:max_len]


def pick_diverse_dump_pairs(pairs: list[dict], limit: int) -> list[dict]:
    """Unique posts, mixing subreddit and search sources; one per source first."""
    by_source: dict[tuple, list[dict]] = {}
    for pair in pairs:
        key = (pair.get("discovery_method") or "", pair.get("discovery_query") or "")
        by_source.setdefault(key, []).append(pair)

    sub_keys = sorted(k for k in by_source if k[0] == "subreddit")
    search_keys = sorted(k for k in by_source if k[0] == "search")
    other_keys = sorted(k for k in by_source if k[0] not in ("subreddit", "search"))
    interleaved: list[tuple] = []
    for sub_key, search_key in zip_longest(sub_keys, search_keys):
        if sub_key:
            interleaved.append(sub_key)
        if search_key:
            interleaved.append(search_key)
    interleaved.extend(other_keys)

    picked: list[dict] = []
    seen_posts: set[int] = set()
    cursors = {key: 0 for key in interleaved}
    while len(picked) < limit:
        added = False
        for key in interleaved:
            bucket = by_source[key]
            index = cursors[key]
            while index < len(bucket) and bucket[index]["post_id"] in seen_posts:
                index += 1
            cursors[key] = index
            if index >= len(bucket):
                continue
            pair = bucket[index]
            cursors[key] = index + 1
            picked.append(pair)
            seen_posts.add(pair["post_id"])
            added = True
            if len(picked) >= limit:
                break
        if not added:
            break
    return picked


def dump_prompts(db: Database, out_dir: Path, limit: int, pool_size: int = 200) -> list[Path]:
    pool = eval_repo.list_dump_pairs(db, pool_size)
    pairs = pick_diverse_dump_pairs(pool, limit)
    logger.info(
        "Dumping %s prompts from %s pairs across %s sources",
        len(pairs),
        len(pool),
        len({(p.get("discovery_method"), p.get("discovery_query")) for p in pool}),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.txt"):
        old.unlink()
    written: list[Path] = []
    for index, pair in enumerate(pairs, start=1):
        method = _slug(str(pair.get("discovery_method") or "unknown"), 12)
        source = _slug(str(pair.get("discovery_query") or "unknown"), 40)
        reddit_id = _slug(str(pair.get("reddit_post_id") or pair["post_id"]), 20)
        path = out_dir / f"{index:02d}_{method}_{source}_{reddit_id}.txt"
        path.write_text(build_prompt(pair), encoding="utf-8")
        written.append(path)
        logger.info(
            "Wrote %s (post %s × %s via %s:%s)",
            path.name,
            pair["post_id"],
            pair.get("category_name"),
            pair.get("discovery_method"),
            pair.get("discovery_query"),
        )
    return written


def mean_score(scores: dict) -> float:
    values = []
    for raw in (scores or {}).values():
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            continue
    if not values:
        return 0.0
    return round(sum(values) / len(values), 3)


def run_evaluation(
    db: Database,
    llm: LlmClient,
    job_id: int,
    limit: int,
    category_id: int | None = None,
) -> int:
    pairs = eval_repo.list_pending_pairs(db, limit, category_id=category_id)
    logger.info("Evaluating %s post/category pairs", len(pairs))
    done = 0
    for pair in pairs:
        prompt = build_prompt(pair)

        structured_output = llm.evaluate(prompt=prompt, schema=PostEvaluationResult)

        # result = llm.complete_json(prompt)
        # reason = str(result.get("reason") or "")
        # scores = {}
        # raw = result.get("user_interest")
        # try:
        #     scores["user_interest"] = float(raw)
        # except (TypeError, ValueError):
        #     pass
        # mean = mean_score(scores)

        scores = {"user_interest": structured_output.user_interest}
        reason = structured_output.reason
        mean = structured_output.user_interest

        eval_repo.upsert_evaluation(
            db,
            post_id=pair["post_id"],
            category_id=pair["category_id"],
            scores=scores,
            mean_score=mean,
            reason=reason,
            job_id=job_id,
        )
        job_repo.increment_counts(db, job_id, seen=1, inserted=1)
        done += 1
        logger.info(
            "post %s × %s mean=%s",
            pair["post_id"],
            pair["category_name"],
            mean,
        )
    return done
