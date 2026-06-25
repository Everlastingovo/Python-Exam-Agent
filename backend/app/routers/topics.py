from fastapi import APIRouter

from app.services.question_generator import SUPPORTED_TOPICS

router = APIRouter(tags=["topics"])


@router.get("/topics")
def list_topics() -> dict:
    return {"topics": [{"value": "__all__", "label": "Full exam: all 8 questions"}] + [{"value": topic, "label": topic} for topic in SUPPORTED_TOPICS]}
