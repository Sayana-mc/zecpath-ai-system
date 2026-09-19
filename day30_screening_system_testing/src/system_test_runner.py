import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DAY25_SRC = (
    PROJECT_ROOT
    / "day25_answer_intent_engine"
    / "src"
)

DAY26_SRC = (
    PROJECT_ROOT
    / "day26_screening_scoring_engine"
    / "src"
)

DAY30_SRC = (
    PROJECT_ROOT
    / "day30_screening_system_testing"
    / "src"
)

sys.path.insert(0, str(DAY25_SRC))
sys.path.insert(0, str(DAY26_SRC))
sys.path.insert(0, str(DAY30_SRC))

from test_dataset import TEST_CASES

from intent_classifier import IntentClassifier
from answer_validator import validate_answer
from question_scorer import QuestionScorer


def load_scoring_config():
    """
    Day 26 scoring configuration.
    """

    return {
        "score_range": {
            "minimum": 0,
            "maximum": 5
        },
        "parameters": {
            "clarity": {
                "weight": 0.25
            },
            "relevance": {
                "weight": 0.25
            },
            "completeness": {
                "weight": 0.25
            },
            "consistency": {
                "weight": 0.25
            }
        }
    }


class ScreeningSystemTester:

    def __init__(self):

        self.classifier = IntentClassifier()

        self.scorer = QuestionScorer(
            load_scoring_config()
        )

    def run_test(self, test_case):

        answer = test_case["answer"]

        expected_intent = (
            test_case["expected_intent"]
        )

        intent_result = (
            self.classifier.classify(answer)
        )

        actual_intent = (
            intent_result["intent"]
        )

        validation = validate_answer(
            answer,
            expected_intent
        )

        score_result = (
            self.scorer.calculate_score(
                answer,
                expected_intent
            )
        )

        intent_match = (
            actual_intent
            == expected_intent
        )

        status_match = (
            validation["status"]
            == test_case["human_expected_status"]
        )

        return {
            "test_id": test_case["id"],
            "question_id": test_case["question_id"],
            "answer": answer,
            "expected_intent": expected_intent,
            "actual_intent": actual_intent,
            "intent_match": intent_match,
            "expected_status": (
                test_case[
                    "human_expected_status"
                ]
            ),
            "actual_status": (
                validation["status"]
            ),
            "status_match": status_match,
            "normalized_score": (
                score_result[
                    "normalized_score"
                ]
            ),
            "parameter_scores": (
                score_result[
                    "parameter_scores"
                ]
            )
        }

    def run_all(self):

        results = []

        for test_case in TEST_CASES:

            result = self.run_test(
                test_case
            )

            results.append(result)

        total = len(results)

        correct_intents = sum(
            result["intent_match"]
            for result in results
        )

        correct_statuses = sum(
            result["status_match"]
            for result in results
        )

        intent_accuracy = (
            correct_intents
            / total
            * 100
            if total
            else 0
        )

        status_accuracy = (
            correct_statuses
            / total
            * 100
            if total
            else 0
        )

        return {
            "total_test_cases": total,
            "correct_intents": correct_intents,
            "intent_accuracy": round(
                intent_accuracy,
                2
            ),
            "correct_statuses": correct_statuses,
            "status_accuracy": round(
                status_accuracy,
                2
            ),
            "results": results
        }


def main():

    print(
        "Starting Day 30 Screening System Testing..."
    )

    tester = ScreeningSystemTester()

    report = tester.run_all()

    output_dir = (
        PROJECT_ROOT
        / "day30_screening_system_testing"
        / "output"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir
        / "screening_test_report.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print()
    print(
        "Total test cases:",
        report["total_test_cases"]
    )

    print(
        "Correct intents:",
        report["correct_intents"]
    )

    print(
        "Intent accuracy:",
        report["intent_accuracy"],
        "%"
    )

    print(
        "Correct statuses:",
        report["correct_statuses"]
    )

    print(
        "Status accuracy:",
        report["status_accuracy"],
        "%"
    )

    print()
    print(
        "Screening system testing completed."
    )

    print(
        "Output:",
        output_file
    )


if __name__ == "__main__":
    main()