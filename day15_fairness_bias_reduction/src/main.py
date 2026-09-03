import json
from pathlib import Path

from .fairness_engine import (
    load_config,
    load_ranking_files,
    process_candidates,
    calculate_bias_indicators,
)


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "input" / "rankings"
OUTPUT_DIR = BASE_DIR / "output" / "fairness"
CONFIG_FILE = BASE_DIR / "config" / "fairness_config.json"


def save_json(path, data):
    """Save JSON with readable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def create_job_output(job_id, candidates):
    """Create fairness-adjusted output for one job."""

    if not candidates:
        return {}

    job_title = candidates[0].get(
        "job_title",
        "Unknown Job"
    )

    ranked = sorted(
        candidates,
        key=lambda candidate: float(
            candidate.get("fairness_score", 0)
        ),
        reverse=True,
    )

    for rank, candidate in enumerate(
        ranked,
        start=1,
    ):
        candidate["fairness_rank"] = rank

    return {
        "job_id": job_id,
        "job_title": job_title,
        "total_candidates": len(ranked),
        "fairness_checked": True,
        "ranked_candidates": ranked,
    }


def main():

    print("=" * 60)
    print("ZecPath - Day 15 Fairness & Bias Reduction")
    print("=" * 60)

    config = load_config(str(CONFIG_FILE))

    candidates = load_ranking_files(str(INPUT_DIR))

    print(f"Input candidate-job records : {len(candidates)}")

    if not candidates:
        print("[ERROR] No ranking files found.")
        return

    processed = process_candidates(
        candidates,
        config,
    )

    jobs = {}

    for candidate in processed:

        job_id = candidate.get(
            "job_id",
            "UNKNOWN",
        )

        jobs.setdefault(
            job_id,
            [],
        ).append(candidate)

    print(f"Jobs processed              : {len(jobs)}")

    all_bias_indicators = {}

    for job_id, job_candidates in sorted(jobs.items()):

        output = create_job_output(
            job_id,
            job_candidates,
        )

        output_path = (
            OUTPUT_DIR
            / f"{job_id}_fairness_adjusted.json"
        )

        save_json(
            output_path,
            output,
        )

        indicators = calculate_bias_indicators(
            job_candidates,
            float(
                config.get(
                    "bias_gap_warning",
                    0.20,
                )
            ),
        )

        all_bias_indicators[job_id] = indicators

        print(
            f"[SUCCESS] {job_id} - "
            f"{output['job_title']} "
            f"({len(job_candidates)} candidates)"
        )

    total_scores = len(processed)

    average_score = (
        sum(
            float(
                candidate.get(
                    "fairness_score",
                    0,
                )
            )
            for candidate in processed
        )
        / total_scores
        if total_scores
        else 0
    )

    summary = {
        "total_candidate_job_records": total_scores,
        "jobs_processed": len(jobs),
        "average_fairness_score": round(
            average_score,
            2,
        ),
        "configuration": config,
        "bias_indicators": all_bias_indicators,
        "fairness_method": [
            "Resume/candidate field normalization",
            "Keyword dependence reduction",
            "Score normalization",
            "Non-essential personal attribute masking",
            "Bias indicator calculation",
        ],
    }

    save_json(
        OUTPUT_DIR / "fairness_summary.json",
        summary,
    )

    bias_report = {
        "report_title": "ZecPath Day 15 Bias Evaluation Report",
        "candidate_job_records": total_scores,
        "jobs_evaluated": len(jobs),
        "bias_indicators": all_bias_indicators,
        "protected_attributes_used_for_scoring": False,
        "personal_attributes_masked": config.get(
            "personal_attributes",
            [],
        ),
        "keyword_dependence_limit": config.get(
            "keyword_weight_limit",
            0.35,
        ),
        "bias_warning_threshold": config.get(
            "bias_gap_warning",
            0.20,
        ),
    }

    save_json(
        OUTPUT_DIR / "bias_report.json",
        bias_report,
    )

    output_files = list(
        OUTPUT_DIR.glob("*.json")
    )

    print()
    print("Candidate records processed :", total_scores)
    print("Jobs processed              :", len(jobs))
    print("Output files                :", len(output_files))
    print("Fairness processing completed successfully.")


if __name__ == "__main__":
    main()