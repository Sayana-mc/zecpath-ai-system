"""Extract structured resume details using the existing Day 8-11 parsers."""

import re
from typing import Any

from day11_education_certification.src.certification_parser import (
    extract_certifications,
)
from day10_experience_relevance.src.experience_parser import (
    calculate_total_experience,
    parse_experience_section,
)
from day11_education_certification.src.education_parser import (
    parse_education_section,
)
from day8_resume_section_segmentation.src.segmentation_engine import (
    segment_resume,
)
from day9_skill_extraction.src.skill_extractor import (
    deduplicate_skills,
    extract_skills_from_sections,
    extract_skills_from_text,
)


_PERSONAL_LABEL = re.compile(
    r"^\s*(?:"
    r"name|candidate name|email|e-mail|phone|telephone|mobile|"
    r"date of birth|birth date|dob|age|gender|sex|marital status|"
    r"religion|nationality|citizenship|address|photo|photograph"
    r")\s*[:\-]",
    re.IGNORECASE,
)
_EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_STANDALONE_PHONE = re.compile(r"^\s*[+()\d][\d\s().+-]{6,}\s*$")
_PLAIN_NAME = re.compile(
    r"^[A-Z][a-z]+(?:[-'][A-Z]?[a-z]+)?(?:\s+[A-Z][a-z]+){1,3}$"
)


def build_resume_matching_text(
    resume_text: str,
    resume_data: dict[str, Any] | None = None,
) -> str:
    """Build matching input without contact details or labeled personal attributes."""
    data = resume_data or {}
    segmentation = data.get("sections", {})
    sections = (
        segmentation.get("sections", {})
        if isinstance(segmentation, dict)
        else {}
    )
    if not isinstance(sections, dict):
        sections = {}
    cleaned_lines = []
    section_texts = (
        sections.items()
        if sections
        else ((None, resume_text),)
    )
    for section_name, section_text in section_texts:
        if not isinstance(section_text, str):
            continue
        for index, line in enumerate(section_text.splitlines()):
            stripped = line.strip()
            if (
                not stripped
                or _PERSONAL_LABEL.match(stripped)
                or _STANDALONE_PHONE.match(stripped)
            ):
                continue
            if (
                index < 3
                and section_name in (None, "OTHER")
                and _PLAIN_NAME.fullmatch(stripped)
            ):
                continue
            cleaned_lines.append(_EMAIL.sub("[REDACTED]", stripped))
    return "\n".join(cleaned_lines).strip()


def extract_resume_data(resume_text: str) -> dict[str, Any]:
    segmentation = segment_resume(resume_text)
    sections = segmentation["sections"]
    has_targeted_sections = any(
        sections.get(section)
        for section in (
            "SKILLS",
            "WORK EXPERIENCE",
            "EDUCATION",
            "CERTIFICATIONS",
            "PROJECTS",
        )
    )
    skills = extract_skills_from_text(resume_text)
    if has_targeted_sections:
        safe_sections = {
            section: build_resume_matching_text(
                section_text,
                {"sections": {"sections": {section: section_text}}},
            )
            for section, section_text in sections.items()
        }
        skills = extract_skills_from_sections(safe_sections)
        skills.extend(
            extract_skills_from_text(safe_sections.get("OTHER", ""), source="OTHER")
        )
        skills = deduplicate_skills(skills)

    experience_text = sections.get("WORK EXPERIENCE") or resume_text
    education_text = sections.get("EDUCATION") or resume_text
    certification_text = sections.get("CERTIFICATIONS") or resume_text
    experience = parse_experience_section(experience_text)
    education = parse_education_section(education_text)
    return {
        "extraction_method": (
            "day8_sections_day9_skills_day10_experience_day11_education_certifications"
        ),
        "skills": [item["skill"] for item in skills],
        "skill_details": skills,
        "education": education,
        "certifications": extract_certifications(certification_text),
        "experience": experience,
        "experience_years": (
            calculate_total_experience(experience) if experience else None
        ),
        "sections": segmentation,
    }
