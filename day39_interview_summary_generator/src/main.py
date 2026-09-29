import json
from pathlib import Path

from interview_report_generator import InterviewReportGenerator


BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(
    exist_ok=True
)


def main():

    print("=" * 60)
    print("DAY 39 - AI INTERVIEW SUMMARY GENERATOR")
    print("=" * 60)

    responses = {
        "communication_score": 85,
        "confidence_score": 80,
        "relevance_score": 90,
        "consistency_score": 88,

        "teamwork": (
            "I enjoy working with a team and collaborating "
            "with other members."
        ),

        "adaptability": (
            "I am flexible and willing to learn new technologies."
        ),

        "answers": [
            "I have experience with Python and SQL.",
            "I worked on data analysis projects.",
            "I enjoy working with a team.",
            "I am confident about learning new technologies."
        ]
    }

    generator = InterviewReportGenerator()

    report = generator.generate_report(
        "C001",
        responses
    )

    output_file = (
        OUTPUT_DIR /
        "hr_interview_summary.json"
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
    print("Candidate ID:", report["candidate_id"])
    print(
        "Overall HR Score:",
        report["overall_hr_score"]
    )

    print("\nStrengths:")
    for item in report["strengths"]:
        print("-", item)

    print("\nWeaknesses:")
    for item in report["weaknesses"]:
        print("-", item)

    print("\nCultural Fit Indicators:")
    for item in report["cultural_fit_indicators"]:
        print("-", item)

    print("\nRisk Flags:")
    for item in report["risk_flags"]:
        print("-", item)

    print("\nInconsistencies:")
    for item in report["inconsistencies"]:
        print("-", item)

    print("\nRecruiter Summary:")
    print(report["summary"])

    print()
    print("Interview summary generation completed.")
    print("Output:", output_file)


if __name__ == "__main__":
    main()