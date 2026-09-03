import re
from typing import List, Dict

from .education_patterns import CERTIFICATION_CATEGORIES


def normalize_certification_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip()

    replacements = {
        "aws certified": "AWS Certified",
        "google cloud": "Google Cloud",
        "microsoft azure": "Microsoft Azure",
        "power bi": "Power BI",
        "tableau": "Tableau",
        "python": "Python",
        "sql": "SQL",
        "pmp": "PMP",
        "scrum": "Scrum",
        "figma": "Figma",
    }

    lower_name = name.lower()

    for key, value in replacements.items():
        if key in lower_name:
            return value

    return name


def classify_certification(name: str) -> str:
    lower_name = name.lower()

    for category, keywords in CERTIFICATION_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in lower_name:
                return category

    return "OTHER"


def extract_certifications(text: str) -> List[Dict]:
    if not text:
        return []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    certifications = []

    for line in lines:
        lower_line = line.lower()

        is_certification = (
            "certificate" in lower_line
            or "certification" in lower_line
            or "certified" in lower_line
            or any(
                keyword.lower() in lower_line
                for keywords in CERTIFICATION_CATEGORIES.values()
                for keyword in keywords
            )
        )

        if not is_certification:
            continue

        name = normalize_certification_name(line)

        year_match = re.search(
            r"\b(?:19|20)\d{2}\b",
            line,
        )

        year = (
            int(year_match.group())
            if year_match
            else None
        )

        certifications.append(
            {
                "name": name,
                "category": classify_certification(name),
                "year": year,
            }
        )

    unique = []
    seen = set()

    for certification in certifications:
        key = certification["name"].lower()

        if key not in seen:
            seen.add(key)
            unique.append(certification)

    return unique