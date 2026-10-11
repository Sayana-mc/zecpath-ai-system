import json
from pathlib import Path

from .scoring_engine import load_json, build_evaluation_report


BASE_DIR = Path(__file__).resolve().parent.parent


def main():
    records = load_json("data/technical_answers.json")
    rubric = load_json("config/scoring_rubric.json")

    report = build_evaluation_report(records, rubric)

    output_dir = BASE_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "technical_evaluation_report.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("=" * 60)
    print("DAY 47 - TECHNICAL SKILL SCORING MODEL")
    print("=" * 60)
    print(f"Candidate ID : {report['candidate_id']}")
    print(f"Questions    : {report['question_count']}")
    print(f"Overall Score: {report['overall_score']}/100")

    print("\nSkill-wise Scores:")
    for skill, details in report["skill_wise_breakdown"].items():
        print(
            f"  {skill}: {details['average_score']}/100 "
            f"({details['question_count']} question(s))"
        )

    print("\nQuestion Results:")
    for item in report["question_results"]:
        print(
            f"  {item['question_id']} | {item['skill']} | "
            f"Score: {item['technical_score']} | "
            f"Depth: {item['answer_depth']}"
        )

    print(f"\nReport saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()