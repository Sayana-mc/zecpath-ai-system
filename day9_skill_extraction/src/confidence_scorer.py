"""
Day 9 - Skill Confidence Scoring

This module assigns a confidence score to extracted skills
based on the type of match found during skill extraction.
"""


CONFIDENCE_SCORES = {
    "exact": 0.90,
    "synonym": 0.85,
    "stack": 0.85,
    "fuzzy": 0.80,
    "context": 0.75,
}


def calculate_confidence(match_type):
    """
    Calculate confidence score based on match type.

    Parameters
    ----------
    match_type : str
        Type of skill match.

    Returns
    -------
    float
        Confidence score between 0 and 1.
    """

    if not match_type:
        return 0.0

    match_type = str(match_type).strip().lower()

    return CONFIDENCE_SCORES.get(
        match_type,
        0.70
    )


def score_skill(skill, match_type):
    """
    Create a structured confidence result for a skill.
    """

    return {
        "skill": skill,
        "match_type": match_type,
        "confidence": calculate_confidence(match_type)
    }


if __name__ == "__main__":

    examples = [
        ("Python", "exact"),
        ("JavaScript", "synonym"),
        ("MERN", "stack"),
        ("Python", "fuzzy"),
    ]

    print("Day 9 - Confidence Scoring Demo")
    print("=" * 40)

    for skill, match_type in examples:

        result = score_skill(
            skill,
            match_type
        )

        print(result)