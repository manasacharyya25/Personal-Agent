from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    LLM_API_KEY : str
    LLM_MODEL : str = "gpt-4o-min"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_MIN_POOL_SIZE: int
    DB_MAX_POOL_SIZE: int
    DB_CONNECTION_STRING: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings :
    return Settings()