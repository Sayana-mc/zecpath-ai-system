import json
from pathlib import Path

from .ranking_engine import (
    group_candidates_by_job,
    load_score_files,
    rank_candidates,
)
from .shortlisting_engine import (
    enrich_candidate,
    load_thresholds,
)


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "input" / "scores"
OUTPUT_DIR = BASE_DIR / "output" / "rankings"
THRESHOLD_FILE = BASE_DIR / "config" / "thresholds.json"


def save_json(file_path, data):
    """Save data as formatted JSON."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def create_job_output(job_id, candidates, thresholds):
    """Create ranking and shortlist output for one job."""
    ranked_candidates = rank_candidates(candidates)

    enriched_candidates = [
        enrich_candidate(candidate, thresholds)
        for candidate in ranked_candidates
    ]

    job_title = "Unknown Job"

    if enriched_candidates:
        job_title = enriched_candidates[0].get(
            "job_title",
            "Unknown Job",
        )

    shortlisted_count = sum(
        1
        for candidate in enriched_candidates
        if candidate["decision"] == "SHORTLISTED"
    )

    review_count = sum(
        1
        for candidate in enriched_candidates
        if candidate["decision"] == "REVIEW"
    )

    rejected_count = sum(
        1
        for candidate in enriched_candidates
        if candidate["decision"] == "REJECTED"
    )

    top_limit = thresholds["top_candidates_limit"]

    return {
        "job_id": job_id,
        "job_title": job_title,
        "total_candidates": len(enriched_candidates),
        "shortlisted_count": shortlisted_count,
        "review_count": review_count,
        "rejected_count": rejected_count,
        "top_candidates": enriched_candidates[:top_limit],
        "ranked_candidates": enriched_candidates,
    }


def main():
    print()
    print("DAY 14 - CANDIDATE RANKING AND SHORTLISTING")
    print("=" * 55)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    thresholds = load_thresholds(THRESHOLD_FILE)

    print(f"Input score folder : {INPUT_DIR}")
    print(f"Output folder      : {OUTPUT_DIR}")
    print(
        "Shortlist threshold: "
        f"{thresholds['shortlisted_min_score']}"
    )
    print(
        "Review threshold   : "
        f"{thresholds['review_min_score']}"
    )
    print("=" * 55)

    candidate_matches = load_score_files(INPUT_DIR)

    if not candidate_matches:
        print("No Day 13 score records were found.")
        return

    jobs = group_candidates_by_job(candidate_matches)

    recruiter_summary = {
        "total_score_records": len(candidate_matches),
        "jobs_processed": len(jobs),
        "thresholds": thresholds,
        "jobs": [],
    }

    total_ranked = 0

    for job_id, candidates in sorted(jobs.items()):
        job_output = create_job_output(
            job_id,
            candidates,
            thresholds,
        )

        output_file = OUTPUT_DIR / f"{job_id}_ranked_candidates.json"

        save_json(output_file, job_output)

        recruiter_summary["jobs"].append(
            {
                "job_id": job_output["job_id"],
                "job_title": job_output["job_title"],
                "total_candidates": job_output["total_candidates"],
                "shortlisted_count": job_output["shortlisted_count"],
                "review_count": job_output["review_count"],
                "rejected_count": job_output["rejected_count"],
                "top_candidates": job_output["top_candidates"],
            }
        )

        total_ranked += job_output["total_candidates"]

        print(
            f"[SUCCESS] {job_id} - "
            f"{job_output['job_title']} "
            f"({job_output['total_candidates']} candidates)"
        )

    summary_file = OUTPUT_DIR / "recruiter_summary.json"

    save_json(summary_file, recruiter_summary)

    print("=" * 55)
    print(f"Score files found : {len(list(INPUT_DIR.glob('*.json')))}")
    print(f"Jobs processed    : {len(jobs)}")
    print(f"Candidates ranked : {total_ranked}")
    print(
        f"Output files      : "
        f"{len(jobs) + 1}"
    )
    print("Candidate ranking completed successfully.")
    print("=" * 55)


if __name__ == "__main__":
    main()