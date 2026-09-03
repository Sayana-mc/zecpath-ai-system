import json
from pathlib import Path


def normalize_score(value):
    """Convert any score safely into the 0-100 range."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(100.0, score))


def load_score_files(input_dir):
    """
    Load all Day 13 ATS score JSON files.
    Returns one candidate-job record for every match.
    """
    input_dir = Path(input_dir)
    candidate_matches = []

    if not input_dir.exists():
        return candidate_matches

    for file_path in sorted(input_dir.glob("*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            continue

        source_file = data.get("source_file", file_path.name)
        matches = data.get("matches", [])

        if not isinstance(matches, list):
            continue

        for match in matches:
            if not isinstance(match, dict):
                continue

            candidate = dict(match)
            candidate["source_file"] = source_file
            candidate["final_ats_score"] = normalize_score(
                candidate.get("final_ats_score", 0.0)
            )

            candidate_matches.append(candidate)

    return candidate_matches


def group_candidates_by_job(candidate_matches):
    """Group all candidate-job records using job ID."""
    jobs = {}

    for candidate in candidate_matches:
        job_id = candidate.get("job_id", "UNKNOWN")

        if job_id not in jobs:
            jobs[job_id] = []

        jobs[job_id].append(candidate)

    return jobs


def rank_candidates(candidates):
    """Sort candidates by ATS score and assign rank numbers."""
    sorted_candidates = sorted(
        candidates,
        key=lambda candidate: normalize_score(
            candidate.get("final_ats_score", 0.0)
        ),
        reverse=True,
    )

    ranked_candidates = []

    for rank, candidate in enumerate(sorted_candidates, start=1):
        ranked_candidate = dict(candidate)
        ranked_candidate["rank"] = rank
        ranked_candidates.append(ranked_candidate)

    return ranked_candidates