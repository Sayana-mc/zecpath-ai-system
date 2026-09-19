import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT /
    "day29_ai_conversation_flow" /
    "src"
)

sys.path.insert(0, str(SRC_DIR))


from conversation_flow import ConversationFlow
from decision_tree import ConversationDecisionTree


def test_start_conversation():

    flow = ConversationFlow()

    result = flow.start()

    assert result["state"] == "asking"
    assert result["action"] == "ask_question"


def test_silence_handling():

    flow = ConversationFlow()

    flow.start()

    result = flow.process_response("")

    assert result["action"] == "handle_silence"


def test_confusion_handling():

    flow = ConversationFlow()

    flow.start()

    result = flow.process_response(
        "I don't understand the question."
    )

    assert result["action"] == "clarify"


def test_follow_up_trigger():

    flow = ConversationFlow()

    flow.start()

    result = flow.process_response(
        "Python"
    )

    assert result["action"] == "follow_up"


def test_valid_response():

    flow = ConversationFlow()

    flow.start()

    result = flow.process_response(
        "I have two years of experience working with Python and SQL."
    )

    assert result["action"] == "continue"


def test_decision_tree_silence():

    tree = ConversationDecisionTree()

    result = tree.decide("")

    assert result["condition"] == "silence"


def test_decision_tree_confusion():

    tree = ConversationDecisionTree()

    result = tree.decide(
        "I don't understand"
    )

    assert result["condition"] == "confusion"


def test_decision_tree_follow_up():

    tree = ConversationDecisionTree()

    result = tree.decide(
        "Python"
    )

    assert result["next_action"] == "follow_up"