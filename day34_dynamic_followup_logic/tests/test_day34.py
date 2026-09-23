import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day34_dynamic_followup_logic"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))

from followup_engine import FollowUpEngine
from adaptive_questioning import AdaptiveQuestioning
from decision_tree import FollowUpDecisionTree


def test_incomplete_response():

    engine = FollowUpEngine()

    result = engine.detect_response_quality(
        "Yes"
    )

    assert result == "incomplete"


def test_vague_response():

    engine = FollowUpEngine()

    result = engine.detect_response_quality(
        "I don't know."
    )

    assert result == "vague"


def test_complete_response():

    engine = FollowUpEngine()

    result = engine.detect_response_quality(
        "I worked with my team and completed the project successfully."
    )

    assert result == "complete"


def test_clarification_trigger():

    engine = FollowUpEngine()

    result = engine.generate_followup(
        "Q001",
        "What are your strengths?",
        "Yes"
    )

    assert result["trigger"] == "clarification"


def test_example_trigger():

    engine = FollowUpEngine()

    result = engine.generate_followup(
        "Q002",
        "Tell me about your project.",
        "I don't know."
    )

    assert result["trigger"] == "example_based"


def test_adaptive_difficulty():

    engine = AdaptiveQuestioning()

    result = engine.determine_level(
        "I managed a complex project and solved multiple technical issues.",
        "high"
    )

    assert result == "advanced"


def test_decision_tree():

    tree = FollowUpDecisionTree()

    result = tree.decide(
        "vague",
        "normal"
    )

    assert result["action"] == "example_based"


def test_repeated_question():

    tree = FollowUpDecisionTree()

    result = tree.decide(
        "complete",
        "high",
        repeated=True
    )

    assert result["action"] == "move_forward"