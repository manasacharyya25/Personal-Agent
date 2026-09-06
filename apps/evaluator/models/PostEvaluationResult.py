from pydantic import BaseModel

class PostEvaluationResult(BaseModel):
    user_interest: float
    reason: str