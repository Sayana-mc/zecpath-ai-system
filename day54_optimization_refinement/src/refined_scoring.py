
from statistics import mean


def validate_score(score):
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError("Score must be numeric.")

    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")

    return float(score)


def calculate_round_score(round_scores):
    """Average only supplied, valid completed-round scores."""
    if not isinstance(round_scores, list):
        raise ValueError("round_scores must be a list.")

    if not round_scores:
        return None

    scores = [validate_score(score) for score in round_scores]
    return round(mean(scores), 2)


def evaluate_candidate(
    score,
    round_scores,
    completed_rounds,
    thresholds,
    consistency_config,
    review_config,
    intent="unknown"
):
    """Return an advisory score band and review reasons."""

    score = validate_score(score)

    if not isinstance(round_scores, list):
        raise ValueError("round_scores must be a list.")

    if (
        isinstance(completed_rounds, bool)
        or not isinstance(completed_rounds, int)
        or completed_rounds < 0
    ):
        raise ValueError("completed_rounds must be a non-negative integer.")

    checked_scores = [
        validate_score(item) for item in round_scores
    ]

    if checked_scores and len(checked_scores) != completed_rounds:
        raise ValueError(
            "completed_rounds must match the number of supplied round scores."
        )

    strong_fit = validate_score(thresholds["strong_fit"])
    potential_fit = validate_score(thresholds["potential_fit"])

    if potential_fit >= strong_fit:
        raise ValueError(
            "potential_fit threshold must be lower than strong_fit."
        )

    if strong_fit > 100:
        raise ValueError("strong_fit threshold cannot exceed 100.")

    if not isinstance(intent, str):
        raise ValueError("intent must be a string.")

    # This category is advisory only; it is never a final hiring decision.
    if score >= strong_fit:
        band = "STRONG_FIT_FOR_REVIEW"
    elif score >= potential_fit:
        band = "POTENTIAL_FIT_FOR_REVIEW"
    else:
        band = "FURTHER_REVIEW_REQUIRED"

    reasons = []

    minimum_rounds = consistency_config["minimum_completed_rounds"]
    maximum_gap = consistency_config["maximum_round_score_gap"]

    if completed_rounds < minimum_rounds:
        reasons.append("INSUFFICIENT_COMPLETED_ROUNDS")

    if checked_scores:
        gap = round(max(checked_scores) - min(checked_scores), 2)
        round_average = round(mean(checked_scores), 2)
    else:
        gap = None
        round_average = None

    if gap is not None and gap > maximum_gap:
        reasons.append("LARGE_ROUND_SCORE_GAP")

    if (
        review_config.get("review_on_unknown_intent", True)
        and intent == "unknown"
    ):
        reasons.append("UNKNOWN_INTENT")

    if reasons:
        status = "HOLD_FOR_HUMAN_REVIEW"
    else:
        status = "ADVISORY_RESULT_REQUIRES_HUMAN_DECISION"

    return {
        "score": score,
        "advisory_band": band,
        "status": status,
        "round_average": round_average,
        "round_score_gap": gap,
        "review_reasons": reasons,
        "human_review_required": True,
        "automatic_rejection_enabled": False
    }
