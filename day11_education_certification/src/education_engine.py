import json
from pathlib import Path

from .education_parser import parse_education_section
from .certification_parser import extract_certifications
from .education_relevance import calculate_education_relevance


def load_resume(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def process_resume(
    input_path,
    output_path,
    target_role="data analyst",
):
    resume = load_resume(input_path)

    segmentation = resume.get(
        "segmentation",
        {},
    )

    sections = segmentation.get(
        "sections",
        {},
    )

    education_text = sections.get(
        "EDUCATION",
        "",
    )

    certification_text = sections.get(
        "CERTIFICATIONS",
        "",
    )

    education = parse_education_section(
        education_text
    )

    certifications = extract_certifications(
        certification_text
    )

    relevance = calculate_education_relevance(
        education,
        target_role,
    )

    result = {
        "source_file": resume.get(
            "source_file",
            Path(input_path).name,
        ),
        "status": "success",
        "academic_profile": {
            "education": education,
            "certifications": certifications,
            "education_relevance": relevance,
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
    target_role="data analyst",
):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    files = list(
        input_dir.glob("*.json")
    )

    results = []

    for file_path in files:
        output_path = (
            output_dir / file_path.name
        )

        result = process_resume(
            file_path,
            output_path,
            target_role,
        )

        results.append(result)

    return results