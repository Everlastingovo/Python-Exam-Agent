from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models import Exam, ExamQuestion, FeedbackReport, Question, Submission, User
from app.services.question_generator import seed_original_questions


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_db(db: Session) -> None:
    for seeded_question in seed_original_questions():
        existing_question = db.query(Question).filter(Question.title == seeded_question.title).first()
        if not existing_question:
            db.add(seeded_question)
            continue

        existing_question.description = seeded_question.description
        existing_question.topic = seeded_question.topic
        existing_question.difficulty = seeded_question.difficulty
        existing_question.function_signature = seeded_question.function_signature
        existing_question.starter_code = seeded_question.starter_code
        existing_question.test_cases = seeded_question.test_cases
        existing_question.reference_solution = seeded_question.reference_solution
    db.commit()
