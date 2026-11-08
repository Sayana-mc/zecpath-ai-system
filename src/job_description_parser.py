"""Conservative parser for explicitly labeled job-description sections."""

from __future__ import annotations

import re
from typing import Any


_HEADINGS = {
    "required_skills": {
        "required skills",
        "mandatory skills",
        "must have",
        "must-have skills",
        "requirements",
    },
    "preferred_skills": {
        "preferred skills",
        "desired skills",
        "nice to have",
        "nice-to-have skills",
    },
    "education": {"education", "educational qualification", "qualifications"},
    "experience": {
        "experience",
        "minimum experience",
        "experience required",
        "years of experience",
    },
    "responsibilities": {"responsibilities", "what you will do", "duties"},
}
_HEADING_LOOKUP = {
    heading: field for field, headings in _HEADINGS.items() for heading in headings
}
_EXPERIENCE_VALUE = re.compile(
    r"(?<!\d)(\d+(?:\.\d+)?)\s*(?:\+|years?|yrs?)", re.IGNORECASE
)
_EXPERIENCE_RANGE = re.compile(
    r"(?<!\d)(\d+(?:\.\d+)?)\s*[-–]\s*\d+(?:\.\d+)?\s*(?:years?|yrs?)",
    re.IGNORECASE,
)


def _heading(line: str) -> tuple[str | None, str]:
    cleaned = line.strip().strip(":").strip()
    if ":" in line:
        possible, remainder = line.split(":", 1)
        key = possible.strip().casefold()
        if key in _HEADING_LOOKUP:
            return _HEADING_LOOKUP[key], remainder.strip()
    key = cleaned.casefold()
    if key in _HEADING_LOOKUP:
        return _HEADING_LOOKUP[key], ""
    return None, ""


def _items(lines: list[str]) -> list[str]:
    result: list[str] = []
    for line in lines:
        for item in re.split(r"[,;]", line):
            cleaned = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", item).strip()
            if cleaned and cleaned.casefold() not in {value.casefold() for value in result}:
                result.append(cleaned)
    return result


def parse_job_description(description: str) -> dict[str, Any]:
    normalized = description.replace("\r\n", "\n").replace("\r", "\n")
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in normalized.splitlines():
        field, inline = _heading(line)
        if field:
            current = field
            sections.setdefault(field, [])
            if inline:
                sections[field].append(inline)
        elif current and line.strip():
            sections[current].append(line.strip())

    required_skills = _items(sections.get("required_skills", []))
    preferred_skills = _items(sections.get("preferred_skills", []))
    education = " ".join(sections.get("education", [])).strip() or None
    experience_text = " ".join(sections.get("experience", [])).strip()
    experience_match = _EXPERIENCE_RANGE.search(experience_text)
    if experience_match is None:
        experience_match = _EXPERIENCE_VALUE.search(experience_text)
    minimum_years_experience = (
        float(experience_match.group(1)) if experience_match else None
    )
    warnings = []
    if not required_skills:
        warnings.append(
            "No explicitly labeled required-skills section was found; enter required skills manually."
        )
    if experience_text and experience_match is None:
        warnings.append(
            "Experience wording was found but could not be converted to a minimum-year value."
        )
    if not experience_text:
        warnings.append("No explicitly labeled experience requirement was found.")
    if not education:
        warnings.append("No explicitly labeled education requirement was found.")

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "minimum_education": education,
        "minimum_years_experience": minimum_years_experience,
        "evidence": {
            "required_skills": sections.get("required_skills", []),
            "preferred_skills": sections.get("preferred_skills", []),
            "education": sections.get("education", []),
            "experience": sections.get("experience", []),
            "responsibilities": sections.get("responsibilities", []),
        },
        "warnings": warnings,
        "method": "explicit_heading_rules_v1",
        "human_confirmation_required": True,
    }
