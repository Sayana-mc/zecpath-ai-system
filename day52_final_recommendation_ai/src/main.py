
"""Run the Day 52 Final Recommendation AI."""

import json
from pathlib import Path

from day52_final_recommendation_ai.src.decision_engine import (
    load_json,
    recommend_candidate,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DAY52_DIR = PROJECT_ROOT / "day52_final_recommendation_ai"

ASSESSMENT_PATH = DAY52_DIR / "data" / "candidate_assessment.json"
RULES_PATH = DAY52_DIR / "config" / "decision_rules.json"
OUTPUT_PATH = DAY52_DIR / "output" / "final_candidate_decision.json"


def main() -> None:
    assessment = load_json(ASSESSMENT_PATH)
    rules = load_json(RULES_PATH)

    result = recommend_candidate(assessment, rules)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print("=" * 60)
    print("DAY 52 - FINAL RECOMMENDATION AI")
    print("=" * 60)
    print(f"Candidate ID : {result['candidate_id']}")
    print(f"Target Role  : {result['target_role']}")
    print(f"Score        : {result['score']:.2f}/100")
    print(f"Confidence   : {result['confidence']:.2f}/100")
    print(f"Decision     : {result['decision']}")
    print("-" * 60)
    print("Explanation:")
    for reason in result["explanation"]["reasons"]:
        print(f"- {reason}")

    print("-" * 60)
    print(f"JSON report saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
