import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT
    / "day42_optimization_stability"
    / "src"
)

sys.path.insert(
    0,
    str(SRC_DIR)
)

from transcript_cleaner import TranscriptCleaner
from followup_stabilizer import FollowUpStabilizer
from refined_scoring_engine import RefinedScoringEngine
from optimization_engine import OptimizationEngine


BASE_DIR = (
    PROJECT_ROOT
    / "day42_optimization_stability"
)

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "interview_samples.json"
)

CONFIG_FILE = (
    BASE_DIR
    / "config"
    / "optimization_config.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_config():

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print("=" * 60)
    print("DAY 42 - OPTIMIZATION & STABILITY")
    print("=" * 60)

    config = load_config()

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        samples = json.load(file)

    transcript_cleaner = (
        TranscriptCleaner()
    )

    followup_stabilizer = (
        FollowUpStabilizer(
            max_followups=config[
                "followup"
            ][
                "max_followups_per_question"
            ]
        )
    )

    scoring_engine = (
        RefinedScoringEngine(
            min_score=config[
                "scoring"
            ][
                "min_score"
            ],
            max_score=config[
                "scoring"
            ][
                "max_score"
            ],
            anomaly_difference_threshold=config[
                "scoring"
            ][
                "anomaly_difference_threshold"
            ],
            default_score=config[
                "scoring"
            ][
                "default_score"
            ]
        )
    )

    optimizer = OptimizationEngine(
        transcript_cleaner,
        followup_stabilizer,
        scoring_engine
    )

    results = []

    for sample in samples:

        result = optimizer.optimize_interview(
            sample
        )

        results.append(result)

        print()
        print(
            f"Candidate: "
            f"{result['candidate_id']}"
        )

        print(
            f"Question: "
            f"{result['question_id']}"
        )

        print(
            f"Cleaned Response: "
            f"{result['cleaned_response']}"
        )

        print(
            f"Follow-up: "
            f"{result['followup_question']}"
        )

        print(
            f"Processing Time: "
            f"{result['processing_time_ms']} ms"
        )

    output = {
        "day": 42,
        "title": "Optimization & Stability",
        "total_samples": len(results),
        "results": results
    }

    output_file = (
        OUTPUT_DIR
        / "optimized_interview_results.json"
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
    print("DAY 42 OPTIMIZATION COMPLETED")
    print("=" * 60)

    print(
        f"Output: {output_file}"
    )


if __name__ == "__main__":
    main()