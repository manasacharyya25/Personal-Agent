from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_CONNECTION_STRING: str

    REDDIT_REQUEST_DELAY_SECONDS: float = 3.0
    REDDIT_MAX_RETRIES: int = 3
    REDDIT_MAX_PAGES_PER_TARGET: int = 5
    PLAYWRIGHT_HEADLESS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
