import re

from .section_patterns import SECTION_PATTERNS


def normalize_heading(text):
    """
    Normalize a possible resume heading.
    """

    text = text.strip().lower()

    text = re.sub(r"[:\-–—]+$", "", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def classify_heading(text):
    """
    Classify a heading into a standard resume section.
    """

    normalized = normalize_heading(text)

    if not normalized:
        return None

    for section, patterns in SECTION_PATTERNS.items():

        for pattern in patterns:

            if normalized == pattern:
                return section

    return None


def is_heading_candidate(line):
    """
    Determine whether a line looks like a section heading.
    """

    line = line.strip()

    if not line:
        return False

    normalized = normalize_heading(line)

    if classify_heading(line):
        return True

    if len(line) > 60:
        return False

    if line.endswith("."):
        return False

    words = normalized.split()

    if len(words) > 6:
        return False

    uppercase_ratio = sum(
        1 for char in line if char.isupper()
    )

    letter_count = sum(
        1 for char in line if char.isalpha()
    )

    if letter_count > 0:

        ratio = uppercase_ratio / letter_count

        if ratio >= 0.70:
            return True

    return False


def detect_section_heading(line):
    """
    Return the canonical section name if a heading is detected.
    """

    section = classify_heading(line)

    if section:
        return section

    if is_heading_candidate(line):

        normalized = normalize_heading(line)

        for section, patterns in SECTION_PATTERNS.items():

            for pattern in patterns:

                if pattern in normalized:
                    return section

    return None