import re
from typing import List, Dict

from .education_patterns import (
    DEGREE_PATTERNS,
    FIELD_NORMALIZATION,
)


def normalize_text(text: str) -> str:
    """
    Normalize whitespace and clean text.
    """
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def normalize_field(field: str) -> str:
    """
    Normalize field-of-study names.
    """
    if not field:
        return ""

    cleaned = normalize_text(field)
    key = cleaned.lower()

    if key in FIELD_NORMALIZATION:
        return FIELD_NORMALIZATION[key]

    return cleaned.title()


def detect_degree_type(text: str) -> str:
    """
    Detect degree level from education text.

    Returns:
        BACHELOR
        MASTER
        DOCTORATE
        DIPLOMA
        OTHER
    """

    if not text:
        return "OTHER"

    text_lower = normalize_text(text).lower()

    # IMPORTANT:
    # Check specific degree abbreviations first.
    # This prevents B.Sc / B.Tech etc. from being incorrectly
    # classified because of generic words.

    bachelor_patterns = [
        r"\bb\.?\s*sc\b",
        r"\bbachelor\b",
        r"\bb\.?\s*tech\b",
        r"\bb\.?\s*e\b",
        r"\bb\.?\s*a\b",
        r"\bb\.?\s*com\b",
        r"\bbba\b",
        r"\bbca\b",
        r"\bb\.?\s*des\b",
        r"\bbe\b",
        r"\bb\.?s\b",
    ]

    master_patterns = [
        r"\bm\.?\s*sc\b",
        r"\bmaster\b",
        r"\bm\.?\s*tech\b",
        r"\bm\.?\s*a\b",
        r"\bm\.?\s*com\b",
        r"\bmba\b",
        r"\bmca\b",
        r"\bm\.?\s*des\b",
        r"\bme\b",
    ]

    doctorate_patterns = [
        r"\bph\.?\s*d\b",
        r"\bdoctorate\b",
        r"\bdoctoral\b",
    ]

    diploma_patterns = [
        r"\bdiploma\b",
        r"\bpolytechnic\b",
        r"\bcertificate diploma\b",
    ]

    for pattern in bachelor_patterns:
        if re.search(pattern, text_lower):
            return "BACHELOR"

    for pattern in master_patterns:
        if re.search(pattern, text_lower):
            return "MASTER"

    for pattern in doctorate_patterns:
        if re.search(pattern, text_lower):
            return "DOCTORATE"

    for pattern in diploma_patterns:
        if re.search(pattern, text_lower):
            return "DIPLOMA"

    # Fallback to configured patterns
    for degree_type, patterns in DEGREE_PATTERNS.items():

        for pattern in patterns:

            if pattern.lower() in text_lower:
                return degree_type

    return "OTHER"


def extract_year(text: str):
    """
    Extract the latest valid year from education text.
    """

    if not text:
        return None

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    if not years:
        return None

    return int(years[-1])


def extract_field(text: str) -> str:
    """
    Extract field of study.
    """

    if not text:
        return ""

    text = normalize_text(text)

    patterns = [
        r"(?:in|major in|specialization in)\s+([A-Za-z& /-]+)",
        r"(?:science|arts|commerce)\s+in\s+([A-Za-z& /-]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            field = match.group(1)

            field = re.split(
                r"\b(?:from|at|university|college|institute)\b",
                field,
                flags=re.IGNORECASE
            )[0]

            return normalize_field(field)

    # Dictionary-based fallback
    text_lower = text.lower()

    for key, normalized in FIELD_NORMALIZATION.items():

        if key.lower() in text_lower:
            return normalized

    return ""


def extract_institution(text: str) -> str:
    """
    Extract institution name from education text.
    """

    if not text:
        return ""

    text = normalize_text(text)

    patterns = [

        # Example:
        # at Jain University
        r"(?:at|from)\s+([A-Z][A-Za-z0-9&.,' -]{2,80})",

        # Example:
        # Jain University
        r"([A-Z][A-Za-z0-9&.,' -]+)\s+"
        r"(?:University|College|Institute)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            institution = match.group(1).strip()

            institution = re.sub(
                r"\s+",
                " ",
                institution
            )

            return institution.strip(" ,.")

    return ""


def parse_education_section(text: str) -> List[Dict]:
    """
    Parse education section into structured records.
    """

    if not text:
        return []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    records = []

    for line in lines:

        degree_type = detect_degree_type(line)

        if degree_type == "OTHER":
            continue

        record = {
            "degree_type": degree_type,
            "degree_name": line,
            "field_of_study": extract_field(line),
            "institution": extract_institution(line),
            "graduation_year": extract_year(line),
        }

        records.append(record)

    return records