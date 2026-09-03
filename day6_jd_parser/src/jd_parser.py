from jd_cleaner import (
    clean_jd_text,
    normalize_title,
    normalize_experience
)

from skill_normalizer import (
    normalize_skills,
    normalize_role
)


def create_ai_jd_profile(jd):
    """
    Convert one raw JD object into an AI-readable
    structured job requirement profile.
    """

    job_title = normalize_role(
        normalize_title(jd.get("job_title", ""))
    )

    required_skills = normalize_skills(
        jd.get("required_skills", [])
    )

    preferred_skills = normalize_skills(
        jd.get("preferred_skills", [])
    )

    education = [
        clean_jd_text(item)
        for item in jd.get("education", [])
    ]

    responsibilities = [
        clean_jd_text(item)
        for item in jd.get("responsibilities", [])
    ]

    soft_skills = normalize_skills(
        jd.get("soft_skills", [])
    )

    profile = {

        "job_id": jd.get("job_id", ""),

        "role": {
            "title": job_title,
            "department": jd.get("department", ""),
            "domain": jd.get("domain", ""),
            "job_type": jd.get("job_type", "")
        },

        "experience": {
            "required_years": normalize_experience(
                jd.get("experience_required_years", "")
            )
        },

        "education": education,

        "skills": {
            "required": required_skills,
            "preferred": preferred_skills,
            "soft_skills": soft_skills
        },

        "responsibilities": responsibilities,

        "location": jd.get("location", ""),

        "employment_type": jd.get(
            "employment_type",
            ""
        ),

        "ai_metadata": {
            "canonical_role": job_title,
            "required_skill_count": len(required_skills),
            "preferred_skill_count": len(preferred_skills),
            "soft_skill_count": len(soft_skills)
        }
    }

    return profile