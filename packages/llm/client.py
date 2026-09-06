import json
import re

from typing import Type, TypeVar
from pydantic import BaseModel

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

T = TypeVar("T", bound=BaseModel)

def _ollama_base_url(url: str) -> str:
    base = (url or "").strip().rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3].rstrip("/")
    return base or "http://localhost:11434"


def _content_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        return "".join(parts)
    return str(content)


def _parse_json(text: str) -> dict:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            return {}
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
    return data if isinstance(data, dict) else {}


class LlmClient:
    def __init__(self, model: str, base_url: str):
        self.model = ChatOllama(
            model=model,
            base_url=_ollama_base_url(base_url),
            temperature=0,
            format="json",
        )

    def complete_json(self, prompt: str) -> dict:
        response = self.model.invoke([HumanMessage(content=prompt)])
        return _parse_json(_content_text(response.content))

    def evaluate(self, prompt: str, schema: Type[T]) -> T:
        structured_llm = self.model.with_structured_output(schema)
        response = structured_llm.invoke([HumanMessage(prompt)])
        return response