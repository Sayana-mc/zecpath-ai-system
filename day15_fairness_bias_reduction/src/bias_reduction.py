from typing import Any, Dict


DEFAULT_PERSONAL_ATTRIBUTES = {
    "candidate_name",
    "name",
    "email",
    "phone",
    "mobile",
    "address",
    "date_of_birth",
    "dob",
    "gender",
    "age",
    "photo",
    "nationality",
    "religion",
    "marital_status",
}


def mask_personal_attributes(
    candidate: Dict[str, Any],
    attributes=None
) -> Dict[str, Any]:
    """
    Remove or mask non-essential personal attributes.

    These attributes should not contribute to candidate scoring.
    """

    masked = dict(candidate)

    if attributes is None:
        attributes = DEFAULT_PERSONAL_ATTRIBUTES

    for attribute in attributes:
        if attribute in masked:
            masked[attribute] = "[MASKED]"

    return masked


def calculate_keyword_dependence(
    breakdown: Dict[str, Any]
) -> float:
    """
    Estimate keyword dependence using skill-match contribution.

    A high skill-match contribution can indicate stronger dependence
    on explicit keyword matching.
    """

    if not isinstance(breakdown, dict):
        return 0.0

    skill_match = breakdown.get("skill_match", 0)

    try:
        value = float(skill_match)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(1.0, value / 100.0))


def reduce_keyword_dependence(
    candidate: Dict[str, Any],
    keyword_limit: float = 0.35
) -> Dict[str, Any]:
    """
    Reduce excessive dependence on keyword-based matching.

    Semantic similarity and other evidence remain important.
    """

    adjusted = dict(candidate)

    score = float(adjusted.get("final_ats_score", 0.0))

    breakdown = adjusted.get("breakdown", {})

    if not isinstance(breakdown, dict):
        breakdown = {}

    keyword_dependence = calculate_keyword_dependence(breakdown)

    adjusted["keyword_dependence"] = round(keyword_dependence, 4)

    if keyword_dependence > keyword_limit:
        reduction_factor = 0.95
        score = score * reduction_factor

    adjusted["fairness_pre_adjusted_score"] = round(score, 2)

    return adjusted