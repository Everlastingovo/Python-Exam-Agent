from fastapi import APIRouter

from app.services.question_generator import SUPPORTED_TOPICS

router = APIRouter(tags=["topics"])


@router.get("/topics")
def list_topics() -> dict:
    return {
        "topics": SUPPORTED_TOPICS,
        "exam_size": 8,
        "difficulty_distribution": {"easy": 3, "medium": 3, "hard": 2},
        "max_questions_per_topic": 2,
        "selection_enabled": False,
    }
