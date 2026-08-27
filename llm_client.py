from logger import log_message
import os
from openai import AsyncOpenAI
from tools import TOOL_REGISTRY
from config.settings import Settings, get_settings

class llm_client:
    def __init__(self, settings: Settings):
        api_key = settings.LLM_API_KEY

        if not api_key:
            raise ValueError("LLM_API_KEY is not set")

        self.llm_model =settings.LLM_MODEL

        self.client = AsyncOpenAI(api_key=api_key)

    async def send_message(self, system_prompt : str, user_query: str, tools):
        response = await self.client.responses.create(
            model = self.llm_model,
            instructions=system_prompt,
            input = user_query,
            tools = tools
        )

        return response    


    async def send_subsequent_message(self, previous_call_id: str, tool_result: str):
        response = await self.client.responses.create(
                model=self.llm_model,
                previous_response_id=previous_call_id,
                input=tool_result,
            )
        
        return response
