import json
from pathlib import Path


STORAGE_DIRECTORIES = {
    "resumes": "resumes",
    "parsed_profiles": "parsed_profiles",
    "ats_scores": "ats_scores",
    "screening_reports": "screening_reports",
    "interview_results": "interview_results",
}


def _save_json(data, directory_name, base_dir):
    """
    Save a dictionary as a JSON file inside the specified storage directory.
    """

    base_path = Path(base_dir)

    directory = (
        base_path /
        STORAGE_DIRECTORIES[directory_name]
    )

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    candidate_id = data.get(
        "candidate_id",
        "unknown_candidate"
    )

    job_id = data.get(
        "job_id",
        "general"
    )

    filename = f"{candidate_id}_{job_id}.json"

    output_file = directory / filename

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_file


def save_resume(data, base_dir="storage"):
    """
    Store raw resume information.
    """

    return _save_json(
        data,
        "resumes",
        base_dir
    )


def save_parsed_profile(data, base_dir="storage"):
    """
    Store parsed candidate profile.
    """

    return _save_json(
        data,
        "parsed_profiles",
        base_dir
    )


def save_ats_score(data, base_dir="storage"):
    """
    Store ATS score.
    """

    return _save_json(
        data,
        "ats_scores",
        base_dir
    )


def save_screening_report(data, base_dir="storage"):
    """
    Store screening report.
    """

    return _save_json(
        data,
        "screening_reports",
        base_dir
    )


def save_interview_result(data, base_dir="storage"):
    """
    Store interview result.
    """

    return _save_json(
        data,
        "interview_results",
        base_dir
    )