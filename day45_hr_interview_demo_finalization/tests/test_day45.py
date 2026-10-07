import json

from day45_hr_interview_demo_finalization.src.final_hr_scoring_engine import (
    FinalHRScoringEngine
)
from day45_hr_interview_demo_finalization.src.interview_evaluator import (
    InterviewEvaluator
)
from day45_hr_interview_demo_finalization.src.recommendation_engine import (
    RecommendationEngine
)


def test_question_score():
    engine = FinalHRScoringEngine()

    result = engine.calculate_question_score(
        80, 90, 85, 95
    )

    assert result["overall_score"] == 87.5


def test_candidate_score():
    engine = FinalHRScoringEngine()

    scores = [
        {"overall_score": 80},
        {"overall_score": 90}
    ]

    assert engine.calculate_candidate_score(scores) == 85


def test_empty_candidate_score():
    engine = FinalHRScoringEngine()

    assert engine.calculate_candidate_score([]) == 0.0


def test_response_evaluation():
    evaluator = InterviewEvaluator()

    result = evaluator.evaluate_response(
        "I have experience with Python and SQL."
    )

    assert result["relevance"] > 0


def test_empty_response():
    evaluator = InterviewEvaluator()

    result = evaluator.evaluate_response("")

    assert result["relevance"] == 0


def test_high_fit():
    engine = RecommendationEngine()

    result = engine.get_recommendation(85)

    assert result["recommendation"] == "HIGH_FIT"


def test_moderate_fit():
    engine = RecommendationEngine()

    result = engine.get_recommendation(70)

    assert result["recommendation"] == "MODERATE_FIT"


def test_low_fit():
    engine = RecommendationEngine()

    result = engine.get_recommendation(55)

    assert result["recommendation"] == "LOW_FIT"


def test_not_recommended():
    engine = RecommendationEngine()

    result = engine.get_recommendation(45)

    assert result["recommendation"] == "NOT_RECOMMENDED"