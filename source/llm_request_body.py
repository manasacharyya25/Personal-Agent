from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    role : str
    content : str

class LlmRequestBody(BaseModel):
    system_prompt: Optional[str] = None
    user_prompt: str
    chat_message : list[Message]
    top_k: int = 5
    stream: bool = True