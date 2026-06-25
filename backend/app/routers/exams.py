from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.exam import Exam, ExamQuestion, FeedbackReport
from app.models.question import Question
from app.models.submission import Submission
from app.models.user import User
from app.schemas.exam import (
    FeedbackReportOut,
    GenerateExamRequest,
    GenerateExamResponse,
    HistoryItemOut,
    QuestionOut,
    WrongQuestionOut,
)
from app.services.feedback_generator import build_exam_feedback

router = APIRouter(tags=["exams"])


@router.post("/generate-exam", response_model=GenerateExamResponse)
def generate_exam(payload: GenerateExamRequest, db: Session = Depends(get_db)) -> GenerateExamResponse:
    if payload.topic == "__all__":
        questions = (
            db.query(Question)
            .filter(Question.difficulty == payload.difficulty)
            .order_by(Question.id)
            .limit(8)
            .all()
        )
    else:
        questions = (
            db.query(Question)
            .filter(Question.topic == payload.topic, Question.difficulty == payload.difficulty)
            .order_by(Question.id)
            .limit(payload.number_of_questions)
            .all()
        )

    target_count = 8 if payload.topic == "__all__" else payload.number_of_questions
    if len(questions) < target_count:
        fallback_questions = (
            db.query(Question)
            .filter(Question.difficulty == payload.difficulty)
            .order_by(Question.id)
            .limit(target_count)
            .all()
        )
        questions = fallback_questions

    if not questions:
        raise HTTPException(status_code=404, detail="No questions are available for this difficulty yet.")

    user = None
    if payload.username:
        user = db.query(User).filter(User.username == payload.username).first()
        if not user:
            user = User(username=payload.username)
            db.add(user)
            db.flush()

    exam = Exam(
        user_id=user.id if user else None,
        topic="full exam" if payload.topic == "__all__" else payload.topic,
        difficulty=payload.difficulty,
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
        questions=[QuestionOut.model_validate(question, from_attributes=True) for question in questions],
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
        questions=[QuestionOut.model_validate(link.question, from_attributes=True) for link in ordered_links],
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
