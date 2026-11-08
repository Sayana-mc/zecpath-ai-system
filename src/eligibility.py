"""Human-reviewed, job-specific eligibility evaluation."""

from __future__ import annotations

from datetime import date
from typing import Any

from day9_skill_extraction.src.skill_normalizer import normalize_skill_name


def _canonical_skill(value: str) -> str:
    canonical = normalize_skill_name(value)
    return (canonical or value).casefold().strip()


def _rule(status: str, reason: str, **details: Any) -> dict[str, Any]:
    return {"status": status, "reason": reason, **details}


def evaluate_eligibility(
    candidate: dict[str, Any],
    opening: dict[str, Any],
    configuration: dict[str, Any],
    configuration_version: int,
    evaluation_id: str,
    evaluated_at: str,
) -> dict[str, Any]:
    """Evaluate explicit job rules; absent or uncertain evidence routes to review."""
    rules: dict[str, Any] = {}
    missing_information: list[str] = []
    review_reasons: list[str] = []
    explicit_failures: list[str] = []
    ats_score = candidate.get("score")
    score_evidence = candidate.get("score_evidence") or {}
    score_is_current = (
        isinstance(ats_score, (int, float))
        and isinstance(score_evidence, dict)
        and bool(score_evidence.get("scored_at"))
    )
    minimum_score = configuration.get("minimum_ats_score")
    if not score_is_current:
        missing_information.append("A current ATS score is unavailable.")
        rules["minimum_ats_score"] = _rule(
            "REVIEW", "A current, timestamped ATS result is required."
        )
    elif minimum_score is not None and ats_score < minimum_score:
        explicit_failures.append("The current ATS score is below the configured minimum.")
        rules["minimum_ats_score"] = _rule(
            "FAIL",
            "The current ATS score is below the configured minimum.",
            value=ats_score,
            required=minimum_score,
        )
    else:
        rules["minimum_ats_score"] = _rule(
            "PASS",
            "The current ATS score meets the configured threshold."
            if minimum_score is not None
            else "A current ATS score is available; no minimum was configured.",
            value=ats_score,
            required=minimum_score,
        )

    profile_skills = candidate.get("skills") or []
    resume_data = candidate.get("resume_data") or {}
    extracted_skills = resume_data.get("skills") or []
    canonical_profile = {
        _canonical_skill(skill): skill
        for skill in profile_skills
        if isinstance(skill, str) and skill.strip()
    }
    canonical_resume = {
        _canonical_skill(skill): skill
        for skill in extracted_skills
        if isinstance(skill, str) and skill.strip()
    }
    all_candidate_skills = set(canonical_profile) | set(canonical_resume)
    required_skills = configuration.get("mandatory_skills", [])
    matched_skills = [
        skill
        for skill in required_skills
        if _canonical_skill(skill) in all_candidate_skills
    ]
    missing_skills = [
        skill
        for skill in required_skills
        if _canonical_skill(skill) not in all_candidate_skills
    ]
    if missing_skills:
        missing_information.append(
            "Mandatory skill evidence is not present for: " + ", ".join(missing_skills)
        )
        review_reasons.append("Mandatory-skill evidence requires recruiter review.")
        rules["mandatory_skills"] = _rule(
            "REVIEW",
            "Missing skill evidence is not treated as proof the candidate lacks a skill.",
            matched=matched_skills,
            missing=missing_skills,
            evidence_sources={
                skill: (
                    "candidate_reported"
                    if _canonical_skill(skill) in canonical_profile
                    else "resume_extraction"
                )
                for skill in matched_skills
            },
        )
    else:
        rules["mandatory_skills"] = _rule(
            "PASS",
            "All configured mandatory skills have profile or resume evidence.",
            matched=matched_skills,
            missing=[],
            evidence_sources={
                skill: (
                    "candidate_reported"
                    if _canonical_skill(skill) in canonical_profile
                    else "resume_extraction"
                )
                for skill in matched_skills
            },
        )

    experience_years = resume_data.get("experience_years")
    minimum_experience = configuration.get("minimum_experience_years")
    maximum_experience = configuration.get("maximum_experience_years")
    experience_result = {
        "status": "NOT_CONFIGURED",
        "years": experience_years,
        "minimum_years": minimum_experience,
        "maximum_years": maximum_experience,
    }
    if minimum_experience is not None or maximum_experience is not None:
        if not isinstance(experience_years, (int, float)):
            missing_information.append("Parsed work experience is unavailable.")
            experience_result.update(
                status="REVIEW",
                reason="Missing or uncertain experience requires human review.",
            )
        elif minimum_experience is not None and experience_years < minimum_experience:
            explicit_failures.append(
                "Parsed experience is below the configured minimum."
            )
            experience_result.update(
                status="FAIL",
                reason="Parsed experience is below the configured minimum.",
            )
        elif maximum_experience is not None and experience_years > maximum_experience:
            review_reasons.append(
                "Parsed experience exceeds the configured range and needs review."
            )
            experience_result.update(
                status="REVIEW",
                reason="Parsed experience exceeds the configured range.",
            )
        else:
            experience_result.update(
                status="PASS",
                reason="Parsed experience is within the configured range.",
            )
    rules["experience"] = experience_result

    location_rules = configuration.get("location_rules") or {}
    candidate_location = candidate.get("location")
    allowed_locations = location_rules.get("allowed_locations") or []
    candidate_mode = candidate.get("work_mode_preference")
    required_mode = location_rules.get("work_mode")
    location_result = {"status": "NOT_CONFIGURED"}
    if allowed_locations or required_mode:
        location_matches = (
            candidate_location is not None
            and candidate_location.casefold()
            in {value.casefold() for value in allowed_locations}
        )
        remote_exception = (
            candidate_mode == "REMOTE" and location_rules.get("remote_allowed", False)
        )
        mode_matches = (
            required_mode is None
            or candidate_mode is None
            or candidate_mode == required_mode
            or remote_exception
        )
        if not candidate_location and allowed_locations and not remote_exception:
            missing_information.append("Candidate location was not supplied.")
            location_result = _rule(
                "REVIEW", "Candidate location is required by configured rules."
            )
        elif not location_matches and allowed_locations and not remote_exception:
            relocation = candidate.get("relocation_willingness")
            if location_rules.get("relocation_required") and relocation is None:
                missing_information.append("Relocation willingness was not supplied.")
                location_result = _rule(
                    "REVIEW", "Relocation willingness is unknown."
                )
            elif location_rules.get("relocation_required") and relocation is True:
                location_result = _rule(
                    "PASS", "Candidate reports willingness to relocate."
                )
            else:
                location_result = _rule(
                    "REVIEW",
                    "Location does not match; recruiter review is required.",
                    candidate_location=candidate_location,
                    allowed_locations=allowed_locations,
                )
                review_reasons.append("Location compatibility requires review.")
        elif not mode_matches:
            location_result = _rule(
                "REVIEW",
                "Candidate work-mode preference does not match the job.",
                candidate_preference=candidate_mode,
                required_mode=required_mode,
            )
            review_reasons.append("Work-mode compatibility requires review.")
        else:
            location_result = _rule(
                "PASS",
                "Candidate location and supplied work-mode preference meet configured rules.",
                candidate_location=candidate_location,
                candidate_preference=candidate_mode,
            )
    rules["location"] = location_result

    latest_start_date = location_rules.get("latest_start_date")
    availability_date = candidate.get("availability_date")
    availability_result = {"status": "NOT_CONFIGURED"}
    if latest_start_date:
        if availability_date is None:
            missing_information.append("Candidate availability date was not supplied.")
            availability_result = _rule(
                "REVIEW", "Availability is unknown; no availability is inferred."
            )
        elif date.fromisoformat(availability_date) > date.fromisoformat(latest_start_date):
            availability_result = _rule(
                "REVIEW",
                "Candidate availability is later than the configured date.",
                availability_date=availability_date,
                latest_start_date=latest_start_date,
            )
            review_reasons.append("Availability compatibility requires review.")
        else:
            availability_result = _rule(
                "PASS",
                "Candidate availability is on or before the configured date.",
                availability_date=availability_date,
                latest_start_date=latest_start_date,
            )
    rules["availability"] = availability_result

    if explicit_failures:
        status = "REJECTED"
        explanation = (
            "One or more explicit, configured job-related thresholds were not met. "
            "This is decision support and must be reviewed by a recruiter."
        )
    elif missing_information or review_reasons:
        status = "REVIEW"
        explanation = (
            "Evidence is missing, uncertain, or requires recruiter judgment; "
            "no employment decision is made automatically."
        )
    else:
        status = "ELIGIBLE"
        explanation = (
            "Configured rules were met using available evidence. "
            "Recruiter review is still required."
        )

    return {
        "evaluation_id": evaluation_id,
        "candidate_id": candidate["candidate_id"],
        "opening_id": opening["opening_id"],
        "status": status,
        "ats_score": ats_score if score_is_current else None,
        "rules": rules,
        "mandatory_skills_matched": matched_skills,
        "mandatory_skills_missing": missing_skills,
        "experience_result": experience_result,
        "location_result": location_result,
        "availability_result": availability_result,
        "missing_information": missing_information,
        "review_reasons": list(dict.fromkeys(review_reasons)),
        "decision_explanation": explanation,
        "configuration_version": configuration_version,
        "evaluated_at": evaluated_at,
        "human_review_required": True,
    }
