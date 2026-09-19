import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day31_edge_case_failure_handling"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))


from edge_case_handler import EdgeCaseHandler
from retry_manager import RetryManager
from clarification_manager import ClarificationManager


def test_missing_answer():

    handler = EdgeCaseHandler()

    result = handler.analyze(
        "",
        confidence=0.95
    )

    assert result.case_type == "missing_answer"
    assert result.action == "clarify"
    assert result.retry_allowed is True


def test_poor_audio():

    handler = EdgeCaseHandler()

    result = handler.analyze(
        "I have Python experience.",
        confidence=0.30
    )

    assert result.case_type == "poor_audio"
    assert result.action == "retry"


def test_background_noise():

    handler = EdgeCaseHandler()

    result = handler.analyze(
        "I have two years of experience.",
        confidence=0.95,
        background_noise=True
    )

    assert result.case_type == "background_noise"
    assert result.action == "retry"


def test_language_mixing():

    handler = EdgeCaseHandler()

    result = handler.analyze(
        "Python aanu ente main skill.",
        confidence=0.95,
        language="mixed"
    )

    assert result.case_type == "language_mixing"
    assert result.action == "clarify"


def test_incomplete_answer():

    handler = EdgeCaseHandler()

    result = handler.analyze(
        "Python",
        confidence=0.95
    )

    assert result.case_type == "incomplete_answer"
    assert result.action == "clarify"


def test_normal_answer():

    handler = EdgeCaseHandler()

    result = handler.analyze(
        "I have two years of experience in data analysis.",
        confidence=0.95
    )

    assert result.case_type == "normal"
    assert result.action == "continue"


def test_retry_manager():

    manager = RetryManager(max_retries=2)

    result = manager.get_action(0)

    assert result["action"] == "retry"

    result = manager.get_action(2)

    assert result["action"] == "fallback"


def test_clarification_manager():

    manager = ClarificationManager()

    result = manager.clarify("missing_answer")

    assert result["action"] == "clarify"
    assert "answer" in result["message"].lower()