import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day38_aptitude_logic_design"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))


from aptitude_engine import AptitudeEngine
from logical_scoring import LogicalReasoningScorer
from scenario_evaluator import ScenarioEvaluator


def test_question_bank():

    engine = AptitudeEngine()

    questions = engine.get_questions()

    assert len(questions) >= 3


def test_get_question():

    engine = AptitudeEngine()

    question = engine.get_question("APT001")

    assert question is not None
    assert question["category"] == "logical_reasoning"


def test_missing_question():

    engine = AptitudeEngine()

    result = engine.evaluate_answer(
        "UNKNOWN",
        "test answer"
    )

    assert result["status"] == "unknown_question"


def test_logical_score():

    scorer = LogicalReasoningScorer()

    result = scorer.calculate_score(
        "First calculate the value, then check the result. "
        "Therefore the answer is correct."
    )

    assert result["normalized_score"] > 0


def test_problem_solving_score():

    scorer = LogicalReasoningScorer()

    result = scorer.score_problem_solving(
        "I would analyze the issue, solve it and test the solution."
    )

    assert result == 5


def test_scenario_evaluation():

    evaluator = ScenarioEvaluator()

    result = evaluator.evaluate(
        "I would identify the issue, prioritize it, "
        "communicate with the team and solve the problem."
    )

    assert result["overall_score"] > 0


def test_empty_scenario():

    evaluator = ScenarioEvaluator()

    result = evaluator.evaluate("")

    assert result["overall_score"] == 0


def test_question_filter():

    engine = AptitudeEngine()

    questions = engine.get_questions(
        "situational_judgment"
    )

    assert len(questions) >= 1