from src.ats_scoring_engine import (
    calculate_component_scores,
    calculate_ats_score,
    classify_score,
    generate_score_breakdown,
)


def test_component_scores():

    result = calculate_component_scores(
        0.8,
        0.7,
        0.9,
        0.85,
    )

    assert result["skill_match"] == 80.0
    assert result["experience_relevance"] == 70.0
    assert result["education_alignment"] == 90.0
    assert result["semantic_similarity"] == 85.0


def test_ats_score():

    score = calculate_ats_score(
        0.8,
        0.7,
        0.9,
        0.85,
        "data analyst",
    )

    assert score == 81.0


def test_score_classification():

    assert classify_score(85) == "EXCELLENT"
    assert classify_score(70) == "GOOD"
    assert classify_score(55) == "MODERATE"
    assert classify_score(40) == "LOW"


def test_score_range():

    score = calculate_ats_score(
        1.5,
        -0.2,
        0.8,
        0.9,
        "data analyst",
    )

    assert 0 <= score <= 100


def test_explainable_breakdown():

    result = generate_score_breakdown(
        0.8,
        0.7,
        0.9,
        0.85,
        "data analyst",
    )

    assert "final_score" in result
    assert "classification" in result
    assert "weights" in result
    assert "breakdown" in result

    assert "skill_match" in result["breakdown"]
    assert "experience_relevance" in result["breakdown"]
    assert "education_alignment" in result["breakdown"]
    assert "semantic_similarity" in result["breakdown"]