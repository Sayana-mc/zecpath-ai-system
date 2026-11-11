"""Day 13: ATS Scoring Engine and Role-Weighted Multi-Factor Assessment."""

from __future__ import annotations

from typing import Any
from .weight_manager import load_role_weights


def normalize_score(value: float | int | str | None) -> float:
    """
    Convert a score into the 0-100 range.
    Input can be:
    - 0 to 1
    - 0 to 100
    """
    try:
        val = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0

    if val <= 1.0 and val > 0.0:
        val = val * 100.0

    return max(0.0, min(100.0, val))


def calculate_component_scores(
    skill_match: float | int,
    experience_relevance: float | int,
    education_alignment: float | int,
    semantic_similarity: float | int,
) -> dict[str, float]:
    """Normalize all ATS scoring components into the 0-100 range."""
    return {
        "skill_match": normalize_score(skill_match),
        "experience_relevance": normalize_score(experience_relevance),
        "education_alignment": normalize_score(education_alignment),
        "semantic_similarity": normalize_score(semantic_similarity),
    }


def calculate_ats_score(
    skill_match: float | int,
    experience_relevance: float | int,
    education_alignment: float | int,
    semantic_similarity: float | int,
    role: str = "data analyst",
) -> float:
    """Calculate the final ATS score using role-specific configurable weights."""
    weights = load_role_weights(role)
    components = calculate_component_scores(
        skill_match,
        experience_relevance,
        education_alignment,
        semantic_similarity,
    )

    final_score = (
        components["skill_match"] * weights["skill_match"]
        + components["experience_relevance"] * weights["experience_relevance"]
        + components["education_alignment"] * weights["education_alignment"]
        + components["semantic_similarity"] * weights["semantic_similarity"]
    )

    return round(max(0.0, min(100.0, final_score)), 2)


def classify_score(score: float | int) -> str:
    """Convert numerical ATS score into an explainable category."""
    norm = normalize_score(score)
    if norm >= 80.0:
        return "EXCELLENT"
    if norm >= 65.0:
        return "GOOD"
    if norm >= 50.0:
        return "MODERATE"
    return "LOW"


def generate_score_breakdown(
    skill_match: float | int,
    experience_relevance: float | int,
    education_alignment: float | int,
    semantic_similarity: float | int,
    role: str = "data analyst",
) -> dict[str, Any]:
    """Generate an explainable ATS score breakdown."""
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
            "weighted_contribution": round(contribution, 2),
        }

    return {
        "role": role,
        "final_score": final_score,
        "classification": classify_score(final_score),
        "weights": weights,
        "breakdown": breakdown,
    }


def calculate_weighted_ats_score(
    candidate_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str] | None = None,
    resume_text: str = "",
    job_description: str = "",
    candidate_experience_years: float = 0.0,
    required_experience_years: float = 0.0,
    candidate_education: str = "",
    minimum_education: str = "",
    role: str = "python developer",
) -> dict[str, Any]:
    """Calculates comprehensive weighted ATS score with matched/missing skill evidence."""
    pref = preferred_skills or []
    req_set = {s.casefold() for s in required_skills}
    cand_set = {s.casefold() for s in candidate_skills}

    matched = [s for s in required_skills if s.casefold() in cand_set]
    missing = [s for s in required_skills if s.casefold() not in cand_set]
    matched_pref = [s for s in pref if s.casefold() in cand_set]

    # Skill match score (0-100)
    skill_score = (len(matched) / len(required_skills) * 100.0) if required_skills else 100.0
    if pref:
        pref_boost = (len(matched_pref) / len(pref)) * 10.0
        skill_score = min(100.0, skill_score + pref_boost)

    # Experience relevance score (0-100)
    if required_experience_years > 0:
        exp_score = min(100.0, (candidate_experience_years / required_experience_years) * 100.0)
    else:
        exp_score = 100.0

    # Education alignment score (0-100)
    edu_score = 85.0 if candidate_education else 60.0

    # Semantic relevance score
    sem_score = 80.0 if any(s.casefold() in resume_text.casefold() for s in matched) else 50.0

    overall = calculate_ats_score(
        skill_match=skill_score,
        experience_relevance=exp_score,
        education_alignment=edu_score,
        semantic_similarity=sem_score,
        role=role,
    )

    breakdown = generate_score_breakdown(
        skill_match=skill_score,
        experience_relevance=exp_score,
        education_alignment=edu_score,
        semantic_similarity=sem_score,
        role=role,
    )

    return {
        "overall_score": overall,
        "classification": classify_score(overall),
        "breakdown": breakdown["breakdown"],
        "evidence": {
            "matched_required_skills": matched,
            "missing_required_skills": missing,
            "matched_preferred_skills": matched_pref,
            "candidate_experience_years": candidate_experience_years,
            "candidate_education": candidate_education,
        },
    }

