import sys
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day26_screening_scoring_engine"
    / "src"
)

CONFIG_PATH = (
    PROJECT_ROOT
    / "day26_screening_scoring_engine"
    / "config"
    / "scoring_parameters.json"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)

from question_scorer import QuestionScorer
from scoring_engine import ScreeningScoringEngine


def load_config():

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def test_clarity_score():

    scorer = QuestionScorer(
        load_config()
    )

    score = scorer.score_clarity(
        "I have experience with Python and SQL."
    )

    assert 0 <= score <= 5


def test_relevance_score():

    scorer = QuestionScorer(
        load_config()
    )

    score = scorer.score_relevance(
        "I have experience with Python and SQL.",
        "skills"
    )

    assert score >= 4


def test_completeness_score():

    scorer = QuestionScorer(
        load_config()
    )

    score = scorer.score_completeness(
        "I have experience with Python, SQL and Power BI.",
        "skills"
    )

    assert 0 <= score <= 5


def test_consistency_score():

    scorer = QuestionScorer(
        load_config()
    )

    score = scorer.score_consistency(
        "I have one year of experience.",
        {
            "experience_years": 1
        },
        "experience"
    )

    assert score == 5


def test_question_score():

    scorer = QuestionScorer(
        load_config()
    )

    result = scorer.calculate_score(
        "I have experience with Python and SQL.",
        "skills",
        {
            "skills": [
                "Python",
                "SQL"
            ]
        }
    )

    assert "parameter_scores" in result
    assert "normalized_score" in result
    assert 0 <= result["normalized_score"] <= 100


def test_candidate_score():

    engine = ScreeningScoringEngine(
        load_config()
    )

    answers = [
        {
            "answer_id": "A001",
            "candidate_id": "C001",
            "question_id": "Q001",
            "question": "What skills do you have?",
            "answer": "I know Python and SQL.",
            "expected_intent": "skills",
            "previous_information": {
                "skills": [
                    "Python",
                    "SQL"
                ]
            }
        },
        {
            "answer_id": "A002",
            "candidate_id": "C001",
            "question_id": "Q002",
            "question": "When can you join?",
            "answer": "I can join immediately.",
            "expected_intent": "availability",
            "previous_information": {
                "availability": "immediate"
            }
        }
    ]

    result = engine.score_candidate(
        answers
    )

    assert result["candidate_id"] == "C001"
    assert result["questions_evaluated"] == 2
    assert 0 <= result["total_screening_score"] <= 100
    assert len(result["question_scores"]) == 2


def test_explainable_output():

    engine = ScreeningScoringEngine(
        load_config()
    )

    answer = {
        "answer_id": "A001",
        "candidate_id": "C001",
        "question_id": "Q001",
        "question": "What skills do you have?",
        "answer": "I have experience with Python and SQL.",
        "expected_intent": "skills",
        "previous_information": {
            "skills": [
                "Python",
                "SQL"
            ]
        }
    }

    result = engine.score_question(
        answer
    )

    assert "explanation" in result
    assert isinstance(
        result["explanation"],
        list
    )