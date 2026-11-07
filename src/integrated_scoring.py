"""Integrate Day 12 semantic matching with the configured Day 13 ATS formula."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from day12_semantic_matching.src.similarity_engine import cosine_similarity
from day13_ats_scoring.src.ats.scoring_engine import generate_score_breakdown
from day13_ats_scoring.src.scoring_parameters import (
    education_alignment_score,
    experience_relevance_score,
    skill_match_score,
)

from .resume_analysis import extract_resume_data
from .services import calculate_candidate_match

if TYPE_CHECKING:
    from day12_semantic_matching.src.embedding_engine import EmbeddingEngine


@lru_cache(maxsize=1)
def _embedding_engine() -> EmbeddingEngine:
    from day12_semantic_matching.src.embedding_engine import EmbeddingEngine

    return EmbeddingEngine(local_files_only=True)


def calculate_integrated_score(
    candidate: dict[str, Any],
    opening: dict[str, Any],
) -> tuple[float, dict[str, Any]]:
    resume_text = candidate.get("resume_text", "").strip()
    resume_data = candidate.get("resume_data") or (
        extract_resume_data(resume_text) if resume_text else {}
    )
    profile_skills = candidate.get("skills", [])
    extracted_skills = resume_data.get("skills", [])
    all_skills = list(
        dict.fromkeys(
            [*profile_skills, *extracted_skills]
        )
    )
    skill_result = skill_match_score(
        {"skills": all_skills},
        opening,
    )
    experience_result = experience_relevance_score(
        {"years_of_experience": resume_data.get("experience_years")},
        {"minimum_years_experience": opening.get("minimum_years_experience")},
    )
    education_records = resume_data.get("education", [])
    education_name = (
        education_records[0].get("degree_name")
        if education_records
        else None
    )
    education_result = education_alignment_score(
        {"education": education_name},
        {"minimum_education": opening.get("minimum_education")},
    )

    semantic_similarity = None
    semantic_reason = "A readable resume is required for Day 12 semantic scoring."
    if resume_text:
        job_text_parts = [
            str(opening["title"]),
            str(opening.get("description", "")),
            "Required skills: " + ", ".join(opening.get("required_skills", [])),
            "Preferred skills: " + ", ".join(opening.get("preferred_skills", [])),
        ]
        if opening.get("minimum_education"):
            job_text_parts.append(
                f"Minimum education: {opening['minimum_education']}"
            )
        if opening.get("minimum_years_experience") is not None:
            job_text_parts.append(
                "Minimum years of experience: "
                f"{opening['minimum_years_experience']}"
            )
        try:
            resume_embedding, job_embedding = _embedding_engine().encode_many(
                [
                    resume_text,
                    ". ".join(part for part in job_text_parts if part).strip(),
                ]
            )
            semantic_similarity = max(
                0.0,
                min(1.0, cosine_similarity(resume_embedding, job_embedding)),
            )
            semantic_reason = (
                "Cosine similarity of Day 12 all-MiniLM-L6-v2 embeddings."
            )
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            raise ScoringModelUnavailableError(
                "Day 12 semantic scoring is unavailable. Install the configured "
                "dependencies and cache all-MiniLM-L6-v2 before scoring resumes."
            ) from exc

    components = {
        "skill_match": skill_result,
        "experience_relevance": experience_result,
        "education_alignment": education_result,
        "semantic_similarity": {
            "score": (
                round(semantic_similarity, 4)
                if semantic_similarity is not None
                else None
            ),
            "reason": semantic_reason,
        },
    }
    breakdown = generate_score_breakdown(
        skill_result["score"],
        experience_result["score"],
        education_result["score"],
        semantic_similarity,
        opening["title"],
    )
    _, exact_evidence = calculate_candidate_match(candidate, opening)
    required_skills_by_key: dict[str, str] = {}
    for skill in opening["required_skills"]:
        cleaned = str(skill).strip()
        required_skills_by_key.setdefault(cleaned.casefold(), cleaned)
    required_skills = list(required_skills_by_key.values())
    normalized_skills = {skill.casefold() for skill in all_skills}
    matched_skills = [
        skill for skill in required_skills if skill.casefold() in normalized_skills
    ]
    missing_skills = [
        skill for skill in required_skills if skill not in matched_skills
    ]
    preferred_skills_by_key: dict[str, str] = {}
    for skill in opening["preferred_skills"]:
        cleaned = str(skill).strip()
        preferred_skills_by_key.setdefault(cleaned.casefold(), cleaned)
    preferred_skills = list(preferred_skills_by_key.values())
    matched_preferred = [
        skill for skill in preferred_skills if skill.casefold() in normalized_skills
    ]

    evidence = {
        "method": (
            "day9_12_13_configured_weighted_score"
            if semantic_similarity is not None
            else (
                "day9_11_13_configured_weighted_score"
                if resume_text
                else "day13_profile_skill_weighted_score"
            )
        ),
        "job_id": opening["opening_id"],
        "candidate_id": candidate["candidate_id"],
        "job_title": opening["title"],
        "candidate_name": candidate["name"],
        "extracted_skills": extracted_skills,
        "scoring_skills": all_skills,
        "matching_required_skills": matched_skills,
        "matched_required_skills": matched_skills,
        "missing_required_skills": missing_skills,
        "matching_preferred_skills": matched_preferred,
        "education_details": education_records,
        "experience_details": {
            "years": resume_data.get("experience_years"),
            "roles": resume_data.get("experience", []),
        },
        "components": components,
        "weights": breakdown["weights"],
        "breakdown": breakdown["breakdown"],
        "classification": breakdown["classification"],
        "formula": "sum(component_score_0_to_100 * configured_role_weight)",
        "scoring_explanation": (
            "Day 9-11 extract skills, dated work history, and education; "
            "Day 12 compares the resume with the job title, description, "
            "required/preferred skills, and specified education/experience "
            "requirements using sentence-embedding cosine similarity; Day 13 "
            "applies its configured, role-specific weighted formula. Missing "
            "experience or education inputs are represented as unavailable "
            "by their component helper and contribute zero under Day 13's "
            "existing score normalization."
        ),
        "human_review_required": True,
        **{
            key: value
            for key, value in exact_evidence.items()
            if key not in {
                "method",
                "human_review_required",
                "matched_required_skills",
                "missing_required_skills",
            }
        },
    }
    return breakdown["final_score"], evidence


class ScoringModelUnavailableError(RuntimeError):
    """Raised when locally configured Day 12 inference cannot be run."""
