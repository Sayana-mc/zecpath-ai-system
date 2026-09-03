from __future__ import annotations


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


def to_list(value) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [normalize_text(item) for item in value if str(item).strip()]

    return [normalize_text(value)]


def skill_match_score(resume: dict, job: dict) -> dict:
    resume_skills = set(to_list(resume.get("skills")))
    required_skills = set(to_list(job.get("required_skills")))

    if not required_skills:
        return {
            "score": None,
            "reason": "Job required_skills is missing or empty.",
            "matched_skills": [],
            "missing_skills": []
        }

    if not resume_skills:
        return {
            "score": None,
            "reason": "Resume skills is missing or empty.",
            "matched_skills": [],
            "missing_skills": sorted(required_skills)
        }

    matched = sorted(resume_skills.intersection(required_skills))
    missing = sorted(required_skills.difference(resume_skills))
    score = len(matched) / len(required_skills)

    return {
        "score": round(score, 4),
        "reason": "Score is matched required skills divided by total required skills.",
        "matched_skills": matched,
        "missing_skills": missing
    }


def experience_relevance_score(resume: dict, job: dict) -> dict:
    candidate_years = resume.get("years_of_experience")
    required_years = job.get("minimum_years_experience")

    if candidate_years is None:
        return {
            "score": None,
            "reason": "Resume years_of_experience is missing."
        }

    if required_years is None:
        return {
            "score": None,
            "reason": "Job minimum_years_experience is missing."
        }

    try:
        candidate_years = float(candidate_years)
        required_years = float(required_years)
    except (TypeError, ValueError):
        return {
            "score": None,
            "reason": "Experience values must be numeric."
        }

    if required_years <= 0:
        return {
            "score": 1.0,
            "reason": "No positive minimum experience requirement was specified."
        }

    score = min(candidate_years / required_years, 1.0)

    return {
        "score": round(score, 4),
        "reason": "Score is candidate experience divided by required experience, capped at 1.0.",
        "candidate_years": candidate_years,
        "required_years": required_years
    }


DEGREE_RANKS = {
    "high school": 1,
    "diploma": 2,
    "associate": 3,
    "bachelor": 4,
    "master": 5,
    "phd": 6,
    "doctorate": 6
}


def degree_rank(value: str) -> int | None:
    normalized = normalize_text(value)

    for degree, rank in DEGREE_RANKS.items():
        if degree in normalized:
            return rank

    return None


def education_alignment_score(resume: dict, job: dict) -> dict:
    candidate_education = resume.get("education")
    required_education = job.get("minimum_education")

    if not candidate_education:
        return {
            "score": None,
            "reason": "Resume education is missing."
        }

    if not required_education:
        return {
            "score": None,
            "reason": "Job minimum_education is missing."
        }

    candidate_rank = degree_rank(candidate_education)
    required_rank = degree_rank(required_education)

    if candidate_rank is None or required_rank is None:
        return {
            "score": None,
            "reason": "Education value could not be mapped to a recognised degree level."
        }

    score = min(candidate_rank / required_rank, 1.0)

    return {
        "score": round(score, 4),
        "reason": "Score compares candidate education level with required education level.",
        "candidate_education": candidate_education,
        "required_education": required_education
    }


def semantic_similarity_score(semantic_result: dict | None) -> dict:
    if not semantic_result:
        return {
            "score": None,
            "reason": "No Day 12 semantic matching result was supplied."
        }

    possible_keys = [
        "semantic_similarity",
        "similarity_score",
        "score"
    ]

    value = None
    used_key = None

    for key in possible_keys:
        if key in semantic_result:
            value = semantic_result[key]
            used_key = key
            break

    if value is None:
        return {
            "score": None,
            "reason": "No supported semantic score field was found in the Day 12 result."
        }

    try:
        value = float(value)
    except (TypeError, ValueError):
        return {
            "score": None,
            "reason": "Day 12 semantic score is not numeric."
        }

    if value > 1:
        value = value / 100

    value = max(0.0, min(value, 1.0))

    return {
        "score": round(value, 4),
        "reason": f"Semantic similarity read from Day 12 field '{used_key}'."
    }