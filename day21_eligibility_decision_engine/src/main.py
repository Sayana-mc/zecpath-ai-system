import json
from pathlib import Path

from eligibility_engine import EligibilityDecisionEngine


BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_FILE = BASE_DIR / "config" / "eligibility_rules.json"
INPUT_FILE = BASE_DIR / "input" / "ats_results.json"
OUTPUT_FILE = BASE_DIR / "output" / "eligibility_results.json"


def load_json(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print("Starting Eligibility Decision Engine...")

    # Load recruiter rules
    rules = load_json(CONFIG_FILE)

    # Load ATS results
    candidates = load_json(INPUT_FILE)

    # Create engine
    engine = EligibilityDecisionEngine(rules)

    results = []

    # Evaluate every candidate
    for candidate in candidates:

        decision = engine.evaluate_candidate(
            candidate,
            candidate["job_title"]
        )

        result = {
            "candidate_id": candidate["candidate_id"],
            "job_id": candidate["job_id"],
            "job_title": candidate["job_title"],
            "ats_score": candidate["ats_score"],
            "eligibility_status": decision["status"],
            "reason": decision["reason"]
        }

        if "failed_rule" in decision:

            result["failed_rule"] = decision[
                "failed_rule"
            ]

        if "missing_skills" in decision:

            result["missing_skills"] = decision[
                "missing_skills"
            ]

        results.append(result)

    # Create output directory
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save results
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print()
    print("Eligibility decision completed.")
    print(
        f"Candidates processed: {len(results)}"
    )
    print(
        f"Output file: {OUTPUT_FILE}"
    )

    print()
    print("Eligibility Results:")
    print("--------------------")

    for result in results:

        print(
            f"{result['candidate_id']} -> "
            f"{result['eligibility_status']}"
        )


if __name__ == "__main__":
    main()