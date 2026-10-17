"""Run the Day 53 Hiring Intelligence Report Generator."""

from pathlib import Path

from day53_hiring_intelligence_report.src.report_generator import (
    build_hiring_report,
    load_json,
    save_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DAY53_DIR = PROJECT_ROOT / "day53_hiring_intelligence_report"

CONFIG_PATH = DAY53_DIR / "config" / "report_config.json"
INPUT_PATH = DAY53_DIR / "data" / "candidate_profile.json"
OUTPUT_DIR = DAY53_DIR / "output"


def main() -> None:
    config = load_json(CONFIG_PATH)
    assessment = load_json(INPUT_PATH)

    report = build_hiring_report(assessment, config)
    json_path, markdown_path = save_report(report, OUTPUT_DIR)

    recommendation = report["final_recommendation"]
    candidate = report["candidate_profile"]
    evaluation = report["evaluation_summary"]

    print("=" * 64)
    print("DAY 53 - HIRING INTELLIGENCE REPORT GENERATOR")
    print("=" * 64)
    print(f"Candidate ID       : {candidate['candidate_id']}")
    print(f"Candidate          : {candidate['name']}")
    print(f"Target Role        : {candidate['target_role']}")
    print(f"Completed Scored Rounds: {evaluation['completed_scored_rounds']}")
    print(f"Overall Round Average : {evaluation['overall_round_average']}")
    print(f"Final Recommendation: {recommendation['decision']}")
    print(f"Unified Score      : {recommendation['score']}")
    print(f"Confidence         : {recommendation['confidence']}")
    print(f"Human Review       : {recommendation['human_review_required']}")
    print("-" * 64)
    print("Reports generated:")
    print(f"JSON     : {json_path}")
    print(f"Markdown : {markdown_path}")
    print("=" * 64)


if __name__ == "__main__":
    main()