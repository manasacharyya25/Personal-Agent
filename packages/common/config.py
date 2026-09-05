from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_CONNECTION_STRING: str

    LLM_MODEL: str = "qwen3:4b-instruct"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    REDDIT_REQUEST_DELAY_SECONDS: float = 3.0
    REDDIT_POST_DELAY_MIN_SECONDS: float = 5.0
    REDDIT_POST_DELAY_MAX_SECONDS: float = 15.0
    REDDIT_SUBREDDIT_MAX_AGE_HOURS: float = 24.0
    REDDIT_MAX_RETRIES: int = 3
    REDDIT_MAX_PAGES_PER_TARGET: int = 5
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_USER_DATA_DIR: str = "data/playwright-reddit"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
