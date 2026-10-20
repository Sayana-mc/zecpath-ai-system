"""Input and configuration validation for Day 57."""
from pathlib import Path
import json

EXPECTED_SCORE_KEYS = {"ats", "screening", "hr_interview", "technical_interview", "machine_test"}
ALLOWED_HUMAN_LABELS = {"SELECTED", "HOLD_REVIEW", "REJECTED"}

class ValidationError(ValueError):
    """Raised when input data violates the documented schema."""

def load_json(path):
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ValidationError(f"Required file not found: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path.name} at line {exc.lineno}, column {exc.colno}") from exc
    except OSError as exc:
        raise ValidationError(f"Cannot read {path.name}: {exc}") from exc

def validate_config(config):
    if not isinstance(config, dict):
        raise ValidationError("Configuration must be a JSON object.")
    required = {"project_name", "version", "required_skills", "stage_weights", "thresholds", "inconsistency", "governance", "max_resume_characters", "continue_on_candidate_error"}
    missing = required - set(config)
    if missing:
        raise ValidationError(f"Configuration missing keys: {', '.join(sorted(missing))}")
    skills = config["required_skills"]
    if not isinstance(skills, list) or not skills or any(not isinstance(s, str) or not s.strip() for s in skills):
        raise ValidationError("required_skills must be a non-empty list of non-empty strings.")
    if len({s.casefold() for s in skills}) != len(skills):
        raise ValidationError("required_skills must not contain duplicates (case-insensitive).")
    weights = config["stage_weights"]
    if not isinstance(weights, dict) or set(weights) != EXPECTED_SCORE_KEYS:
        raise ValidationError(f"stage_weights keys must be exactly: {', '.join(sorted(EXPECTED_SCORE_KEYS))}.")
    for key, value in weights.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValidationError(f"Weight '{key}' must be a non-negative number.")
    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValidationError("Stage weights must sum to 1.0 (100%).")
    thresholds = config["thresholds"]
    try:
        strong, potential = thresholds["strong_fit"], thresholds["potential_fit"]
    except (TypeError, KeyError) as exc:
        raise ValidationError("thresholds must contain strong_fit and potential_fit.") from exc
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 100 for v in (strong, potential)):
        raise ValidationError("Thresholds must be numeric values from 0 to 100.")
    if potential >= strong:
        raise ValidationError("potential_fit must be lower than strong_fit.")
    governance = config["governance"]
    if not isinstance(governance, dict) or governance.get("human_review_required") is not True:
        raise ValidationError("Human review must remain enabled.")
    if governance.get("automatic_rejection_enabled") is not False:
        raise ValidationError("Automatic rejection must remain disabled.")
    max_chars = config["max_resume_characters"]
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars < 1:
        raise ValidationError("max_resume_characters must be a positive integer.")
    if not isinstance(config["continue_on_candidate_error"], bool):
        raise ValidationError("continue_on_candidate_error must be true or false.")
    gap = config["inconsistency"].get("score_gap_threshold") if isinstance(config["inconsistency"], dict) else None
    if isinstance(gap, bool) or not isinstance(gap, (int, float)) or gap < 0:
        raise ValidationError("score_gap_threshold must be a non-negative number.")
    return config

def validate_candidates(candidates):
    if not isinstance(candidates, list):
        raise ValidationError("Candidate input must be a JSON array.")
    seen = set()
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise ValidationError(f"Candidate at index {index} must be an object.")
        for key in ("candidate_id", "name", "resume_file", "screening_score", "hr_interview_score", "technical_interview_score", "machine_test_score", "human_judgment", "human_score"):
            if key not in candidate:
                raise ValidationError(f"Candidate at index {index} is missing required field '{key}'.")
        cid = candidate["candidate_id"]
        if not isinstance(cid, str) or not cid.strip():
            raise ValidationError(f"Candidate at index {index} has an invalid candidate_id.")
        if cid in seen:
            raise ValidationError(f"Duplicate candidate_id: {cid}")
        seen.add(cid)
        for key in ("name", "resume_file"):
            if not isinstance(candidate[key], str) or not candidate[key].strip():
                raise ValidationError(f"Candidate {cid}: '{key}' must be a non-empty string.")
        # Disallow directory traversal; resumes must be a plain filename.
        if Path(candidate["resume_file"]).name != candidate["resume_file"] or candidate["resume_file"] in {".", ".."}:
            raise ValidationError(f"Candidate {cid}: resume_file must be a filename, not a path.")
        if candidate["human_judgment"] not in ALLOWED_HUMAN_LABELS:
            raise ValidationError(f"Candidate {cid}: unsupported human_judgment label.")
        for key in ("screening_score", "hr_interview_score", "technical_interview_score", "machine_test_score", "human_score"):
            validate_score(candidate[key], f"Candidate {cid} field {key}")
    return candidates

def validate_score(value, label="Score"):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
        raise ValidationError(f"{label} must be a finite number from 0 to 100.")
    # Reject NaN and infinities, for which range comparisons can be misleading.
    if value != value or value in (float("inf"), float("-inf")):
        raise ValidationError(f"{label} must be finite.")
    return float(value)
