import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT /
    "day36_confidence_stress_indicators" /
    "src"
)

sys.path.insert(0, str(SRC_DIR))

from confidence_analyzer import ConfidenceAnalyzer
from sentiment_engine import SentimentEngine
from behavioral_signals import BehavioralSignalAnalyzer


def test_hesitation_detection():

    analyzer = ConfidenceAnalyzer()

    result = analyzer.detect_hesitation(
        "Um, I think this was difficult."
    )

    assert result["detected"] is True


def test_uncertainty_detection():

    analyzer = ConfidenceAnalyzer()

    result = analyzer.detect_uncertainty(
        "Maybe I can complete it."
    )

    assert result["detected"] is True


def test_repeated_words():

    analyzer = ConfidenceAnalyzer()

    result = analyzer.detect_repeated_words(
        "I I worked on Python."
    )

    assert "i" in result["repeated_words"]


def test_confidence_score():

    analyzer = ConfidenceAnalyzer()

    result = analyzer.calculate_confidence_score(
        "I am confident in Python and SQL."
    )

    assert result >= 80


def test_positive_sentiment():

    engine = SentimentEngine()

    result = engine.analyze(
        "I successfully completed the project."
    )

    assert result["sentiment"] == "positive"


def test_negative_sentiment():

    engine = SentimentEngine()

    result = engine.analyze(
        "I was worried about the difficult problem."
    )

    assert result["sentiment"] == "negative"


def test_contradiction():

    analyzer = BehavioralSignalAnalyzer()

    result = analyzer.detect_contradiction(
        "I have 2 years of experience.",
        {
            "experience_years": 1
        }
    )

    assert result["contradiction"] is True


def test_no_contradiction():

    analyzer = BehavioralSignalAnalyzer()

    result = analyzer.detect_contradiction(
        "I have 1 year of experience.",
        {
            "experience_years": 1
        }
    )

    assert result["contradiction"] is False


def test_stress_score():

    analyzer = BehavioralSignalAnalyzer()

    score = analyzer.calculate_stress_score(
        {
            "hesitation_count": 1,
            "pause_count": 1
        },
        {
            "count": 1
        },
        {
            "count": 1
        },
        {
            "sentiment": "negative"
        }
    )

    assert score > 0