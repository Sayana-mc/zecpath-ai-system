import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day32_screening_system_finalization"
    / "src"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)

from screening_pipeline import ScreeningPipeline


def test_pipeline_creation():

    pipeline = ScreeningPipeline()

    assert pipeline is not None


def test_candidate_processing():

    pipeline = ScreeningPipeline()

    answers = {
        "Q001": "Python and SQL",
        "Q002": "I completed a data analyst internship.",
        "Q003": "I can join immediately.",
        "Q004": "I expect 4 LPA."
    }

    result = pipeline.process_candidate(
        "C001",
        answers
    )

    assert result["candidate_id"] == "C001"
    assert result["status"] == "completed"


def test_question_processing():

    pipeline = ScreeningPipeline()

    result = pipeline.process_candidate(
        "C002",
        {
            "Q001": "Python and SQL",
            "Q002": "Data analyst internship",
            "Q003": "Immediately",
            "Q004": "4 LPA"
        }
    )

    assert result["total_questions"] == 4
    assert len(result["answers"]) == 4


def test_missing_answer():

    pipeline = ScreeningPipeline()

    result = pipeline.process_candidate(
        "C003",
        {
            "Q001": "",
            "Q002": "Internship experience",
            "Q003": "Immediately",
            "Q004": "4 LPA"
        }
    )

    first_answer = result["answers"][0]

    assert first_answer["status"] == "missing"