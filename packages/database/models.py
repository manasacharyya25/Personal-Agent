from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class RedditSource:
    id: int
    subreddit: str
    category_id: int
    active: bool
    priority: int
    last_seen_post_id: str | None
    last_seen_created_at: datetime | None
    pagination_state: dict[str, Any] | None
    last_scanned_at: datetime | None


@dataclass
class RedditSearchQuery:
    id: int
    query: str
    time_filter: str
    category_id: int
    active: bool
    priority: int
    last_seen_post_id: str | None
    last_seen_created_at: datetime | None
    pagination_state: dict[str, Any] | None
    last_scanned_at: datetime | None


@dataclass
class ParsedPost:
    reddit_post_id: str
    subreddit: str | None
    author: str | None
    title: str
    body: str
    url: str
    permalink: str
    created_at: datetime | None
    metadata: dict[str, Any]
