import json
from pathlib import Path

from .section_classifier import detect_section_heading


SUPPORTED_SECTIONS = [
    "SKILLS",
    "WORK EXPERIENCE",
    "EDUCATION",
    "CERTIFICATIONS",
    "PROJECTS",
]


def split_into_lines(text):
    """
    Split resume text into clean lines.
    """

    if not text:
        return []

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return lines


def segment_resume(text):
    """
    Segment resume text into standard sections.
    """

    lines = split_into_lines(text)

    sections = {
        section: []
        for section in SUPPORTED_SECTIONS
    }

    sections["OTHER"] = []

    current_section = "OTHER"

    detected_headings = []

    for line in lines:

        detected_section = detect_section_heading(line)

        if detected_section:

            current_section = detected_section

            detected_headings.append({
                "heading": line,
                "section": detected_section
            })

            continue

        sections[current_section].append(line)

    cleaned_sections = {}

    for section, content in sections.items():

        cleaned_sections[section] = "\n".join(content).strip()

    return {
        "sections": cleaned_sections,
        "detected_headings": detected_headings
    }


def load_resume_json(file_path):
    """
    Load a Day 5 extracted resume JSON.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def process_resume_file(
    input_path,
    output_path
):
    """
    Process one extracted resume JSON.
    """

    resume = load_resume_json(input_path)

    text = resume.get("cleaned_text", "")

    if not text:
        text = resume.get("raw_text", "")

    segmentation = segment_resume(text)

    result = {
        "source_file": resume.get(
            "source_file",
            Path(input_path).name
        ),
        "file_type": resume.get(
            "file_type",
            Path(input_path).suffix.lower()
        ),
        "status": "success",
        "segmentation": segmentation
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
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


def process_all_resumes(
    input_dir,
    output_dir
):
    """
    Process all extracted resume JSON files.
    """

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    results = []

    files = list(
        input_dir.glob("*.json")
    )

    for file_path in files:

        output_path = (
            output_dir /
            file_path.name
        )

        result = process_resume_file(
            file_path,
            output_path
        )

        results.append(result)

    return results