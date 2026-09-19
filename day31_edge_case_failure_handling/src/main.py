import json
from pathlib import Path

from edge_case_handler import EdgeCaseHandler
from retry_manager import RetryManager
from clarification_manager import ClarificationManager


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():

    print("Starting Day 31 Edge Case & Failure Handling...")

    handler = EdgeCaseHandler()
    retry_manager = RetryManager(max_retries=2)
    clarification_manager = ClarificationManager()

    test_cases = [
        {
            "id": "CASE001",
            "transcript": "",
            "confidence": 0.95,
            "language": "en",
            "background_noise": False
        },
        {
            "id": "CASE002",
            "transcript": "I have Python experience.",
            "confidence": 0.35,
            "language": "en",
            "background_noise": False
        },
        {
            "id": "CASE003",
            "transcript": "I have experience",
            "confidence": 0.95,
            "language": "en",
            "background_noise": True
        },
        {
            "id": "CASE004",
            "transcript": "Python aanu ente main skill.",
            "confidence": 0.90,
            "language": "mixed",
            "background_noise": False
        },
        {
            "id": "CASE005",
            "transcript": "Python",
            "confidence": 0.95,
            "language": "en",
            "background_noise": False
        },
        {
            "id": "CASE006",
            "transcript": "I have two years of experience in data analysis.",
            "confidence": 0.95,
            "language": "en",
            "background_noise": False
        }
    ]

    results = []

    for case in test_cases:

        result = handler.analyze_as_dict(
            transcript=case["transcript"],
            confidence=case["confidence"],
            language=case["language"],
            background_noise=case["background_noise"]
        )

        retry_action = retry_manager.get_action(0)

        clarification = None

        if result["action"] == "clarify":
            clarification = clarification_manager.clarify(
                result["case_type"]
            )

        record = {
            "case_id": case["id"],
            "input": case,
            "edge_case_analysis": result,
            "retry_logic": retry_action,
            "clarification": clarification
        }

        results.append(record)

        print()
        print("Case:", case["id"])
        print("Type:", result["case_type"])
        print("Severity:", result["severity"])
        print("Action:", result["action"])
        print("Retry Allowed:", result["retry_allowed"])

    output = {
        "total_cases": len(results),
        "results": results
    }

    output_file = OUTPUT_DIR / "edge_case_test_report.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)

    print()
    print("Edge case testing completed.")
    print("Total cases:", len(results))
    print("Output:", output_file)


if __name__ == "__main__":
    main()