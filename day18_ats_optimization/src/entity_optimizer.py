from __future__ import annotations

import re


SKILL_PATTERNS = [
    "python",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pandas",
    "numpy",
]


def detect_skills(text: str) -> list[str]:

    text_lower = text.lower()

    detected = []

    for skill in SKILL_PATTERNS:

        if skill in text_lower:
            detected.append(skill)

    return sorted(
        set(detected)
    )


def detect_years_of_experience(text: str):

    pattern = r"(\d+)\+?\s+years?"

    matches = re.findall(
        pattern,
        text.lower(),
    )

    if not matches:
        return 0

    return max(
        int(value)
        for value in matches
    )


def detect_email(text: str):

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    match = re.search(
        pattern,
        text,
    )

    if match:
        return match.group(0)

    return None


if __name__ == "__main__":

    sample = """
    Python Data Analyst with 3 years of experience.
    Skilled in SQL, Excel, Power BI and Pandas.
    """

    print("=" * 65)
    print("OPTIMIZED ENTITY DETECTION")
    print("=" * 65)

    print("\nSkills:")
    print(detect_skills(sample))

    print("\nExperience:")
    print(
        detect_years_of_experience(sample),
        "years",
    )

    print("\nEntity detection completed.")

    print("=" * 65)