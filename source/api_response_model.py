from pydantic import BaseModel

class LlmResponseModel(BaseModel):
    llm_response: str
    created_at: str