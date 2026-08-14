def calculate_ats_score(candidate_skills, required_skills):
    """
    Calculate ATS score based on matching skills.

    Args:
        candidate_skills: Skills available in the candidate profile.
        required_skills: Skills required for the job.

    Returns:
        ATS score as a percentage.
    """

    if not required_skills:
        return 0.0

    candidate_skills = {
        skill.strip().lower()
        for skill in candidate_skills
    }

    required_skills = {
        skill.strip().lower()
        for skill in required_skills
    }

    matched_skills = candidate_skills.intersection(required_skills)

    score = (len(matched_skills) / len(required_skills)) * 100

    return round(score, 2)