from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

TIME_FILTERS = ("hour", "day", "week", "month", "year", "all")


def jsonable(row: dict | None) -> dict | None:
    if row is None:
        return None
    out: dict[str, Any] = {}
    for key, value in dict(row).items():
        if isinstance(value, datetime):
            out[key] = value.isoformat()
        else:
            out[key] = value
    return out


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name is required")
        return cleaned


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=80)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name is required")
        return cleaned


class SourceCreate(BaseModel):
    subreddit: str = Field(min_length=1, max_length=80)
    category_id: int
    active: bool = True
    priority: int = 0

    @field_validator("subreddit")
    @classmethod
    def clean_subreddit(cls, value: str) -> str:
        name = value.strip().removeprefix("r/").strip("/")
        if not name:
            raise ValueError("subreddit is required")
        return name


class SourceUpdate(BaseModel):
    category_id: int | None = None
    active: bool | None = None
    priority: int | None = None


class SearchCreate(BaseModel):
    query: str = Field(min_length=1, max_length=300)
    category_id: int
    time_filter: Literal["hour", "day", "week", "month", "year", "all"] = "week"
    active: bool = True
    priority: int = 0

    @field_validator("query")
    @classmethod
    def clean_query(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("query is required")
        return cleaned


class SearchUpdate(BaseModel):
    category_id: int | None = None
    time_filter: Literal["hour", "day", "week", "month", "year", "all"] | None = None
    active: bool | None = None
    priority: int | None = None
