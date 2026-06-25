from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models import Exam, ExamQuestion, FeedbackReport, Question, Submission, User
from app.services.question_generator import seed_original_questions
from app.services.auth import hash_password


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_user_schema()


def ensure_user_schema() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    column_names = {column["name"] for column in inspector.get_columns("users")}
    if "password_hash" not in column_names:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(256) DEFAULT ''"))


def seed_db(db: Session) -> None:
    seed_test_user(db)
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


def seed_test_user(db: Session) -> None:
    test_user = db.query(User).filter(User.username == "test").first()
    password_hash = hash_password("123456", "python_exam_agent_test_user")
    if not test_user:
        db.add(User(username="test", password_hash=password_hash))
        return

    test_user.password_hash = password_hash
