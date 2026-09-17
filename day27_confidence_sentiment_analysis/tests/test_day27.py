import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day27_confidence_sentiment_analysis"
    / "src"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)


from confidence_analyzer import ConfidenceAnalyzer
from sentiment_analyzer import SentimentAnalyzer
from behavioral_analyzer import BehavioralAnalyzer


CONFIG_FILE = (
    PROJECT_ROOT
    / "day27_confidence_sentiment_analysis"
    / "config"
    / "analysis_config.json"
)


def load_config():

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def create_analyzers():

    config = load_config()

    confidence = ConfidenceAnalyzer(
        config
    )

    sentiment = SentimentAnalyzer(
        config
    )

    behavioral = BehavioralAnalyzer(
        confidence,
        sentiment
    )

    return confidence, sentiment, behavioral


def test_hesitation_detection():

    confidence, _, _ = create_analyzers()

    result = confidence.detect_hesitation(
        "Um, I have experience with Python."
    )

    assert result["detected"] is True


def test_uncertainty_detection():

    confidence, _, _ = create_analyzers()

    result = confidence.detect_uncertainty(
        "I think I have one year of experience."
    )

    assert result["detected"] is True


def test_response_length():

    confidence, _, _ = create_analyzers()

    result = confidence.calculate_response_length(
        "I have Python and SQL skills."
    )

    assert result["word_count"] == 6


def test_pace():

    confidence, _, _ = create_analyzers()

    result = confidence.calculate_pace(
        "I have Python and SQL skills.",
        10
    )

    assert result["words_per_minute"] == 36.0


def test_positive_sentiment():

    _, sentiment, _ = create_analyzers()

    result = sentiment.analyze(
        "I am excited and motivated to learn."
    )

    assert result["sentiment"] == "positive"


def test_negative_sentiment():

    _, sentiment, _ = create_analyzers()

    result = sentiment.analyze(
        "I am worried about this problem."
    )

    assert result["sentiment"] == "negative"


def test_neutral_sentiment():

    _, sentiment, _ = create_analyzers()

    result = sentiment.analyze(
        "I have two years of experience."
    )

    assert result["sentiment"] == "neutral"


def test_contradiction_detection():

    _, _, behavioral = create_analyzers()

    result = behavioral.detect_contradiction(
        {
            "experience_years": 1
        },
        "I have two years of experience."
    )

    assert result is True


def test_behavioral_analysis():

    _, _, behavioral = create_analyzers()

    result = behavioral.analyze(
        {
            "answer_id": "TEST001",
            "question_id": "Q001",
            "question": "What skills do you have?",
            "transcript": (
                "I am confident with Python and SQL."
            ),
            "duration_seconds": 8,
            "expected_information": {
                "skills": ["Python", "SQL"]
            }
        }
    )

    assert "confidence_analysis" in result
    assert "sentiment_analysis" in result
    assert "communication_strength" in result