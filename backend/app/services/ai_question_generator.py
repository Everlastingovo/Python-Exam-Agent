import json
import urllib.error
import urllib.request

from app.models.question import Question


def build_question_bank_context(questions: list[Question]) -> str:
    summaries = []
    for question in questions:
        summaries.append(
            {
                "title": question.title,
                "topic": question.topic,
                "difficulty": question.difficulty,
                "function_signature": question.function_signature,
                "description": question.description,
            }
        )
    return json.dumps(summaries, ensure_ascii=True)


def generate_ai_questions(api_key: str, model: str, questions: list[Question]) -> list[dict]:
    prompt = (
        "Generate 8 original beginner-friendly Python coding questions based on this existing question bank. "
        "Do not copy the questions. The output must be public-safe and must not mention any school, course, exam, instructor, or private source. "
        "Use this exact distribution: 3 easy, 3 medium, 2 hard. No topic may appear more than twice. "
        "Each question must include title, topic, difficulty, description, function_signature, and examples. "
        "Examples must be a list of objects with input and expected fields. "
        "Return only JSON with this shape: {\"questions\": [...]}.\n\n"
        f"Existing question bank:\n{build_question_bank_context(questions)}"
    )
    payload = {
        "model": model,
        "input": prompt,
        "text": {
            "format": {
                "type": "json_object"
            }
        },
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise ValueError(f"AI request failed: {detail}") from error
    except urllib.error.URLError as error:
        raise ValueError(f"AI request failed: {error.reason}") from error

    text = _extract_response_text(response_payload)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("AI response was not valid JSON.") from error

    generated_questions = parsed.get("questions", [])
    if not isinstance(generated_questions, list) or len(generated_questions) != 8:
        raise ValueError("AI response must contain exactly 8 questions.")
    return generated_questions


def _extract_response_text(response_payload: dict) -> str:
    if "output_text" in response_payload:
        return response_payload["output_text"]

    parts = []
    for item in response_payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                parts.append(content.get("text", ""))
    return "\n".join(parts).strip()
