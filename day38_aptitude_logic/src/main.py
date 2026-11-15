import json
from pathlib import Path

from aptitude_engine import AptitudeEngine
from logical_scoring import LogicalReasoningScorer
from scenario_evaluator import ScenarioEvaluator


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def main():

    print("=" * 60)
    print("DAY 38 - APTITUDE LOGIC DESIGN")
    print("=" * 60)

    aptitude_engine = AptitudeEngine()
    reasoning_scorer = LogicalReasoningScorer()
    scenario_evaluator = ScenarioEvaluator()

    answers = [
        {
            "question_id": "APT001",
            "answer": (
                "There are 10 tasks. "
                "6 are completed, so 4 tasks remain."
            )
        },
        {
            "question_id": "APT002",
            "answer": (
                "First calculate the total tasks and divide by "
                "the number of days. Therefore the average is 4."
            )
        },
        {
            "question_id": "APT003",
            "answer": (
                "I would identify the error, communicate it to the "
                "manager, analyze the impact, and fix or escalate it."
            )
        }
    ]

    results = []

    for item in answers:

        question = aptitude_engine.get_question(
            item["question_id"]
        )

        answer = item["answer"]

        print()
        print(f"Question ID: {item['question_id']}")
        print(f"Category: {question['category']}")
        print(f"Answer: {answer}")

        if question["category"] == "logical_reasoning":

            score = reasoning_scorer.calculate_score(answer)

            result = {
                "question_id": item["question_id"],
                "category": question["category"],
                "answer": answer,
                "logical_reasoning_score": score
            }

            print(
                f"Logical Score: "
                f"{score['normalized_score']}"
            )

        else:

            score = scenario_evaluator.evaluate(answer)

            result = {
                "question_id": item["question_id"],
                "category": question["category"],
                "answer": answer,
                "scenario_score": score
            }

            print(
                f"Scenario Score: "
                f"{score['overall_score']}"
            )

        results.append(result)

    output = {
        "module": "Day 38 Aptitude Logic Design",
        "total_questions": len(results),
        "results": results
    }

    output_file = OUTPUT_DIR / "aptitude_evaluation.json"

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
    print("APTITUDE EVALUATION COMPLETED")
    print(f"Total questions: {len(results)}")
    print(f"Output: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()