"""Day 52 - Explainable Final Recommendation AI Engine.

Generates holistic, explainable hiring recommendations based on:
1. Cross-round unified score (Day 41 & 51).
2. Evidence completeness confidence (coverage 50%, evidence quality 30%, data consistency 20%).
3. Risk factors (integrity flags, behavioral review signals).
4. Strict non-punitive safeguards: risk flags route to HOLD_REVIEW for human verification,
   never automatic rejection.
5. Recruiter review & override tracking.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src import database


VALID_DECISIONS = {"SELECTED", "HOLD_REVIEW", "REJECTED"}
VALID_RECRUITER_STATUSES = {"PENDING_REVIEW", "APPROVED", "OVERRIDDEN", "REJECTED"}

DEFAULT_DECISION_RULES: dict[str, Any] = {
    "decision_version": "day52-v1",
    "score_thresholds": {
        "selected_min": 80.0,
        "review_min": 60.0,
    },
    "confidence_thresholds": {
        "selected_min": 75.0,
        "review_min": 50.0,
    },
    "minimum_completed_rounds": 3,
    "require_complete_assessment_for_selection": True,
    "risk_policy": {
        "integrity_flag_requires_review": True,
        "behavior_flag_requires_review": True,
        "missing_rounds_require_review": True,
        "low_confidence_requires_review": True,
        "automatic_rejection_from_risk_flags": False,
    },
    "risk_weights": {
        "integrity": 0.6,
        "behavior": 0.4,
    },
}


class DecisionInputError(ValueError):
    """Raised when candidate assessment data is invalid."""


def _validate_number(
    value: Any,
    field_name: str,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    """Validate a numeric score without accepting booleans."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DecisionInputError(f"{field_name} must be numeric.")

    number = float(value)
    if not minimum <= number <= maximum:
        raise DecisionInputError(
            f"{field_name} must be between {minimum} and {maximum}."
        )
    return number


def _validate_count(value: Any, field_name: str) -> int:
    """Validate a non-negative integer count."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DecisionInputError(
            f"{field_name} must be a non-negative integer."
        )
    return value


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON object from disk."""
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise DecisionInputError(f"{path} must contain a JSON object.")
    return data


def calculate_confidence(assessment: dict[str, Any]) -> float:
    """
    Estimate confidence in the recommendation from evidence quality,
    data consistency, and completed-round coverage.

    Formula: Coverage (50%) + Evidence Quality (30%) + Data Consistency (20%).
    This is an evidence-completeness indicator, NOT a probability of job success.
    """
    completed = _validate_count(
        assessment.get("completed_rounds"), "completed_rounds"
    )
    expected = _validate_count(
        assessment.get("expected_rounds"), "expected_rounds"
    )
    evidence_quality = _validate_number(
        assessment.get("evidence_quality"), "evidence_quality"
    )
    data_consistency = _validate_number(
        assessment.get("data_consistency"), "data_consistency"
    )

    if expected == 0:
        raise DecisionInputError("expected_rounds must be greater than zero.")

    if completed > expected:
        raise DecisionInputError(
            "completed_rounds cannot exceed expected_rounds."
        )

    coverage = (completed / expected) * 100.0

    confidence = (
        coverage * 0.50
        + evidence_quality * 0.30
        + data_consistency * 0.20
    )
    return round(confidence, 2)


def _validate_risk_factor(
    risk_factors: dict[str, Any], name: str
) -> dict[str, Any]:
    """Validate and return one risk-factor record."""
    factor = risk_factors.get(name, {})

    if not isinstance(factor, dict):
        raise DecisionInputError(f"Risk factor '{name}' must be an object.")

    flag = factor.get("flag", False)
    if not isinstance(flag, bool):
        raise DecisionInputError(
            f"Risk factor '{name}.flag' must be true or false."
        )

    evidence = factor.get("evidence", [])
    if not isinstance(evidence, list):
        raise DecisionInputError(
            f"Risk factor '{name}.evidence' must be a list."
        )

    if flag and not evidence:
        raise DecisionInputError(
            f"Flagged risk factor '{name}' must include evidence."
        )

    return {
        "flag": flag,
        "evidence": evidence,
        "source": factor.get("source", "Not specified"),
    }


def recommend_candidate(
    assessment: dict[str, Any],
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a rule-based recommendation with an explainable breakdown."""
    if rules is None:
        rules = DEFAULT_DECISION_RULES

    required_fields = (
        "candidate_id",
        "session_id",
        "target_role",
        "assessment_status",
        "unified_score",
        "completed_rounds",
        "expected_rounds",
        "evidence_quality",
        "data_consistency",
    )
    missing_fields = [
        field for field in required_fields if field not in assessment
    ]
    if missing_fields:
        raise DecisionInputError(
            f"Missing assessment fields: {', '.join(missing_fields)}"
        )

    score = _validate_number(assessment["unified_score"], "unified_score")
    completed = _validate_count(
        assessment["completed_rounds"], "completed_rounds"
    )
    expected = _validate_count(
        assessment["expected_rounds"], "expected_rounds"
    )

    if expected == 0 or completed > expected:
        raise DecisionInputError("Invalid completed/expected round counts.")

    thresholds = rules.get("score_thresholds", {})
    confidence_rules = rules.get("confidence_thresholds", {})
    risk_policy = rules.get("risk_policy", {})

    selected_min = _validate_number(
        thresholds.get("selected_min", 80.0), "selected_min"
    )
    review_min = _validate_number(
        thresholds.get("review_min", 60.0), "review_min"
    )
    confidence_selected_min = _validate_number(
        confidence_rules.get("selected_min", 75.0),
        "confidence selected_min",
    )
    confidence_review_min = _validate_number(
        confidence_rules.get("review_min", 50.0),
        "confidence review_min",
    )
    minimum_rounds = _validate_count(
        rules.get("minimum_completed_rounds", 3),
        "minimum_completed_rounds",
    )

    if not review_min < selected_min:
        raise DecisionInputError(
            "review_min must be lower than selected_min."
        )

    if not confidence_review_min < confidence_selected_min:
        raise DecisionInputError(
            "confidence review_min must be lower than selected_min."
        )

    if expected < minimum_rounds:
        raise DecisionInputError(
            "expected_rounds is below the configured minimum."
        )

    confidence = calculate_confidence(assessment)
    risk_data = assessment.get("risk_factors", {})

    if not isinstance(risk_data, dict):
        raise DecisionInputError("risk_factors must be a JSON object.")

    integrity = _validate_risk_factor(risk_data, "integrity")
    behavior = _validate_risk_factor(risk_data, "behavior")

    reasons: list[str] = []
    review_reasons: list[str] = []

    if integrity["flag"] and risk_policy.get(
        "integrity_flag_requires_review", True
    ):
        review_reasons.append(
            "Integrity flag requires human verification."
        )

    if behavior["flag"] and risk_policy.get(
        "behavior_flag_requires_review", True
    ):
        review_reasons.append(
            "Job-related behavior flag requires human review."
        )

    if completed < minimum_rounds:
        review_reasons.append(
            f"Only {completed} evaluation rounds are complete; "
            f"at least {minimum_rounds} are required."
        )

    if completed < expected and risk_policy.get(
        "missing_rounds_require_review", True
    ):
        review_reasons.append("One or more evaluation rounds are missing.")

    if assessment["assessment_status"] != "COMPLETE":
        review_reasons.append(
            "Assessment status is not COMPLETE."
        )

    if confidence < confidence_selected_min:
        review_reasons.append(
            f"Confidence {confidence:.2f} is below the "
            f"selection threshold {confidence_selected_min:.2f}."
        )

    if review_reasons:
        decision = "HOLD_REVIEW"
        reasons.extend(review_reasons)
        reasons.append(
            "Human review is required before an employment decision."
        )
    elif score >= selected_min:
        decision = "SELECTED"
        reasons.append(
            f"Score {score:.2f} meets the selection threshold "
            f"of {selected_min:.2f}."
        )
        reasons.append(
            "Required assessment rounds are complete and no configured "
            "review flag is unresolved."
        )
    elif score >= review_min:
        decision = "HOLD_REVIEW"
        reasons.append(
            f"Score {score:.2f} falls in the review range "
            f"({review_min:.2f} to below {selected_min:.2f})."
        )
        reasons.append(
            "A human reviewer should assess the candidate's evidence."
        )
    else:
        decision = "REJECTED"
        reasons.append(
            f"Score {score:.2f} is below the configured review threshold "
            f"of {review_min:.2f}."
        )
        reasons.append(
            "This recommendation is based on the configured score rule "
            "and must be reviewed by an authorized human."
        )

    round_scores = assessment.get("rounds", {})
    if not isinstance(round_scores, dict):
        raise DecisionInputError("rounds must be a JSON object.")

    validated_round_scores = {}
    for round_name, round_score in round_scores.items():
        validated_round_scores[round_name] = _validate_number(
            round_score, f"rounds.{round_name}"
        )

    flagged_risks = []
    if integrity["flag"]:
        flagged_risks.append(
            {"type": "integrity", "details": integrity}
        )
    if behavior["flag"]:
        flagged_risks.append(
            {"type": "behavior", "details": behavior}
        )

    return {
        "candidate_id": assessment["candidate_id"],
        "session_id": assessment["session_id"],
        "target_role": assessment["target_role"],
        "decision_version": rules.get("decision_version", "day52-v1"),
        "assessment_status": assessment["assessment_status"],
        "decision": decision,
        "score": score,
        "confidence": confidence,
        "confidence_interpretation": (
            "Evidence completeness indicator; not a probability of job success."
        ),
        "round_coverage": {
            "completed": completed,
            "expected": expected,
            "coverage_percent": round((completed / expected) * 100.0, 2),
        },
        "round_scores": validated_round_scores,
        "risk_factors": {
            "integrity": integrity,
            "behavior": behavior,
            "flagged_risks": flagged_risks,
            "automatic_rejection_from_risk_flags": False,
        },
        "explanation": {
            "reasons": reasons,
            "review_reasons": review_reasons,
            "score_thresholds": {
                "selected_min": selected_min,
                "review_min": review_min,
            },
            "confidence_thresholds": {
                "selected_min": confidence_selected_min,
                "review_min": confidence_review_min,
            },
            "human_review_required": True,
        },
        "audit": {
            "recommendation_only": True,
            "automatic_employment_action": False,
        },
    }


def generate_final_recommendation(
    candidate_id: str,
    opening_id: str,
    target_role: str,
    decision: str = "SELECTED",
    score: float = 85.0,
    confidence: float = 0.9,
    reasons: list[str] | None = None,
    save_to_db: bool = True,
) -> dict[str, Any]:
    reasons = reasons or [f"Multi-round evaluation meets requirements for {target_role}."]
    rec = {
        "candidate_id": candidate_id,
        "opening_id": opening_id,
        "target_role": target_role,
        "recommendation": decision,
        "decision": decision,
        "confidence": confidence,
        "confidence_score": confidence,
        "score": score,
        "reasons": reasons,
        "rationale": reasons,
    }
    if save_to_db:
        database.save_final_recommendation(
            candidate_id=candidate_id,
            opening_id=opening_id,
            target_role=target_role,
            decision=decision,
            score=score,
            confidence=confidence,
            reasons=reasons,
        )
    return rec

