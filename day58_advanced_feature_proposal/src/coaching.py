"""Explainable, rule-based candidate coaching prototype; not a hiring scorer."""

ALLOWED_SKILLS = {"python", "sql", "excel", "data visualization", "statistics", "machine learning", "communication"}

SUGGESTIONS = {
    "python": "Practice data cleaning with pandas and explain each transformation.",
    "sql": "Practice SELECT, JOIN, GROUP BY, filtering, and window-function questions.",
    "excel": "Practice pivot tables, lookup functions, and data-quality checks.",
    "data visualization": "Build a small dashboard and explain why each chart fits the question.",
    "statistics": "Review descriptive statistics, sampling, confidence intervals, and hypothesis testing.",
    "machine learning": "Practice explaining train/test splits, overfitting, and suitable evaluation metrics.",
    "communication": "Use a structured response: context, action, result, and reflection."
}


def _normalise_skills(values, field_name):
    if not isinstance(values, list):
        raise ValueError(f"{field_name} must be a list of skill names")
    cleaned = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Every item in {field_name} must be a non-empty string")
        skill = value.strip().lower()
        if skill not in ALLOWED_SKILLS:
            raise ValueError(f"Unsupported skill in {field_name}: {value}")
        if skill not in cleaned:
            cleaned.append(skill)
    return cleaned


def build_coaching_plan(candidate):
    """Build skill-gap suggestions from explicit input; never rank or reject."""
    if not isinstance(candidate, dict):
        raise ValueError("Candidate must be a JSON object")
    candidate_id = candidate.get("candidate_id")
    role = candidate.get("target_role")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string")
    if not isinstance(role, str) or not role.strip():
        raise ValueError("target_role must be a non-empty string")
    demonstrated = _normalise_skills(candidate.get("skills_demonstrated", []), "skills_demonstrated")
    required = _normalise_skills(candidate.get("required_skills", []), "required_skills")
    missing = [skill for skill in required if skill not in demonstrated]
    return {
        "schema_version": "1.0",
        "candidate_id": candidate_id.strip(),
        "target_role": role.strip(),
        "purpose": "candidate_coaching_only",
        "demonstrated_skills": demonstrated,
        "skills_to_practice": [
            {"skill": skill, "suggestion": SUGGESTIONS[skill]} for skill in missing
        ],
        "summary": f"{len(missing)} target skill(s) identified for optional practice.",
        "hiring_decision": None,
        "human_review_required_for_hiring": True,
        "note": "This plan is advisory and must not be used to rank or reject a candidate. Verify the input profile with the candidate."
    }
