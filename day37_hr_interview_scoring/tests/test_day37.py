import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = (
    PROJECT_ROOT
    / "day37_hr_interview_scoring_engine"
    / "config"
)

SRC_DIR = (
    PROJECT_ROOT
    / "day37_hr_interview_scoring_engine"
    / "src"
)

sys.path.insert(0, str(CONFIG_DIR))
sys.path.insert(0, str(SRC_DIR))


from scoring_config import load_config
from hr_scoring_engine import HRInterviewScoringEngine


def create_engine():

    return HRInterviewScoringEngine(
        load_config()
    )


def test_weight_configuration():

    config = load_config()

    total = sum(
        config["weights"].values()
    )

    assert total == 1.0


def test_weighted_score():

    engine = create_engine()

    score = engine.calculate_weighted_score(
        5,
        4,
        4,
        5
    )

    assert score > 0


def test_normalized_score():

    engine = create_engine()

    score = engine.normalize_score(
        5
    )

    assert score == 100


def test_breakdown():

    engine = create_engine()

    result = engine.generate_breakdown(
        5,
        4,
        4,
        5
    )

    assert "answer_relevance" in result
    assert "communication" in result
    assert "confidence" in result
    assert "consistency" in result


def test_candidate_score():

    engine = create_engine()

    result = engine.calculate_candidate_score(
        responses=4,
        relevance=5,
        communication=4,
        confidence=4,
        consistency=5
    )

    assert "normalized_score" in result
    assert result["normalized_score"] >= 0
    assert result["normalized_score"] <= 100