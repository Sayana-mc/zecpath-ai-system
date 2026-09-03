import json
from pathlib import Path


def load_thresholds(config_path):
    """Load shortlisting thresholds from JSON configuration."""
    default_thresholds = {
        "shortlisted_min_score": 65,
        "review_min_score": 40,
        "top_candidates_limit": 5,
    }

    config_path = Path(config_path)

    if not config_path.exists():
        return default_thresholds

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            thresholds = json.load(file)
    except (OSError, json.JSONDecodeError):
        return default_thresholds

    try:
        shortlisted_min = float(
            thresholds.get(
                "shortlisted_min_score",
                default_thresholds["shortlisted_min_score"],
            )
        )

        review_min = float(
            thresholds.get(
                "review_min_score",
                default_thresholds["review_min_score"],
            )
        )

        top_limit = int(
            thresholds.get(
                "top_candidates_limit",
                default_thresholds["top_candidates_limit"],
            )
        )
    except (TypeError, ValueError):
        return default_thresholds

    if shortlisted_min < review_min:
        return default_thresholds

    return {
        "shortlisted_min_score": shortlisted_min,
        "review_min_score": review_min,
        "top_candidates_limit": max(1, top_limit),
    }


def get_decision(score, shortlisted_min, review_min):
    """Return the final candidate decision."""
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0

    if score >= shortlisted_min:
        return "SHORTLISTED"

    if score >= review_min:
        return "REVIEW"

    return "REJECTED"


def get_recommendation(decision):
    """Create recruiter-friendly recommendation text."""
    if decision == "SHORTLISTED":
        return (
            "Strong match. Recommended for the next "
            "recruitment stage."
        )

    if decision == "REVIEW":
        return (
            "Potential candidate. Recruiter review is "
            "recommended before final decision."
        )

    return (
        "Current job match score is below the shortlist "
        "threshold."
    )


def extract_score_contributions(candidate):
    """Extract component weighted contributions from Day 13 output."""
    breakdown = candidate.get("breakdown", {})

    if not isinstance(breakdown, dict):
        return {}

    contributions = {}

    for component, details in breakdown.items():
        if not isinstance(details, dict):
            continue

        try:
            contribution = float(
                details.get("weighted_contribution", 0.0)
            )
        except (TypeError, ValueError):
            contribution = 0.0

        contributions[component] = round(contribution, 2)

    return contributions


def enrich_candidate(candidate, thresholds):
    """Add decision, recommendation and recruiter-friendly fields."""
    score = candidate.get("final_ats_score", 0.0)

    decision = get_decision(
        score,
        thresholds["shortlisted_min_score"],
        thresholds["review_min_score"],
    )

    contributions = extract_score_contributions(candidate)

    strongest_area = "Not available"

    if contributions:
        strongest_area = max(
            contributions,
            key=contributions.get,
        )

    enriched = dict(candidate)

    enriched["decision"] = decision
    enriched["recommendation"] = get_recommendation(decision)
    enriched["score_contributions"] = contributions
    enriched["strongest_area"] = strongest_area

    return enriched