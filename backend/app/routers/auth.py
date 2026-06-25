import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.exam import Exam
from app.models.user import User
from app.schemas.auth import (
    AccountDetailsResponse,
    ActivityAttemptResponse,
    ActivityDayResponse,
    AvatarUpdateRequest,
    LoginRequest,
    LoginResponse,
    SaveToAccountRequest,
    SaveToAccountResponse,
)
from app.services.auth import hash_password, verify_password

router = APIRouter(tags=["auth"])
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def user_to_login_response(user: User, message: str) -> LoginResponse:
    return LoginResponse(
        username=user.username,
        email=user.email,
        avatar_initial=user.avatar_initial or user.username[:1].upper(),
        is_demo=user.is_demo,
        message=message,
    )


def exam_score(exam: Exam) -> tuple[int, int, float]:
    solved_question_ids = {
        submission.question_id
        for submission in exam.submissions
        if submission.is_correct
    }
    total_questions = len(exam.questions) or 8
    solved_questions = len(solved_question_ids)
    percent = round((solved_questions / total_questions) * 100, 2) if total_questions else 0
    return solved_questions, total_questions, percent


def build_activity_days(exams: list[Exam]) -> list[ActivityDayResponse]:
    grouped: dict[str, list[ActivityAttemptResponse]] = {}
    for exam in exams:
        solved_questions, total_questions, percent = exam_score(exam)
        date_key = exam.created_at.date().isoformat()
        grouped.setdefault(date_key, []).append(
            ActivityAttemptResponse(
                exam_id=exam.id,
                score=f"{solved_questions}/{total_questions}",
                solved_questions=solved_questions,
                total_questions=total_questions,
                percent=percent,
            )
        )

    activity_days = []
    for date_key, attempts in grouped.items():
        best_attempt = max(attempts, key=lambda item: item.percent)
        activity_days.append(
            ActivityDayResponse(
                date=date_key,
                best_percent=best_attempt.percent,
                best_score=best_attempt.score,
                attempts=attempts,
            )
        )
    return sorted(activity_days, key=lambda item: item.date)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).filter(or_(User.username == payload.username, User.email == payload.username)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return user_to_login_response(user, "Login successful.")


@router.get("/account/{username}", response_model=AccountDetailsResponse)
def account_details(username: str, db: Session = Depends(get_db)) -> AccountDetailsResponse:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")

    exams = db.query(Exam).filter(Exam.user_id == user.id).order_by(Exam.created_at.asc()).all()
    attempt_count = len(exams)
    return AccountDetailsResponse(
        username=user.username,
        email=user.email,
        avatar_initial=user.avatar_initial or user.username[:1].upper(),
        is_demo=user.is_demo,
        attempt_count=attempt_count,
        learning_time_minutes=attempt_count * 90,
        activity_days=build_activity_days(exams),
    )


@router.post("/account/save-to-account", response_model=SaveToAccountResponse)
def save_to_account(payload: SaveToAccountRequest, db: Session = Depends(get_db)) -> SaveToAccountResponse:
    if not EMAIL_PATTERN.match(payload.email):
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    source_user = db.query(User).filter(User.username == payload.source_username).first()
    if not source_user:
        raise HTTPException(status_code=404, detail="Source account not found.")
    if not source_user.is_demo:
        raise HTTPException(status_code=400, detail="Normal accounts do not need Save to another account.")

    target_user = db.query(User).filter(or_(User.username == payload.email, User.email == payload.email)).first()
    if target_user:
        if not verify_password(payload.password, target_user.password_hash):
            raise HTTPException(status_code=401, detail="The email exists, but the password is incorrect.")
    else:
        target_user = User(
            username=payload.email,
            email=payload.email,
            password_hash=hash_password(payload.password, payload.email),
            avatar_initial=payload.email[:1].upper(),
            is_demo=False,
        )
        db.add(target_user)
        db.flush()

    db.query(Exam).filter(Exam.user_id == source_user.id).update({"user_id": target_user.id})
    db.commit()
    db.refresh(target_user)
    return SaveToAccountResponse(
        username=target_user.username,
        email=target_user.email or payload.email,
        avatar_initial=target_user.avatar_initial or target_user.username[:1].upper(),
        is_demo=False,
        message="Exam history has been saved to this account.",
    )


@router.post("/account/avatar", response_model=AccountDetailsResponse)
def update_avatar(payload: AvatarUpdateRequest, db: Session = Depends(get_db)) -> AccountDetailsResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")

    user.avatar_initial = payload.avatar_initial[:1].upper()
    db.commit()
    return account_details(user.username, db)
