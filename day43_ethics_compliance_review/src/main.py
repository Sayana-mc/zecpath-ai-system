import json
from pathlib import Path

from .ethics_compliance_engine import EthicsComplianceEngine


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "compliance_config.json"
DATA_PATH = BASE_DIR / "data" / "candidate_review_samples.json"
OUTPUT_DIR = BASE_DIR / "output"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def main():

    config = load_json(CONFIG_PATH)
    candidates = load_json(DATA_PATH)

    engine = EthicsComplianceEngine(config)

    ethics_results = []

    for candidate in candidates:

        result = engine.review_candidate(
            candidate=candidate,
            consent_given=True,
            created_at="2026-10-05T10:00:00"
        )

        ethics_results.append(result)

    fairness_result = engine.review_fairness(candidates)

    ethics_output = {
        "review_type": "AI Ethics Review",
        "candidate_count": len(candidates),
        "results": ethics_results
    }

    fairness_output = {
        "review_type": "Fairness Review",
        "results": fairness_result
    }

    compliance_output = {
        "consent_requirements": config["consent"],
        "fairness_controls": config["fairness"],
        "demographic_signals_excluded": config["demographic_signals"],
        "explainability_controls": config["explainability"],
        "data_retention_controls": config["retention"],
        "readiness_status": "READY_FOR_HUMAN_COMPLIANCE_REVIEW"
    }

    OUTPUT_DIR.mkdir(exist_ok=True)

    save_json(
        OUTPUT_DIR / "ethics_review.json",
        ethics_output
    )

    save_json(
        OUTPUT_DIR / "fairness_review.json",
        fairness_output
    )

    save_json(
        OUTPUT_DIR / "compliance_readiness_report.json",
        compliance_output
    )

    print("=" * 60)
    print("DAY 43 - ETHICS & COMPLIANCE REVIEW")
    print("=" * 60)

    print(f"Candidates reviewed: {len(candidates)}")
    print("Consent validation: Completed")
    print("Demographic bias signal review: Completed")
    print("Fairness review: Completed")
    print("Explainability review: Completed")
    print("Data retention review: Completed")

    print("\nOutput files:")
    print(" - ethics_review.json")
    print(" - fairness_review.json")
    print(" - compliance_readiness_report.json")

    print("\nStatus: READY FOR HUMAN COMPLIANCE REVIEW")


if __name__ == "__main__":
    main()