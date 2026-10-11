import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PARAMETERS = (
    "accuracy",
    "depth",
    "logical_reasoning",
    "real_world_applicability",
)


def load_json(relative_path):
    path = BASE_DIR / relative_path

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def classify_answer_depth(answer, scores):
    """Use transparent demo heuristics, not semantic AI analysis."""
    words = answer.split()
    word_count = len(words)

    depth_score = scores["depth"]
    reasoning_score = scores["logical_reasoning"]
    application_score = scores["real_world_applicability"]

    if (
        word_count >= 40
        and depth_score >= 4
        and reasoning_score >= 4
        and application_score >= 4
    ):
        return "deep"

    if word_count < 15 or (
        depth_score <= 2 and reasoning_score <= 2
    ):
        return "shallow"

    return "moderate"


def validate_scores(scores):
    for parameter in PARAMETERS:
        if parameter not in scores:
            raise ValueError(f"Missing score: {parameter}")

        value = scores[parameter]

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{parameter} must be numeric")

        if not 0 <= value <= 5:
            raise ValueError(f"{parameter} must be between 0 and 5")


def calculate_score(scores, question_type, rubric):
    validate_scores(scores)

    type_weights = rubric["question_type_weights"].get(question_type)

    if type_weights is None:
        raise ValueError(f"Unsupported question type: {question_type}")

    if set(type_weights) != set(PARAMETERS):
        raise ValueError("Question type weights are incomplete")

    if not abs(sum(type_weights.values()) - 1.0) < 1e-9:
        raise ValueError("Question type weights must sum to 1")

    weighted_score = sum(
        scores[parameter] * type_weights[parameter]
        for parameter in PARAMETERS
    )

    return round(weighted_score / 5 * 100, 2)


def evaluate_answer(record, rubric):
    score = calculate_score(
        record["scores"],
        record["question_type"],
        rubric,
    )

    depth = classify_answer_depth(
        record["answer"],
        record["scores"],
    )

    suggestions = []

    if record["scores"]["accuracy"] < 3:
        suggestions.append("Improve technical correctness.")

    if record["scores"]["depth"] < 3:
        suggestions.append("Add more technical detail.")

    if record["scores"]["logical_reasoning"] < 3:
        suggestions.append("Explain the reasoning step by step.")

    if record["scores"]["real_world_applicability"] < 3:
        suggestions.append("Include a relevant practical example.")

    if not suggestions:
        suggestions.append("Maintain the current standard and explain trade-offs.")

    return {
        "candidate_id": record["candidate_id"],
        "candidate_name": record["candidate_name"],
        "role": record["role"],
        "skill": record["skill"],
        "question_id": record["question_id"],
        "question": record["question"],
        "question_type": record["question_type"],
        "difficulty": record["difficulty"],
        "answer": record["answer"],
        "parameter_scores": record["scores"],
        "technical_score": score,
        "answer_depth": depth,
        "explanation": (
            f"Weighted score: {score}/100. "
            f"Answer depth classified as {depth} using demo rules."
        ),
        "improvement_suggestions": suggestions,
    }


def build_evaluation_report(records, rubric):
    evaluated = [evaluate_answer(record, rubric) for record in records]

    skill_groups = {}

    for item in evaluated:
        skill = item["skill"]
        skill_groups.setdefault(skill, []).append(item["technical_score"])

    skill_breakdown = {
        skill: {
            "question_count": len(scores),
            "average_score": round(sum(scores) / len(scores), 2),
        }
        for skill, scores in skill_groups.items()
    }

    overall_score = (
        round(sum(item["technical_score"] for item in evaluated) / len(evaluated), 2)
        if evaluated else 0
    )

    return {
        "report_title": "Technical Skill Evaluation Report",
        "scoring_method": "Question-type weighted rubric",
        "score_range": "0-100",
        "evaluation_mode": "Rule-based demo using manually supplied parameter scores",
        "candidate_id": records[0]["candidate_id"] if records else None,
        "overall_score": overall_score,
        "question_count": len(evaluated),
        "skill_wise_breakdown": skill_breakdown,
        "question_results": evaluated,
        "review_note": (
            "Scores are decision-support signals. Verify technical correctness "
            "and review results before making hiring decisions."
        ),
    }