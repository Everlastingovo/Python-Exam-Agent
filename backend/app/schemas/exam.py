from datetime import datetime

from pydantic import BaseModel, Field


class QuestionOut(BaseModel):
    id: int
    title: str
    description: str
    topic: str
    difficulty: str
    function_signature: str
    starter_code: str


class GenerateExamRequest(BaseModel):
    topic: str = Field(..., min_length=1, examples=["loops"])
    difficulty: str = Field("standard", examples=["standard"])
    number_of_questions: int = Field(3, ge=1, le=8)
    username: str | None = Field(None, max_length=80)


class GenerateExamResponse(BaseModel):
    exam_id: int
    topic: str
    difficulty: str
    questions: list[QuestionOut]


class SubmitAnswerRequest(BaseModel):
    exam_id: int
    question_id: int
    code: str = Field(..., min_length=1)


class TestResultOut(BaseModel):
    input: dict
    expected: object
    actual: object | None = None
    passed: bool
    error: str | None = None
    file_results: list[dict] = Field(default_factory=list)


class SubmitAnswerResponse(BaseModel):
    submission_id: int
    is_correct: bool
    test_results: list[TestResultOut]
    feedback: str
    error_message: str | None = None


class FeedbackReportOut(BaseModel):
    exam_id: int
    total_questions: int
    solved_questions: int
    score_percent: float
    summary: str
    weak_topics: list[str]
    suggestions: list[str]


class HistoryItemOut(BaseModel):
    exam_id: int
    topic: str
    difficulty: str
    status: str
    created_at: datetime
    solved_questions: int
    total_submissions: int
