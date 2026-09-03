import re
from typing import Any, Dict


def normalize_text(value: Any) -> str:
    """Normalize text into a clean standard format."""

    if value is None:
        return ""

    text = str(value)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize bullet symbols
    text = text.replace("•", "-")
    text = text.replace("●", "-")
    text = text.replace("▪", "-")
    text = text.replace("◦", "-")

    return text.strip()


def normalize_score(value: Any) -> float:
    """Normalize a score safely into the range 0-100."""

    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    return round(max(0.0, min(100.0, score)), 2)


def normalize_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Convert candidate data into a standard structure."""

    normalized = dict(candidate)

    normalized["candidate_name"] = normalize_text(
        candidate.get("candidate_name", "Unknown Candidate")
    )

    normalized["job_id"] = normalize_text(
        candidate.get("job_id", "UNKNOWN")
    )

    normalized["job_title"] = normalize_text(
        candidate.get("job_title", "Unknown Job")
    )

    normalized["final_ats_score"] = normalize_score(
        candidate.get("final_ats_score", 0)
    )

    if "classification" in normalized:
        normalized["classification"] = normalize_text(
            normalized["classification"]
        )

    return normalized


def normalize_candidates(candidates):
    """Normalize a list of candidate records."""

    return [
        normalize_candidate(candidate)
        for candidate in candidates
        if isinstance(candidate, dict)
    ]