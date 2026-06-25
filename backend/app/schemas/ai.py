from pydantic import BaseModel, Field


class AiGenerateRequest(BaseModel):
    api_key: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)


class AiGeneratedQuestion(BaseModel):
    title: str
    topic: str
    difficulty: str
    description: str
    function_signature: str
    examples: list[dict] = Field(default_factory=list)


class AiGenerateResponse(BaseModel):
    questions: list[AiGeneratedQuestion]
