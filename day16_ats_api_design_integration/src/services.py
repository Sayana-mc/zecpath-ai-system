import logging
from typing import Dict, Any, List


logger = logging.getLogger(__name__)


def parse_resume(resume_text: str) -> Dict[str, Any]:
    logger.info("Parsing resume")

    return {
        "status": "PARSED",
        "text": resume_text.strip(),
    }


def calculate_score(
    skills: List[str],
    experience_years: float,
) -> float:

    skill_score = min(len(skills) * 10, 70)
    experience_score = min(experience_years * 6, 30)

    score = skill_score + experience_score

    return round(min(score, 100.0), 2)


def shortlist_candidates(
    candidate_ids: List[str],
) -> List[str]:

    return candidate_ids