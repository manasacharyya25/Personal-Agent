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


class EvaluationMetric(BaseModel):
    key: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=120)
    definition: str = Field(min_length=1, max_length=500)

    @field_validator("key", "label", "definition")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("required")
        return cleaned


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    purpose: str | None = None
    prompt: str | None = None
    examples: str | None = None
    evaluation_metrics: list[EvaluationMetric] = Field(default_factory=list)
    active: bool = True

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name is required")
        return cleaned


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    purpose: str | None = None
    prompt: str | None = None
    examples: str | None = None
    evaluation_metrics: list[EvaluationMetric] | None = None
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
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
