def optimize_decision(
    intent,
    status,
    normalized_score
):
    """
    Apply optimized screening decision logic.
    """

    if status == "off_topic":
        return "follow_up"

    if status == "vague":
        return "clarify"

    if intent == "unknown":
        return "clarify"

    if normalized_score >= 70:
        return "accept"

    if normalized_score >= 50:
        return "review"

    return "follow_up"


def reduce_false_rejection(
    intent,
    status,
    normalized_score
):
    """
    Prevent valid but lower-scoring answers
    from being immediately rejected.
    """

    if status == "valid" and intent != "unknown":

        if normalized_score >= 40:
            return "review"

    return optimize_decision(
        intent,
        status,
        normalized_score
    )