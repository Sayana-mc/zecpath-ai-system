import json
from pathlib import Path

from communication_scorer import CommunicationScorer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "day35_communication_skill_evaluation"
    / "output"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():

    print("=" * 60)
    print("DAY 35 - COMMUNICATION SKILL EVALUATION")
    print("=" * 60)

    scorer = CommunicationScorer()

    candidates = [
        {
            "candidate_id": "C001",
            "answer": (
                "I worked on several data analysis projects. "
                "I used Python and SQL to clean data and generate "
                "useful insights for the team."
            )
        },
        {
            "candidate_id": "C002",
            "answer": (
                "Um, I basically worked on Python projects and "
                "like, I learned SQL."
            )
        },
        {
            "candidate_id": "C003",
            "answer": "I know Python."
        }
    ]

    results = []

    for candidate in candidates:

        result = scorer.evaluate(
            candidate["answer"]
        )

        record = {
            "candidate_id": candidate["candidate_id"],
            "answer": candidate["answer"],
            "communication_evaluation": result
        }

        results.append(record)

        print()
        print("Candidate ID:", candidate["candidate_id"])
        print("Answer:", candidate["answer"])
        print(
            "Communication Score:",
            result["communication_score"]
        )

        print("Parameter Scores:")

        for parameter, score in result["parameter_scores"].items():
            print(f"  {parameter}: {score}")

        print(
            "Filler Words:",
            result["filler_words"]
        )

        print(
            "Word Count:",
            result["word_count"]
        )

        print(
            "Sentence Count:",
            result["sentence_count"]
        )

    output = {
        "total_candidates": len(results),
        "evaluations": results
    }

    output_file = (
        OUTPUT_DIR
        / "communication_scores.json"
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
    print("COMMUNICATION EVALUATION COMPLETED")
    print("Total candidates:", len(results))
    print("Output:", output_file)
    print("=" * 60)


if __name__ == "__main__":
    main()