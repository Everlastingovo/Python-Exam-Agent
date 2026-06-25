from collections import Counter

from app.models.exam import Exam


def build_exam_feedback(exam: Exam) -> dict:
    latest_by_question = {}
    for submission in sorted(exam.submissions, key=lambda item: item.created_at):
        latest_by_question[submission.question_id] = submission

    solved = sum(1 for submission in latest_by_question.values() if submission.is_correct)
    total = len(exam.questions)
    score = round((solved / total) * 100, 2) if total else 0.0

    weak_topics = []
    failed_topic_counts = Counter()
    for exam_question in exam.questions:
        latest = latest_by_question.get(exam_question.question_id)
        if not latest or not latest.is_correct:
            failed_topic_counts[exam_question.question.topic] += 1

    weak_topics = [topic for topic, _ in failed_topic_counts.most_common()]

    suggestions = []
    if weak_topics:
        suggestions.append(f"Review {weak_topics[0]} with two or three short practice problems.")
        suggestions.append("Run your function manually with the sample inputs before submitting.")
        suggestions.append("Pay attention to empty inputs and boundary cases.")
    else:
        suggestions.append("Try the next difficulty level or practise a different topic.")

    result_label = "PASS" if total and solved == total else "NOT PASS"
    summary = f"{result_label}: You solved {solved} out of {total} question(s), with a score of {score}%."
    return {
        "exam_id": exam.id,
        "total_questions": total,
        "solved_questions": solved,
        "score_percent": score,
        "summary": summary,
        "weak_topics": weak_topics,
        "suggestions": suggestions,
    }
