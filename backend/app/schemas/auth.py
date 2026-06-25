from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=80)
    password: str = Field(..., min_length=1, max_length=120)


class LoginResponse(BaseModel):
    username: str
    email: str | None = None
    avatar_initial: str
    is_demo: bool
    message: str


class ActivityAttemptResponse(BaseModel):
    exam_id: int
    score: str
    solved_questions: int
    total_questions: int
    percent: float


class ActivityDayResponse(BaseModel):
    date: str
    best_percent: float
    best_score: str
    attempts: list[ActivityAttemptResponse]


class AccountDetailsResponse(BaseModel):
    username: str
    email: str | None = None
    avatar_initial: str
    is_demo: bool
    attempt_count: int
    learning_time_minutes: int
    activity_days: list[ActivityDayResponse] = Field(default_factory=list)


class SaveToAccountRequest(BaseModel):
    source_username: str = Field(..., min_length=1, max_length=80)
    email: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=8, max_length=120)


class SaveToAccountResponse(BaseModel):
    username: str
    email: str
    avatar_initial: str
    is_demo: bool
    message: str


class AvatarUpdateRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=80)
    avatar_initial: str = Field(..., min_length=1, max_length=2)
