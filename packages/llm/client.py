import json

from openai import OpenAI


class LlmClient:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def complete_json(self, prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content or "{}"
        return json.loads(text)
