import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day30_screening_system_testing"
    / "src"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)

from optimization import (
    optimize_decision,
    reduce_false_rejection
)


def test_valid_high_score():

    result = optimize_decision(
        "skills",
        "valid",
        85
    )

    assert result == "accept"


def test_medium_score_review():

    result = optimize_decision(
        "experience",
        "valid",
        60
    )

    assert result == "review"


def test_vague_answer_clarification():

    result = optimize_decision(
        "unknown",
        "vague",
        30
    )

    assert result == "clarify"


def test_off_topic_follow_up():

    result = optimize_decision(
        "unknown",
        "off_topic",
        20
    )

    assert result == "follow_up"


def test_false_rejection_reduction():

    result = reduce_false_rejection(
        "skills",
        "valid",
        45
    )

    assert result == "review"