from pathlib import Path
import json

from day43_ethics_compliance_review.src.consent_manager import ConsentManager
from day43_ethics_compliance_review.src.bias_signal_detector import BiasSignalDetector
from day43_ethics_compliance_review.src.fairness_reviewer import FairnessReviewer
from day43_ethics_compliance_review.src.explainability import ExplainabilityGenerator
from day43_ethics_compliance_review.src.retention_manager import RetentionManager


BASE_DIR = Path(__file__).resolve().parent.parent


def load_config():
    with open(
        BASE_DIR / "config" / "compliance_config.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def test_consent_required():
    config = load_config()

    manager = ConsentManager(config)

    result = manager.validate_consent(False)

    assert result["consent_valid"] is False
    assert result["status"] == "BLOCKED"


def test_consent_allowed():
    config = load_config()

    manager = ConsentManager(config)

    result = manager.validate_consent(True)

    assert result["consent_valid"] is True
    assert result["status"] == "ALLOWED"


def test_demographic_signal_detection():
    config = load_config()

    detector = BiasSignalDetector(config)

    result = detector.detect(
        "Candidate age is 25 and gender is female."
    )

    assert result["bias_signal_count"] >= 2


def test_demographic_signal_removal():
    config = load_config()

    detector = BiasSignalDetector(config)

    result = detector.remove_signals(
        "Candidate age is 25."
    )

    assert "age" in result["removed_signals"]


def test_fairness_review():
    config = load_config()

    reviewer = FairnessReviewer(config)

    candidates = [
        {"final_score": 80},
        {"final_score": 85},
        {"final_score": 90}
    ]

    result = reviewer.review_scores(candidates)

    assert result["candidate_count"] == 3
    assert result["score_difference"] == 10


def test_explainability():
    generator = ExplainabilityGenerator()

    candidate = {
        "candidate_id": "C001",
        "final_score": 85,
        "decision": "SHORTLISTED",
        "score_components": {
            "skills": 90,
            "experience": 80,
            "communication": 85,
            "consistency": 90
        }
    }

    result = generator.generate(candidate)

    assert result["candidate_id"] == "C001"
    assert len(result["explanation"]) > 0


def test_retention_calculation():
    config = load_config()

    manager = RetentionManager(config)

    result = manager.calculate_expiry(
        "2026-10-05T10:00:00"
    )

    assert result["retention_days"] == 90
    assert result["deletion_after_expiry"] is True