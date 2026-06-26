from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.exam import Exam, ExamQuestion, FeedbackReport
from app.models.community import SharedQuestion
from app.models.question import Question
from app.models.submission import Submission
from app.models.user import User
from app.schemas.exam import (
    DailyQuestionOut,
    FeedbackReportOut,
    GenerateExamRequest,
    GenerateExamResponse,
    HistoryItemOut,
    QuestionOut,
    ShareQuestionRequest,
    SharedQuestionOut,
    WrongQuestionOut,
)
from app.services.exam_generator import build_balanced_exam
from app.services.feedback_generator import build_exam_feedback

router = APIRouter(tags=["exams"])


def question_to_out(question: Question) -> QuestionOut:
    examples = [
        {"input": test_case["input"], "expected": test_case["expected"]}
        for test_case in question.test_cases
        if not test_case.get("hidden")
    ]
    return QuestionOut(
        id=question.id,
        title=question.title,
        description=question.description,
        topic=question.topic,
        difficulty=question.difficulty,
        function_signature=question.function_signature,
        starter_code=question.starter_code,
        examples=examples,
    )


def get_or_create_user(db: Session, username: str | None) -> User | None:
    if not username:
        return None
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    user = User(username=username)
    db.add(user)
    db.flush()
    return user


def create_single_question_exam(db: Session, question: Question, username: str | None, topic: str, status: str) -> Exam:
    user = get_or_create_user(db, username)
    exam = Exam(
        user_id=user.id if user else None,
        topic=topic,
        difficulty=question.difficulty,
        status=status,
    )
    db.add(exam)
    db.flush()
    db.add(ExamQuestion(exam_id=exam.id, question_id=question.id, order_number=1))
    db.commit()
    db.refresh(exam)
    return exam


def question_stats(db: Session, question_id: int) -> tuple[int, int, float]:
    submissions = db.query(Submission).filter(Submission.question_id == question_id).all()
    attempts = len(submissions)
    solved = sum(1 for submission in submissions if submission.is_correct)
    solve_rate = round((solved / attempts) * 100, 1) if attempts else 0.0
    return attempts, solved, solve_rate


def build_test_cases_from_examples(examples: list[dict]) -> list[dict]:
    test_cases = []
    for index, example in enumerate(examples):
        if "input" not in example or "expected" not in example:
            raise HTTPException(status_code=422, detail=f"Example {index + 1} must include input and expected.")
        if not isinstance(example["input"], dict):
            raise HTTPException(status_code=422, detail=f"Example {index + 1} input must be a JSON object.")
        test_cases.append(
            {
                "input": example["input"],
                "expected": example["expected"],
                "hidden": False,
            }
        )
    return test_cases


@router.post("/generate-exam", response_model=GenerateExamResponse)
def generate_exam(payload: GenerateExamRequest, db: Session = Depends(get_db)) -> GenerateExamResponse:
    available_questions = db.query(Question).order_by(Question.id).all()

    try:
        questions = build_balanced_exam(available_questions)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    user = None
    if payload.username:
        user = db.query(User).filter(User.username == payload.username).first()
        if not user:
            user = User(username=payload.username)
            db.add(user)
            db.flush()

    exam = Exam(
        user_id=user.id if user else None,
        topic="full exam",
        difficulty="mixed",
    )
    db.add(exam)
    db.flush()

    for index, question in enumerate(questions, start=1):
        db.add(ExamQuestion(exam_id=exam.id, question_id=question.id, order_number=index))

    db.commit()
    db.refresh(exam)

    return GenerateExamResponse(
        exam_id=exam.id,
        topic=exam.topic,
        difficulty=exam.difficulty,
        questions=[question_to_out(question) for question in questions],
    )


@router.post("/generate-practice", response_model=GenerateExamResponse)
def generate_practice(payload: GenerateExamRequest, db: Session = Depends(get_db)) -> GenerateExamResponse:
    questions = db.query(Question).order_by(Question.topic, Question.difficulty, Question.id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No practice questions found.")

    user = None
    if payload.username:
        user = db.query(User).filter(User.username == payload.username).first()
        if not user:
            user = User(username=payload.username)
            db.add(user)
            db.flush()

    exam = Exam(
        user_id=user.id if user else None,
        topic="single question practice",
        difficulty="mixed",
        status="practice",
    )


@router.get("/daily-question", response_model=DailyQuestionOut)
def get_daily_question(
    username: str | None = None,
    start: bool = False,
    db: Session = Depends(get_db),
) -> DailyQuestionOut:
    questions = db.query(Question).order_by(Question.id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No daily question is available.")

    today = date.today()
    index = today.toordinal() % len(questions)
    question = questions[index]
    exam_id = 0
    if start:
        exam = create_single_question_exam(db, question, username, "daily challenge", "daily")
        exam_id = exam.id
    attempts, solved, solve_rate = question_stats(db, question.id)
    return DailyQuestionOut(
        date=today.isoformat(),
        exam_id=exam_id,
        question=question_to_out(question),
        attempts=attempts,
        solved=solved,
        solve_rate=solve_rate,
    )


@router.post("/shared-questions", response_model=SharedQuestionOut)
def share_question(payload: ShareQuestionRequest, db: Session = Depends(get_db)) -> SharedQuestionOut:
    test_cases = build_test_cases_from_examples(payload.examples)
    signature = payload.function_signature.strip()
    starter_code = signature if signature.startswith("def ") else f"def {signature}:\n    # write your code here\n    pass"
    normalized_signature = signature[4:].strip() if signature.startswith("def ") else signature

    question = Question(
        title=payload.title,
        description=payload.description,
        topic=payload.topic,
        difficulty=payload.difficulty,
        function_signature=normalized_signature,
        starter_code=starter_code,
        test_cases=test_cases,
        reference_solution="# Community shared question. Reference solution is not provided.",
    )
    db.add(question)
    db.flush()
    shared = SharedQuestion(
        question_id=question.id,
        creator_username=payload.username,
        note=payload.note,
    )
    db.add(shared)
    db.commit()
    db.refresh(shared)
    attempts, solved, solve_rate = question_stats(db, question.id)
    return SharedQuestionOut(
        share_id=shared.id,
        question=question_to_out(question),
        creator_username=shared.creator_username,
        note=shared.note,
        attempts=attempts,
        solved=solved,
        solve_rate=solve_rate,
        created_at=shared.created_at,
    )


@router.get("/shared-questions", response_model=list[SharedQuestionOut])
def list_shared_questions(db: Session = Depends(get_db)) -> list[SharedQuestionOut]:
    shared_items = db.query(SharedQuestion).order_by(SharedQuestion.created_at.desc()).limit(20).all()
    results = []
    for shared in shared_items:
        question = db.query(Question).filter(Question.id == shared.question_id).first()
        if not question:
            continue
        attempts, solved, solve_rate = question_stats(db, question.id)
        results.append(
            SharedQuestionOut(
                share_id=shared.id,
                question=question_to_out(question),
                creator_username=shared.creator_username,
                note=shared.note,
                attempts=attempts,
                solved=solved,
                solve_rate=solve_rate,
                created_at=shared.created_at,
            )
        )
    return results


@router.post("/shared-questions/{share_id}/start", response_model=GenerateExamResponse)
def start_shared_question(share_id: int, payload: GenerateExamRequest, db: Session = Depends(get_db)) -> GenerateExamResponse:
    shared = db.query(SharedQuestion).filter(SharedQuestion.id == share_id).first()
    if not shared:
        raise HTTPException(status_code=404, detail="Shared question not found.")
    question = db.query(Question).filter(Question.id == shared.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    exam = create_single_question_exam(db, question, payload.username, "shared question", "community")
    return GenerateExamResponse(
        exam_id=exam.id,
        topic=exam.topic,
        difficulty=exam.difficulty,
        questions=[question_to_out(question)],
    )
    db.add(exam)
    db.flush()

    for index, question in enumerate(questions, start=1):
        db.add(ExamQuestion(exam_id=exam.id, question_id=question.id, order_number=index))

    db.commit()
    db.refresh(exam)

    return GenerateExamResponse(
        exam_id=exam.id,
        topic=exam.topic,
        difficulty=exam.difficulty,
        questions=[question_to_out(question) for question in questions],
    )


@router.post("/finish-exam/{exam_id}", response_model=FeedbackReportOut)
def finish_exam(exam_id: int, db: Session = Depends(get_db)) -> FeedbackReportOut:
    exam = (
        db.query(Exam)
        .options(
            joinedload(Exam.questions).joinedload(ExamQuestion.question),
            joinedload(Exam.submissions),
        )
        .filter(Exam.id == exam_id)
        .first()
    )
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    feedback = build_exam_feedback(exam)
    exam.status = "finished"

    existing_report = db.query(FeedbackReport).filter(FeedbackReport.exam_id == exam.id).first()
    if existing_report:
        existing_report.summary = feedback["summary"]
        existing_report.weak_topics = feedback["weak_topics"]
        existing_report.suggestions = feedback["suggestions"]
    else:
        db.add(
            FeedbackReport(
                exam_id=exam.id,
                summary=feedback["summary"],
                weak_topics=feedback["weak_topics"],
                suggestions=feedback["suggestions"],
            )
        )

    db.commit()
    return FeedbackReportOut(**feedback)


@router.get("/exam/{exam_id}", response_model=GenerateExamResponse)
def get_exam(exam_id: int, db: Session = Depends(get_db)) -> GenerateExamResponse:
    exam = (
        db.query(Exam)
        .options(joinedload(Exam.questions).joinedload(ExamQuestion.question))
        .filter(Exam.id == exam_id)
        .first()
    )
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    ordered_links = sorted(exam.questions, key=lambda link: link.order_number)
    return GenerateExamResponse(
        exam_id=exam.id,
        topic=exam.topic,
        difficulty=exam.difficulty,
        questions=[question_to_out(link.question) for link in ordered_links],
    )


@router.get("/history", response_model=list[HistoryItemOut])
def get_history(db: Session = Depends(get_db)) -> list[HistoryItemOut]:
    exams = db.query(Exam).order_by(Exam.created_at.desc()).limit(20).all()
    items = []
    for exam in exams:
        solved_question_ids = {
            submission.question_id
            for submission in exam.submissions
            if submission.is_correct
        }
        items.append(
            HistoryItemOut(
                exam_id=exam.id,
                topic=exam.topic,
                difficulty=exam.difficulty,
                status=exam.status,
                created_at=exam.created_at,
                solved_questions=len(solved_question_ids),
                total_questions=len(exam.questions),
                total_submissions=len(exam.submissions),
            )
        )
    return items


@router.get("/wrong-questions", response_model=list[WrongQuestionOut])
def get_wrong_questions(username: str | None = None, db: Session = Depends(get_db)) -> list[WrongQuestionOut]:
    query = (
        db.query(Submission)
        .join(Submission.question)
        .join(Submission.exam)
        .filter(Submission.is_correct.is_(False))
        .order_by(Submission.created_at.desc())
        .limit(50)
    )

    if username:
        query = query.join(Exam.user).filter(User.username == username)

    submissions = query.all()
    return [
        WrongQuestionOut(
            submission_id=submission.id,
            exam_id=submission.exam_id,
            question_id=submission.question_id,
            title=submission.question.title,
            topic=submission.question.topic,
            difficulty=submission.question.difficulty,
            description=submission.question.description,
            function_signature=submission.question.function_signature,
            starter_code=submission.question.starter_code,
            user_code=submission.user_code,
            feedback=submission.feedback,
            error_message=submission.error_message,
            created_at=submission.created_at,
        )
        for submission in submissions
    ]
