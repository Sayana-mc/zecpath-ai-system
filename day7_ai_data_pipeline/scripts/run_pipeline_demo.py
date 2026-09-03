import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.metadata import create_metadata
from src.storage import (
    save_resume,
    save_parsed_profile,
    save_ats_score,
    save_screening_report,
    save_interview_result,
)


BASE_DIR = PROJECT_ROOT / "examples" / "demo_storage"


def main():

    candidate_id = "CAND001"
    job_id = "JD001"
    model_version = "v1.0"

    metadata = create_metadata(
        candidate_id=candidate_id,
        job_id=job_id,
        model_version=model_version,
    )

    resume = {
        **metadata,
        "file_name": "candidate_resume.pdf",
        "file_type": "pdf",
        "raw_text": "Python developer with SQL and FastAPI experience."
    }

    parsed_profile = {
        **metadata,
        "name": "Demo Candidate",
        "skills": [
            "Python",
            "SQL",
            "FastAPI",
            "Git"
        ],
        "experience_years": 1,
        "education": "M.Sc Data Science"
    }

    ats_score = {
        **metadata,
        "score": 85,
        "matched_skills": [
            "Python",
            "SQL",
            "FastAPI"
        ],
        "missing_skills": [
            "Django"
        ]
    }

    screening_report = {
        **metadata,
        "recommendation": "Shortlist",
        "reason": "Candidate meets the major technical requirements."
    }

    interview_result = {
        **metadata,
        "technical_score": 88,
        "communication_score": 82,
        "overall_score": 85,
        "result": "Pass"
    }

    save_resume(
        resume,
        BASE_DIR
    )

    save_parsed_profile(
        parsed_profile,
        BASE_DIR
    )

    save_ats_score(
        ats_score,
        BASE_DIR
    )

    save_screening_report(
        screening_report,
        BASE_DIR
    )

    save_interview_result(
        interview_result,
        BASE_DIR
    )

    print("Day 7 AI data pipeline demo completed successfully.")
    print(f"Storage location: {BASE_DIR}")


if __name__ == "__main__":
    main()