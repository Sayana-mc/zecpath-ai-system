import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day40_hr_interview_simulation"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))

from simulation_engine import HRInterviewSimulator
from evaluator import HREvaluator


def test_confident_candidate():

    simulator = HRInterviewSimulator()

    result = simulator.simulate(
        "confident"
    )

    assert result["candidate_type"] == "confident"
    assert result["total_questions"] == 6


def test_hesitant_candidate():

    simulator = HRInterviewSimulator()

    result = simulator.simulate(
        "hesitant"
    )

    assert result["candidate_type"] == "hesitant"


def test_inexperienced_candidate():

    simulator = HRInterviewSimulator()

    result = simulator.simulate(
        "inexperienced"
    )

    assert result["candidate_type"] == "inexperienced"


def test_overqualified_candidate():

    simulator = HRInterviewSimulator()

    result = simulator.simulate(
        "overqualified"
    )

    assert result["candidate_type"] == "overqualified"


def test_all_candidate_types():

    simulator = HRInterviewSimulator()

    results = simulator.simulate_all()

    assert len(results) == 4


def test_response_evaluation():

    evaluator = HREvaluator()

    response = {
        "question_id": "Q001",
        "answer": (
            "I am a data science graduate "
            "with experience in Python and SQL."
        )
    }

    result = evaluator.evaluate_response(
        response
    )

    assert "score" in result
    assert 0 <= result["score"] <= 100


def test_session_evaluation():

    simulator = HRInterviewSimulator()
    evaluator = HREvaluator()

    session = simulator.simulate(
        "confident"
    )

    result = evaluator.evaluate_session(
        session
    )

    assert "overall_ai_score" in result
    assert len(result["question_scores"]) == 6


def test_score_comparison():

    simulator = HRInterviewSimulator()
    evaluator = HREvaluator()

    session = simulator.simulate(
        "confident"
    )

    result = evaluator.evaluate_session(
        session
    )

    assert result["overall_ai_score"] >= 0
    assert result["overall_ai_score"] <= 100