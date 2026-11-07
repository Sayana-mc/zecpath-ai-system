"""Extract structured resume details using the existing Day 9-11 parsers."""

from day10_experience_relevance.src.experience_parser import (
    calculate_total_experience,
    parse_experience_section,
)
from day11_education_certification.src.education_parser import (
    parse_education_section,
)
from day9_skill_extraction.src.skill_extractor import extract_skills_from_text


def extract_resume_data(resume_text: str) -> dict:
    skills = extract_skills_from_text(resume_text)
    experience = parse_experience_section(resume_text)
    education = parse_education_section(resume_text)
    return {
        "extraction_method": "day9_skill_day10_experience_day11_education",
        "skills": [item["skill"] for item in skills],
        "skill_details": skills,
        "education": education,
        "experience": experience,
        "experience_years": (
            calculate_total_experience(experience) if experience else None
        ),
    }
