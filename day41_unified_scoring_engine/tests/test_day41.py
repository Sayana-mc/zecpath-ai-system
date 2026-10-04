import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day41_unified_scoring_engine"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))

from unified_scoring_engine import UnifiedScoringEngine


CONFIG_FILE = (
    PROJECT_ROOT
    / "day41_unified_scoring_engine"
    / "config"
    / "role_weights.json"
)


def create_engine():

    return UnifiedScoringEngine(
        CONFIG_FILE
    )


def test_default_weights():

    engine = create_engine()

    weights = engine.get_weights(
        "unknown role"
    )

    assert weights["ats"] == 0.40
    assert weights["screening"] == 0.30
    assert weights["hr_interview"] == 0.30


def test_role_based_weights():

    engine = create_engine()

    weights = engine.get_weights(
        "data analyst"
    )

    assert weights["ats"] == 0.40
    assert weights["screening"] == 0.35
    assert weights["hr_interview"] == 0.25


def test_hiring_fit():

    engine = create_engine()

    score = engine.calculate_hiring_fit(
        80,
        90,
        100,
        "data analyst"
    )

    expected = (
        80 * 0.40
        + 90 * 0.35
        + 100 * 0.25
    )

    assert score == round(
        expected,
        2
    )


def test_high_fit():

    engine = create_engine()

    recommendation = (
        engine.get_recommendation(85)
    )

    assert recommendation == "HIGH_FIT"


def test_moderate_fit():

    engine = create_engine()

    recommendation = (
        engine.get_recommendation(70)
    )

    assert recommendation == "MODERATE_FIT"


def test_low_fit():

    engine = create_engine()

    recommendation = (
        engine.get_recommendation(55)
    )

    assert recommendation == "LOW_FIT"


def test_candidate_evaluation():

    engine = create_engine()

    candidate = {
        "candidate_id": "C001",
        "candidate_name": "Test Candidate",
        "role": "data analyst",
        "ats_score": 80,
        "screening_score": 90,
        "hr_interview_score": 100
    }

    result = engine.evaluate_candidate(
        candidate
    )

    assert "hiring_fit_percentage" in result
    assert "round_scores" in result
    assert "weights" in result
    assert "weighted_contribution" in result
    assert "recommendation" in result


def test_weights_total():

    engine = create_engine()

    weights = engine.get_weights(
        "data analyst"
    )

    assert sum(weights.values()) == 1.0