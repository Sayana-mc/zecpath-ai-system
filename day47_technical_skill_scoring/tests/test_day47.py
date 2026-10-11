import pytest

from day47_technical_skill_scoring.src.scoring_engine import (
    load_json,
    calculate_score,
    classify_answer_depth,
    evaluate_answer,
    build_evaluation_report,
)


@pytest.fixture
def rubric():
    return load_json("config/scoring_rubric.json")


def test_perfect_conceptual_score(rubric):
    scores = {
        "accuracy": 5,
        "depth": 5,
        "logical_reasoning": 5,
        "real_world_applicability": 5,
    }

    assert calculate_score(scores, "conceptual", rubric) == 100.0


def test_zero_score(rubric):
    scores = {
        "accuracy": 0,
        "depth": 0,
        "logical_reasoning": 0,
        "real_world_applicability": 0,
    }

    assert calculate_score(scores, "conceptual", rubric) == 0.0


def test_invalid_score_is_rejected(rubric):
    scores = {
        "accuracy": 6,
        "depth": 3,
        "logical_reasoning": 3,
        "real_world_applicability": 3,
    }

    with pytest.raises(ValueError):
        calculate_score(scores, "conceptual", rubric)


def test_shallow_answer_detection():
    scores = {
        "accuracy": 3,
        "depth": 1,
        "logical_reasoning": 1,
        "real_world_applicability": 1,
    }

    assert classify_answer_depth("A list stores items.", scores) == "shallow"


def test_question_evaluation(rubric):
    record = {
        "candidate_id": "TEST001",
        "candidate_name": "Test Candidate",
        "role": "Data Analyst",
        "skill": "SQL",
        "question_id": "T001",
        "question": "Explain INNER JOIN.",
        "question_type": "conceptual",
        "difficulty": "basic",
        "answer": "INNER JOIN returns matching rows.",
        "scores": {
            "accuracy": 4,
            "depth": 3,
            "logical_reasoning": 3,
            "real_world_applicability": 2,
        },
    }

    result = evaluate_answer(record, rubric)

    assert 0 <= result["technical_score"] <= 100
    assert result["answer_depth"] in ("shallow", "moderate", "deep")
    assert "explanation" in result
    assert "improvement_suggestions" in result


def test_report_generation(rubric):
    records = load_json("data/technical_answers.json")

    report = build_evaluation_report(records, rubric)

    assert report["question_count"] == len(records)
    assert "SQL" in report["skill_wise_breakdown"]
    assert "Python" in report["skill_wise_breakdown"]
    assert "question_results" in report