from pathlib import Path

from packages.common.logger import get_logger
from packages.database.database import Database
from packages.database.repositories import evaluations as eval_repo
from packages.database.repositories import jobs as job_repo
from packages.llm.client import LlmClient

logger = get_logger(__name__)
TEMPLATE_PATH = Path(__file__).resolve().parent / "prompts" / "system.md"


def _format_criteria(metrics: list) -> str:
    lines = []
    for i, metric in enumerate(metrics, start=1):
        key = metric.get("key") or f"c{i}"
        label = metric.get("label") or key
        definition = metric.get("definition") or ""
        lines.append(f"{i}. `{key}` {label} — {definition}")
    return "\n".join(lines) if lines else "(none)"


def build_prompt(template: str, pair: dict) -> str:
    metrics = pair.get("evaluation_metrics") or []
    return (
        template.replace("{prompt}", pair.get("prompt") or "")
        .replace("{purpose}", pair.get("purpose") or "(not set)")
        .replace("{criteria}", _format_criteria(metrics))
        .replace("{examples}", pair.get("examples") or "(none)")
        .replace("{subreddit}", pair.get("subreddit") or "")
        .replace("{title}", pair.get("title") or "")
        .replace("{body}", pair.get("body") or "")
        .replace("{url}", pair.get("url") or "")
    )


def mean_score(metrics: list, scores: dict) -> float:
    keys = [m.get("key") for m in metrics if m.get("key")]
    if not keys:
        return 0.0
    values = []
    for key in keys:
        raw = scores.get(key, 0)
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            values.append(0.0)
    return round(sum(values) / len(values), 3)


def run_evaluation(db: Database, llm: LlmClient, job_id: int, limit: int) -> int:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    pairs = eval_repo.list_pending_pairs(db, limit)
    logger.info("Evaluating %s post/category pairs", len(pairs))
    done = 0
    for pair in pairs:
        metrics = pair.get("evaluation_metrics") or []
        prompt = build_prompt(template, pair)
        result = llm.complete_json(prompt)
        scores = result.get("scores") or {}
        if not isinstance(scores, dict):
            scores = {}
        reason = str(result.get("reason") or "")
        mean = mean_score(metrics, scores)
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
