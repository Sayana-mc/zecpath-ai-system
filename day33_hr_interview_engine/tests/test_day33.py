import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT /
    "day33_hr_interview_engine" /
    "src"
)

sys.path.insert(0, str(SRC_DIR))

from question_generator import QuestionGenerator
from interview_state import InterviewState
from interview_flow import InterviewFlow


def test_question_generator():

    generator = QuestionGenerator()

    questions = generator.generate_questions(
        experience_level="fresher",
        role_type="technical"
    )

    assert len(questions) > 0


def test_fresher_questions():

    generator = QuestionGenerator()

    questions = generator.generate_questions(
        experience_level="fresher",
        role_type="technical"
    )

    assert any(
        q["experience_level"]
        in ["fresher", "both"]
        for q in questions
    )


def test_interview_state():

    state = InterviewState(
        "C001",
        "technical",
        "fresher"
    )

    state.capture_response(
        "HR001",
        "My answer",
        True
    )

    result = state.get_state()

    assert result["current_question_id"] == "HR001"
    assert result["response"] == "My answer"
    assert result["follow_up_eligible"] is True


def test_interview_flow():

    flow = InterviewFlow()

    assert flow.current_phase() == "introduction"

    flow.move_next()

    assert flow.current_phase() == "core_hr_questions"


def test_required_phases():

    flow = InterviewFlow()

    assert "introduction" in flow.PHASES
    assert "core_hr_questions" in flow.PHASES
    assert "role_based_evaluation" in flow.PHASES
    assert "closing" in flow.PHASES