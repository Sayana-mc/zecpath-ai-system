"""
Day 9 - Skill Extraction Engine
Main processing module.
"""

import json
from pathlib import Path

from .skill_extractor import (
    extract_skills_from_sections
)


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "input"

OUTPUT_DIR = BASE_DIR / "output"


def process_resume(
    input_file,
    output_file
):
    """
    Process one labeled resume JSON.
    """

    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as file:

        resume = json.load(file)

    segmentation = resume.get(
        "segmentation",
        {}
    )

    sections = segmentation.get(
        "sections",
        {}
    )

    skills = extract_skills_from_sections(
        sections
    )

    result = {

        "source_file": resume.get(
            "source_file",
            input_file.name
        ),

        "status": "success",

        "skill_extraction": {

            "total_skills": len(skills),

            "skills": skills

        }

    }

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    return result


def process_all_resumes():

    files = list(
        INPUT_DIR.glob("*.json")
    )

    print(
        f"Found {len(files)} resume files."
    )

    successful = 0

    for file_path in files:

        output_path = (
            OUTPUT_DIR /
            file_path.name
        )

        print(
            f"Processing: {file_path.name}"
        )

        try:

            process_resume(
                file_path,
                output_path
            )

            successful += 1

            print(
                "  SUCCESS"
            )

        except Exception as error:

            print(
                f"  FAILED: {error}"
            )

    print()
    print(
        f"Processed resumes: {len(files)}"
    )

    print(
        f"Successful: {successful}"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )


if __name__ == "__main__":

    process_all_resumes()