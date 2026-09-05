"""Reddit Playwright client: load a listing page, parse posts, find next page."""

from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
import time

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from packages.common.logger import get_logger
from packages.database.models import ParsedPost

logger = get_logger(__name__)

OLD_REDDIT = "https://old.reddit.com"
LISTING_SELECTOR = ".thing.link[data-fullname]"


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

    def ensure_session(self) -> None:
        self.page.goto(f"{OLD_REDDIT}/", wait_until="domcontentloaded", timeout=60000)
        if self._listing_visible():
            logger.info("Reddit session already logged in")
            return
        self.wait_until_logged_in()

    def wait_until_logged_in(self) -> None:
        logger.info(
            "Reddit login required. Log in in the browser window; "
            "the scraper waits until a post listing appears."
        )
        self.page.wait_for_selector(LISTING_SELECTOR, timeout=0)
        logger.info("Logged in; listing is visible")

    def _listing_visible(self) -> bool:
        return self.page.locator(LISTING_SELECTOR).count() > 0

    def _looks_like_login(self) -> bool:
        url = (self.page.url or "").lower()
        if "login" in url or "register" in url:
            return True
        if self.page.locator("input[name='user']").count() > 0:
            return True
        if self.page.locator("#login_login-main, form#login").count() > 0:
            return True
        return False

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
                if self._looks_like_login() and not self._listing_visible():
                    self.wait_until_logged_in()
                    self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
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
            permalink=permalink,
            created_at=created_at,
            metadata={"score": item.get("score"), "source": "old.reddit.com"},
        )

    def thread_url(self, permalink: str) -> str:
        if permalink.startswith("http"):
            return permalink.replace("https://www.reddit.com", OLD_REDDIT)
        return urljoin(OLD_REDDIT, permalink)

    def fetch_post_body(self, permalink: str) -> str:
        url = self.thread_url(permalink)
        logger.info("Opening post %s", url)
        self._goto_with_retry(url)
        time.sleep(self.request_delay_seconds)
        body = self.page.evaluate(
            """() => {
                const op = document.querySelector('.thing.link .usertext-body .md')
                    || document.querySelector('.thing.link .usertext-body');
                return op ? op.innerText.trim() : '';
            }"""
        )
        return (body or "").strip()
