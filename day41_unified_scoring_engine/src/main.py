import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day41_unified_scoring_engine"
    / "src"
)

sys.path.insert(0, str(SRC_DIR))

from unified_scoring_engine import UnifiedScoringEngine


BASE_DIR = (
    PROJECT_ROOT
    / "day41_unified_scoring_engine"
)

CONFIG_FILE = (
    BASE_DIR
    / "config"
    / "role_weights.json"
)

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "candidate_scores.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def main():

    print("=" * 60)
    print("DAY 41 - UNIFIED SCORING ENGINE")
    print("=" * 60)

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        candidates = json.load(file)

    engine = UnifiedScoringEngine(
        CONFIG_FILE
    )

    results = []

    for candidate in candidates:

        result = engine.evaluate_candidate(
            candidate
        )

        results.append(result)

        print()
        print(
            f"Candidate ID: "
            f"{result['candidate_id']}"
        )

        print(
            f"Role: "
            f"{result['role']}"
        )

        print(
            f"ATS Score: "
            f"{result['round_scores']['ats_score']}"
        )

        print(
            f"Screening Score: "
            f"{result['round_scores']['screening_score']}"
        )

        print(
            f"HR Interview Score: "
            f"{result['round_scores']['hr_interview_score']}"
        )

        print(
            f"Hiring Fit: "
            f"{result['hiring_fit_percentage']}%"
        )

        print(
            f"Recommendation: "
            f"{result['recommendation']}"
        )

    output = {
        "day": 41,
        "title": "Unified Scoring Engine",
        "total_candidates": len(results),
        "results": results
    }

    output_file = (
        OUTPUT_DIR
        / "unified_candidate_scores.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=4
        )

    print()
    print("=" * 60)
    print("UNIFIED SCORING COMPLETED")
    print("=" * 60)

    print(
        f"Output: {output_file}"
    )


if __name__ == "__main__":
    main()