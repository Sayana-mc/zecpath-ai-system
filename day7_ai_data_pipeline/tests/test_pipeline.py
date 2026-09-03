from pathlib import Path

from src.metadata import create_metadata
from src.storage import (
    save_resume,
    save_parsed_profile,
    save_ats_score,
    save_screening_report,
    save_interview_result,
)


def test_metadata_creation():
    metadata = create_metadata(
        candidate_id="CAND001",
        job_id="JD001",
        model_version="v1.0",
    )

    assert metadata["candidate_id"] == "CAND001"
    assert metadata["job_id"] == "JD001"
    assert metadata["model_version"] == "v1.0"
    assert "timestamp" in metadata


def test_resume_storage(tmp_path):
    data = {
        "candidate_id": "CAND001",
        "file_name": "resume.pdf",
        "raw_text": "Python developer with SQL experience.",
    }

    result = save_resume(
        data,
        base_dir=tmp_path
    )

    assert result.exists()


def test_profile_storage(tmp_path):
    data = {
        "candidate_id": "CAND001",
        "name": "Test Candidate",
        "skills": ["Python", "SQL"],
    }

    result = save_parsed_profile(
        data,
        base_dir=tmp_path
    )

    assert result.exists()


def test_ats_score_storage(tmp_path):
    data = {
        "candidate_id": "CAND001",
        "job_id": "JD001",
        "score": 85,
    }

    result = save_ats_score(
        data,
        base_dir=tmp_path
    )

    assert result.exists()


def test_screening_report_storage(tmp_path):
    data = {
        "candidate_id": "CAND001",
        "job_id": "JD001",
        "recommendation": "Shortlist",
    }

    result = save_screening_report(
        data,
        base_dir=tmp_path
    )

    assert result.exists()


def test_interview_result_storage(tmp_path):
    data = {
        "candidate_id": "CAND001",
        "job_id": "JD001",
        "score": 90,
        "result": "Pass",
    }

    result = save_interview_result(
        data,
        base_dir=tmp_path
    )

    assert result.exists()