from typing import List, Dict


FIELD_KEYWORDS = {
    "data analyst": [
        "data science",
        "data analytics",
        "statistics",
        "mathematics",
        "computer science",
        "information technology",
    ],
    "data scientist": [
        "data science",
        "statistics",
        "mathematics",
        "computer science",
        "machine learning",
    ],
    "software developer": [
        "computer science",
        "computer applications",
        "information technology",
        "software engineering",
    ],
    "python developer": [
        "computer science",
        "computer applications",
        "information technology",
        "software engineering",
    ],
    "hr": [
        "human resources",
        "business administration",
        "management",
    ],
    "marketing": [
        "marketing",
        "business administration",
        "business management",
    ],
    "graphic designer": [
        "graphic design",
        "communication design",
        "visual design",
        "fine arts",
    ],
}


def calculate_education_relevance(
    education: List[Dict],
    target_role: str,
) -> Dict:

    target = target_role.lower().strip()

    keywords = FIELD_KEYWORDS.get(
        target,
        [],
    )

    if not education:
        return {
            "score": 0.0,
            "matched_fields": [],
            "relevance": "LOW",
        }

    matched_fields = []

    for record in education:
        field = record.get(
            "field_of_study",
            "",
        ).lower()

        for keyword in keywords:
            if keyword.lower() in field:
                matched_fields.append(
                    record.get(
                        "field_of_study",
                        "",
                    )
                )
                break

    matched_fields = list(
        dict.fromkeys(matched_fields)
    )

    if matched_fields:
        score = 1.0
        relevance = "HIGH"
    else:
        score = 0.3
        relevance = "LOW"

    return {
        "score": score,
        "matched_fields": matched_fields,
        "relevance": relevance,
    }