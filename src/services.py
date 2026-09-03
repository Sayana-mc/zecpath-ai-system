from pathlib import Path
from typing import Any, Dict, List

from .errors import InvalidResumeError


def parse_resume(file_path: str) -> str:
    """
    Parse a resume file.

    Day 16 uses a lightweight parser placeholder.
    The existing Day 15/Day 5 extraction engine can be
    connected here later.
    """

    path = Path(file_path)

    if not path.exists():
        raise InvalidResumeError("Resume file does not exist.")

    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    return (
        f"Resume file '{path.name}' received successfully. "
        "Connect the existing resume extraction engine here."
    )


def calculate_score(candidate: Dict[str, Any]) -> float:
    """
    Calculate a simple ATS score.

    This is an API-layer demonstration.
    The production implementation should call the
    existing ZecPath scoring engine.
    """

    score = candidate.get("score", 0)

    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0

    return round(max(0.0, min(100.0, score)), 2)


def shortlist_candidates(
    candidates: List[Dict[str, Any]],
    minimum_score: float = 60.0,
) -> List[Dict[str, Any]]:
    """Filter and rank candidates using their ATS score."""

    processed = []

    for candidate in candidates:
        score = calculate_score(candidate)

        if score >= minimum_score:
            processed.append(
                {
                    "candidate_id": str(
                        candidate.get("candidate_id", "UNKNOWN")
                    ),
                    "score": score,
                }
            )

    processed.sort(
        key=lambda candidate: candidate["score"],
        reverse=True,
    )

    for rank, candidate in enumerate(processed, start=1):
        candidate["rank"] = rank

    return processed