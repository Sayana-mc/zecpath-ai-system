import re


SECTION_MAPPING = {
    "summary": "SUMMARY",
    "professional summary": "SUMMARY",
    "profile": "SUMMARY",
    "career objective": "SUMMARY",
    "objective": "SUMMARY",

    "skills": "SKILLS",
    "technical skills": "SKILLS",
    "key skills": "SKILLS",
    "core skills": "SKILLS",

    "experience": "EXPERIENCE",
    "work experience": "EXPERIENCE",
    "professional experience": "EXPERIENCE",
    "employment history": "EXPERIENCE",

    "education": "EDUCATION",
    "academic background": "EDUCATION",
    "educational qualifications": "EDUCATION",

    "certifications": "CERTIFICATIONS",
    "certificates": "CERTIFICATIONS",

    "projects": "PROJECTS",
    "academic projects": "PROJECTS",

    "achievements": "ACHIEVEMENTS",

    "languages": "LANGUAGES",
}


def normalize_section_heading(line):
    """
    Normalize common resume section headings.
    """

    cleaned = line.strip().lower()

    cleaned = re.sub(r"[:\-]+$", "", cleaned)

    return SECTION_MAPPING.get(cleaned, line.strip())


def normalize_sections(text):
    """
    Normalize section headings line by line.
    """

    lines = []

    for line in text.split("\n"):

        normalized = normalize_section_heading(line)

        lines.append(normalized)

    return "\n".join(lines)