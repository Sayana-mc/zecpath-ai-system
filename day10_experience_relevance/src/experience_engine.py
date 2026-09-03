import json
from pathlib import Path

from .experience_parser import (
    parse_experience_section,
    calculate_total_experience,
    detect_gaps,
    detect_overlaps,
)

from .relevance_scorer import (
    calculate_relevance_score,
)


def load_json(file_path):
    """Load JSON data."""

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def process_resume(
    input_path,
    output_path,
    target_role="Data Analyst",
):
    """Process one segmented resume."""

    resume = load_json(
        input_path
    )

    sections = (
        resume
        .get("segmentation", {})
        .get("sections", {})
    )

    experience_text = sections.get(
        "WORK EXPERIENCE",
        "",
    )

    experiences = parse_experience_section(
        experience_text
    )

    total_experience = (
        calculate_total_experience(
            experiences
        )
    )

    gaps = detect_gaps(
        experiences
    )

    overlaps = detect_overlaps(
        experiences
    )

    relevance = calculate_relevance_score(
        experiences,
        target_role,
    )

    result = {
        "source_file": resume.get(
            "source_file",
            Path(input_path).name,
        ),
        "status": "success",
        "experience_analysis": {
            "total_experience_years": total_experience,
            "employment_count": len(
                experiences
            ),
            "employment_history": experiences,
            "employment_gaps": gaps,
            "overlapping_roles": overlaps,
            "relevance_analysis": relevance,
        },
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return result


def process_all_resumes(
    input_dir,
    output_dir,
    target_role="Data Analyst",
):
    """Process all Day 8 segmented resumes."""

    input_dir = Path(
        input_dir
    )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    files = list(
        input_dir.glob("*.json")
    )

    results = []

    print(
        f"Found {len(files)} resume files."
    )

    for file_path in files:

        print(
            f"Processing: {file_path.name}"
        )

        output_path = (
            output_dir
            / file_path.name
        )

        try:

            result = process_resume(
                file_path,
                output_path,
                target_role,
            )

            results.append(result)

            print("  SUCCESS")

        except Exception as error:

            print(
                f"  ERROR: {error}"
            )

    return results