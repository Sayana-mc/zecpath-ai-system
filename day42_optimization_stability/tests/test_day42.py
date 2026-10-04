import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day42_optimization_stability"
    / "src"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)

from transcript_cleaner import TranscriptCleaner
from followup_stabilizer import FollowUpStabilizer
from refined_scoring_engine import RefinedScoringEngine
from anomaly_detector import ScoreAnomalyDetector


def test_transcript_cleanup():

    cleaner = TranscriptCleaner()

    result = cleaner.clean(
        "Actually um I worked worked with my team."
    )

    assert "um" not in result.lower()
    assert "worked worked" not in result.lower()


def test_empty_transcript():

    cleaner = TranscriptCleaner()

    assert cleaner.clean("") == ""


def test_followup_limit():

    stabilizer = FollowUpStabilizer(
        max_followups=2
    )

    history = [
        "Question 1",
        "Question 2"
    ]

    result = stabilizer.select_followup(
        "This is a detailed response with enough information.",
        history
    )

    assert result is None


def test_short_response_followup():

    stabilizer = FollowUpStabilizer()

    result = stabilizer.select_followup(
        "Yes",
        []
    )

    assert result is not None


def test_score_upper_bound():

    engine = RefinedScoringEngine()

    assert engine.validate_score(150) == 100


def test_score_lower_bound():

    engine = RefinedScoringEngine()

    assert engine.validate_score(-20) == 0


def test_missing_score():

    engine = RefinedScoringEngine(
        default_score=50
    )

    assert engine.validate_score(None) == 50


def test_anomaly_detection():

    engine = RefinedScoringEngine(
        anomaly_difference_threshold=40
    )

    result = engine.detect_anomaly(
        [95, 90, 20, 92]
    )

    assert result is True


def test_normal_scores():

    engine = RefinedScoringEngine()

    result = engine.detect_anomaly(
        [80, 85, 82, 88]
    )

    assert result is False


def test_anomaly_detector():

    detector = ScoreAnomalyDetector(
        difference_threshold=40
    )

    result = detector.analyze(
        [95, 90, 20, 92]
    )

    assert result["anomaly_detected"] is True


def test_score_calculation():

    engine = RefinedScoringEngine()

    result = engine.calculate_refined_score(
        80,
        85,
        90,
        88
    )

    assert result["refined_score"] == 85.75
    assert result["anomaly_detected"] is False