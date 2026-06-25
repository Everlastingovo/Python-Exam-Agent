from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.exam import ExamQuestion
from app.models.question import Question
from app.models.submission import Submission
from app.schemas.exam import SubmitAnswerRequest, SubmitAnswerResponse
from app.services.code_runner import run_test_cases
from app.services.mistake_analyzer import build_submission_feedback

router = APIRouter(tags=["submissions"])


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(payload: SubmitAnswerRequest, db: Session = Depends(get_db)) -> SubmitAnswerResponse:
    exam_question = (
        db.query(ExamQuestion)
        .filter(
            ExamQuestion.exam_id == payload.exam_id,
            ExamQuestion.question_id == payload.question_id,
        )
        .first()
    )
    if not exam_question:
        raise HTTPException(status_code=404, detail="This question is not part of the exam.")

    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    test_results, error_message = run_test_cases(
        code=payload.code,
        function_signature=question.function_signature,
        test_cases=question.test_cases,
    )
    is_correct = all(result["passed"] for result in test_results)
    failed_count = sum(1 for result in test_results if not result["passed"])
    feedback = build_submission_feedback(is_correct, error_message, failed_count)

    submission = Submission(
        exam_id=payload.exam_id,
        question_id=payload.question_id,
        user_code=payload.code,
        is_correct=is_correct,
        error_message=error_message,
        test_results=test_results,
        feedback=feedback,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return SubmitAnswerResponse(
        submission_id=submission.id,
        is_correct=submission.is_correct,
        test_results=submission.test_results,
        feedback=submission.feedback,
        error_message=submission.error_message,
    )
