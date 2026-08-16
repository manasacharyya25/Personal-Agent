from logger import log_message
import os
from openai import AsyncOpenAI

class llm_client:
    def __init__(self):
        api_key = os.getenv("LLM_API_KEY")

        if not api_key:
            raise ValueError("LLM_API_KEY is not set")

        self.llm_model = os.getenv("LLM_MODEL")
        if not self.llm_model:
            self.llm_model = "gpt-4o-mini"

        self.client = AsyncOpenAI(api_key=api_key)

    async def send_message(self, msg : str):
        response = await self.client.responses.create(
            model = self.llm_model,
            input = msg
        )

        return response.output_text