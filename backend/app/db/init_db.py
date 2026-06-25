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
    if "email" not in column_names:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(120)"))
    if "avatar_initial" not in column_names:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN avatar_initial VARCHAR(2) DEFAULT ''"))
    if "is_demo" not in column_names:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN is_demo BOOLEAN DEFAULT 0"))


def seed_db(db: Session) -> None:
    seed_test_user(db)
    seed_cloud_user(db)
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
        db.add(User(username="test", password_hash=password_hash, avatar_initial="T", is_demo=True))
        return

    test_user.password_hash = password_hash
    test_user.email = None
    test_user.avatar_initial = "T"
    test_user.is_demo = True


def seed_cloud_user(db: Session) -> None:
    email = "694042546@qq.com"
    user = db.query(User).filter((User.username == email) | (User.email == email)).first()
    password_hash = hash_password("12345678", "python_exam_agent_cloud_user")
    if not user:
        db.add(
            User(
                username=email,
                email=email,
                password_hash=password_hash,
                avatar_initial="6",
                is_demo=False,
            )
        )
        return

    user.email = email
    user.password_hash = password_hash
    user.avatar_initial = user.avatar_initial or "6"
    user.is_demo = False
