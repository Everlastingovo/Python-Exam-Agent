from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    description: Mapped[str] = mapped_column(Text)
    topic: Mapped[str] = mapped_column(String(80), index=True)
    difficulty: Mapped[str] = mapped_column(String(20), index=True)
    function_signature: Mapped[str] = mapped_column(String(160))
    starter_code: Mapped[str] = mapped_column(Text)
    test_cases: Mapped[list[dict]] = mapped_column(JSON)
    reference_solution: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    exam_links = relationship("ExamQuestion", back_populates="question")
    submissions = relationship("Submission", back_populates="question")
