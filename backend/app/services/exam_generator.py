from collections import Counter
from random import shuffle

from app.models.question import Question

EXAM_DIFFICULTY_PLAN = {
    "easy": 3,
    "medium": 3,
    "hard": 2,
}
MAX_TOPIC_REPEAT = 2


def build_balanced_exam(questions: list[Question]) -> list[Question]:
    selected: list[Question] = []
    topic_counts: Counter[str] = Counter()

    for difficulty, required_count in EXAM_DIFFICULTY_PLAN.items():
        candidates = [question for question in questions if question.difficulty == difficulty]
        shuffle(candidates)
        chosen_for_difficulty = []

        for question in candidates:
            if topic_counts[question.topic] >= MAX_TOPIC_REPEAT:
                continue
            chosen_for_difficulty.append(question)
            topic_counts[question.topic] += 1
            if len(chosen_for_difficulty) == required_count:
                break

        if len(chosen_for_difficulty) < required_count:
            raise ValueError(f"Not enough {difficulty} questions are available for the exam.")

        selected.extend(chosen_for_difficulty)

    if len(selected) != sum(EXAM_DIFFICULTY_PLAN.values()):
        raise ValueError("The exam could not be built with the required difficulty distribution.")

    return selected
