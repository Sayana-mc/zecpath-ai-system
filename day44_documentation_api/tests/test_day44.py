import json
from pathlib import Path

from day44_documentation_api.api.api_models import (
    ScreeningRequest,
    InterviewEvaluationRequest
)

BASE_DIR = Path(__file__).resolve().parents[1]


def test_api_config_exists():
    config_path = BASE_DIR / "config" / "api_config.json"
    assert config_path.exists()


def test_api_config_valid_json():
    config_path = BASE_DIR / "config" / "api_config.json"

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["api_version"] == "v1"
    assert data["service_name"] == "hr-interview-ai"


def test_screening_request_model():
    request = ScreeningRequest(
        candidate_id="C001",
        role="Data Analyst",
        responses=[
            {
                "question_id": "Q001",
                "response": "I know Python and SQL."
            }
        ]
    )

    assert request.candidate_id == "C001"
    assert request.role == "Data Analyst"
    assert len(request.responses) == 1


def test_interview_request_model():
    request = InterviewEvaluationRequest(
        candidate_id="C001",
        question_id="Q001",
        question="Tell me about yourself.",
        response="I am a data science graduate."
    )

    assert request.candidate_id == "C001"
    assert request.question_id == "Q001"
    assert request.response


def test_candidate_sample_exists():
    path = BASE_DIR / "data" / "sample_candidate.json"
    assert path.exists()


def test_screening_request_example_exists():
    path = BASE_DIR / "examples" / "screening_request.json"
    assert path.exists()


def test_screening_response_example_exists():
    path = BASE_DIR / "examples" / "screening_response.json"
    assert path.exists()


def test_architecture_document_exists():
    path = BASE_DIR / "docs" / "hr_ai_architecture.md"
    assert path.exists()


def test_api_document_exists():
    path = BASE_DIR / "docs" / "api_specification.md"
    assert path.exists()


def test_developer_handbook_exists():
    path = BASE_DIR / "docs" / "developer_handbook.md"
    assert path.exists()


def test_troubleshooting_document_exists():
    path = BASE_DIR / "docs" / "troubleshooting.md"
    assert path.exists()