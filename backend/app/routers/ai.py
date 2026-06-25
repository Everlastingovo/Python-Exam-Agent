from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.question import Question
from app.schemas.ai import AiGenerateRequest, AiGenerateResponse
from app.services.ai_question_generator import generate_ai_questions

router = APIRouter(tags=["ai"])


@router.post("/ai/generate-questions", response_model=AiGenerateResponse)
def generate_questions(payload: AiGenerateRequest, db: Session = Depends(get_db)) -> AiGenerateResponse:
    questions = db.query(Question).order_by(Question.id).all()
    try:
        generated = generate_ai_questions(payload.api_key, payload.model, questions)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return AiGenerateResponse(questions=generated)
