import json
from pathlib import Path

from scoring_engine import ScreeningScoringEngine


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = (
    PROJECT_ROOT
    / "day26_screening_scoring_engine"
    / "config"
    / "scoring_parameters.json"
)

DATA_PATH = (
    PROJECT_ROOT
    / "day26_screening_scoring_engine"
    / "data"
    / "sample_screening_answers.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "day26_screening_scoring_engine"
    / "output"
    / "screening_scores.json"
)


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():

    print(
        "Starting Day 26 Screening Scoring Engine..."
    )

    config = load_json(CONFIG_PATH)
    answers = load_json(DATA_PATH)

    engine = ScreeningScoringEngine(config)

    candidate_result = engine.score_candidate(
        answers
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            candidate_result,
            file,
            indent=4
        )

    print()
    print(
        f"Candidate ID: "
        f"{candidate_result['candidate_id']}"
    )

    print(
        f"Questions evaluated: "
        f"{candidate_result['questions_evaluated']}"
    )

    print(
        f"Total screening score: "
        f"{candidate_result['total_screening_score']}"
    )

    print()
    print("Per-question scores:")

    for item in candidate_result["question_scores"]:

        print(
            f"{item['question_id']} -> "
            f"{item['normalized_score']}"
        )

        print(
            f"  Clarity: "
            f"{item['parameter_scores']['clarity']}"
        )

        print(
            f"  Relevance: "
            f"{item['parameter_scores']['relevance']}"
        )

        print(
            f"  Completeness: "
            f"{item['parameter_scores']['completeness']}"
        )

        print(
            f"  Consistency: "
            f"{item['parameter_scores']['consistency']}"
        )

    print()
    print("Screening scoring completed.")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()