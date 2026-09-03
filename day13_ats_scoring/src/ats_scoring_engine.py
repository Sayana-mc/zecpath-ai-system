from .weight_manager import load_role_weights


def normalize_score(value):
    """
    Convert a score into the 0-100 range.

    Input can be:
    - 0 to 1
    - 0 to 100
    """

    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.0

    if value <= 1:
        value = value * 100

    return max(0.0, min(100.0, value))


def calculate_component_scores(
    skill_match,
    experience_relevance,
    education_alignment,
    semantic_similarity,
):
    """
    Normalize all ATS scoring components
    into the 0-100 range.
    """

    return {
        "skill_match": normalize_score(skill_match),
        "experience_relevance": normalize_score(
            experience_relevance
        ),
        "education_alignment": normalize_score(
            education_alignment
        ),
        "semantic_similarity": normalize_score(
            semantic_similarity
        ),
    }


def calculate_ats_score(
    skill_match,
    experience_relevance,
    education_alignment,
    semantic_similarity,
    role="data analyst",
):
    """
    Calculate the final ATS score using
    role-specific configurable weights.
    """

    weights = load_role_weights(role)

    components = calculate_component_scores(
        skill_match,
        experience_relevance,
        education_alignment,
        semantic_similarity,
    )

    final_score = (
        components["skill_match"]
        * weights["skill_match"]
        + components["experience_relevance"]
        * weights["experience_relevance"]
        + components["education_alignment"]
        * weights["education_alignment"]
        + components["semantic_similarity"]
        * weights["semantic_similarity"]
    )

    return round(
        max(0.0, min(100.0, final_score)),
        2
    )


def classify_score(score):
    """
    Convert numerical ATS score
    into an explainable category.
    """

    score = normalize_score(score)

    if score >= 80:
        return "EXCELLENT"

    if score >= 65:
        return "GOOD"

    if score >= 50:
        return "MODERATE"

    return "LOW"


def generate_score_breakdown(
    skill_match,
    experience_relevance,
    education_alignment,
    semantic_similarity,
    role="data analyst",
):
    """
    Generate an explainable ATS score breakdown.
    """

    weights = load_role_weights(role)

    components = calculate_component_scores(
        skill_match,
        experience_relevance,
        education_alignment,
        semantic_similarity,
    )

    final_score = calculate_ats_score(
        skill_match,
        experience_relevance,
        education_alignment,
        semantic_similarity,
        role,
    )

    breakdown = {}

    for key, value in components.items():

        contribution = value * weights[key]

        breakdown[key] = {
            "score": round(value, 2),
            "weight": weights[key],
            "weighted_contribution": round(
                contribution,
                2
            ),
        }

    return {
        "role": role,
        "final_score": final_score,
        "classification": classify_score(
            final_score
        ),
        "weights": weights,
        "breakdown": breakdown,
    }


def generate_candidate_score(
    candidate_name,
    job_id,
    job_title,
    skill_match,
    experience_relevance,
    education_alignment,
    semantic_similarity,
):
    """
    Generate the final explainable candidate score.
    """

    breakdown = generate_score_breakdown(
        skill_match=skill_match,
        experience_relevance=experience_relevance,
        education_alignment=education_alignment,
        semantic_similarity=semantic_similarity,
        role=job_title,
    )

    return {
        "candidate_name": candidate_name,
        "job_id": job_id,
        "job_title": job_title,
        "final_ats_score": breakdown["final_score"],
        "classification": breakdown["classification"],
        "weights": breakdown["weights"],
        "breakdown": breakdown["breakdown"],
    }