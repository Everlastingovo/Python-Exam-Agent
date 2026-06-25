from fastapi import APIRouter

from app.services.question_generator import SUPPORTED_TOPICS

router = APIRouter(tags=["topics"])


@router.get("/topics")
def list_topics() -> dict:
    return {"topics": SUPPORTED_TOPICS}
