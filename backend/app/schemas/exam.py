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
    examples: list[dict] = Field(default_factory=list)


class GenerateExamRequest(BaseModel):
    topic: str = Field(..., min_length=1, examples=["__all__"])
    difficulty: str = Field("mixed", examples=["mixed"])
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
    hidden: bool = False


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
    total_questions: int
    total_submissions: int


class WrongQuestionOut(BaseModel):
    submission_id: int
    exam_id: int
    question_id: int
    title: str
    topic: str
    difficulty: str
    description: str
    function_signature: str
    starter_code: str
    user_code: str
    feedback: str
    error_message: str | None = None
    created_at: datetime


class DailyQuestionOut(BaseModel):
    date: str
    exam_id: int
    question: QuestionOut
    attempts: int
    solved: int
    solve_rate: float


class ShareQuestionRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=80)
    title: str = Field(..., min_length=3, max_length=160)
    description: str = Field(..., min_length=10)
    topic: str = Field("community", min_length=1, max_length=80)
    difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")
    function_signature: str = Field(..., min_length=3, max_length=160)
    examples: list[dict] = Field(..., min_length=1)
    note: str = Field("", max_length=500)


class SharedQuestionOut(BaseModel):
    share_id: int
    question: QuestionOut
    creator_username: str
    note: str
    attempts: int
    solved: int
    solve_rate: float
    created_at: datetime
