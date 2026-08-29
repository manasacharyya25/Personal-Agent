"""Reddit Playwright client: load a listing page, parse posts, find next page."""

from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
import time

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from packages.database.models import ParsedPost


OLD_REDDIT = "https://old.reddit.com"


class RedditPageError(Exception):
    pass


class RedditBrowser:
    def __init__(
        self,
        page: Page,
        request_delay_seconds: float = 3.0,
        max_retries: int = 3,
    ):
        self.page = page
        self.request_delay_seconds = request_delay_seconds
        self.max_retries = max_retries

    def subreddit_new_url(self, subreddit: str) -> str:
        name = subreddit.removeprefix("r/").strip("/")
        return f"{OLD_REDDIT}/r/{name}/new/"

    def search_url(self, query: str, time_filter: str) -> str:
        q = quote_plus(query)
        t = time_filter or "week"
        return f"{OLD_REDDIT}/search?q={q}&sort=new&restrict_sr=&t={t}"

    def fetch_listing(self, url: str) -> tuple[list[ParsedPost], str | None]:
        self._goto_with_retry(url)
        time.sleep(self.request_delay_seconds)

        raw_posts = self.page.evaluate(
            """() => {
                const things = [...document.querySelectorAll('.thing.link[data-fullname]')];
                return things.map((el) => {
                    const timeEl = el.querySelector('time');
                    return {
                        reddit_post_id: el.getAttribute('data-fullname'),
                        subreddit: el.getAttribute('data-subreddit'),
                        author: el.getAttribute('data-author'),
                        permalink: el.getAttribute('data-permalink'),
                        title: (el.querySelector('a.title') || {}).innerText || '',
                        body: (el.querySelector('.expando .usertext-body') || {}).innerText || '',
                        score: el.getAttribute('data-score'),
                        datetime: timeEl ? timeEl.getAttribute('datetime') : null
                    };
                });
            }"""
        )

        next_url = None
        next_link = self.page.locator("span.next-button a")
        if next_link.count() > 0:
            href = next_link.first.get_attribute("href")
            if href:
                next_url = urljoin(OLD_REDDIT, href)

        posts = [self._to_parsed(item) for item in raw_posts if item.get("reddit_post_id")]
        return posts, next_url

    def _goto_with_retry(self, url: str) -> None:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                snippet = (self.page.content() or "")[:4000].lower()
                if "whoa there" in snippet or "request to open reddit" in snippet:
                    raise RedditPageError(f"Reddit blocked or rate-limited: {url}")
                return
            except RedditPageError:
                raise
            except (PlaywrightTimeoutError, PlaywrightError) as exc:
                last_error = exc
                if attempt == self.max_retries:
                    raise RedditPageError(
                        f"Failed to load {url} after {self.max_retries} tries: {exc}"
                    ) from exc
                time.sleep(self.request_delay_seconds * attempt)
        raise RedditPageError(str(last_error))

    def _to_parsed(self, item: dict) -> ParsedPost:
        created_at = None
        if item.get("datetime"):
            try:
                created_at = datetime.fromisoformat(
                    item["datetime"].replace("Z", "+00:00")
                )
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
            except ValueError:
                created_at = None

        permalink = item.get("permalink") or ""
        url = permalink if permalink.startswith("http") else f"https://www.reddit.com{permalink}"

        return ParsedPost(
            reddit_post_id=item["reddit_post_id"],
            subreddit=item.get("subreddit"),
            author=item.get("author"),
            title=(item.get("title") or "").strip(),
            body=(item.get("body") or "").strip(),
            url=url,
            created_at=created_at,
            metadata={"score": item.get("score"), "source": "old.reddit.com"},
        )
