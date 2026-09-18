import json
from pathlib import Path

from report_builder import ScreeningReportBuilder
from report_formatter import RecruiterReportFormatter


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "input"
    / "screening_input.json"
)

OUTPUT_DIR = BASE_DIR / "output"

JSON_OUTPUT = (
    OUTPUT_DIR
    / "screening_report.json"
)

TEXT_OUTPUT = (
    OUTPUT_DIR
    / "screening_report.txt"
)


def main():

    print(
        "Starting Day 28 AI Screening Report Generator..."
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    builder = ScreeningReportBuilder(data)

    report = builder.build_report()

    formatter = RecruiterReportFormatter(report)

    formatter.save_json(JSON_OUTPUT)
    formatter.save_text(TEXT_OUTPUT)

    print("")
    print("AI Screening Report Generated")
    print("--------------------------------")

    print(
        f"Candidate ID: "
        f"{report['report_metadata']['candidate_id']}"
    )

    print(
        f"Candidate: "
        f"{report['report_metadata']['candidate_name']}"
    )

    print(
        f"Job: "
        f"{report['report_metadata']['job_title']}"
    )

    print(
        f"Screening Score: "
        f"{report['screening_summary']['total_score']}"
    )

    print("")
    print("Key Answers:")
    print(
        len(report["key_answers"])
    )

    print(
        "Strengths:",
        len(report["strengths"])
    )

    print(
        "Risks:",
        len(report["risks"])
    )

    print(
        "Missing Data:",
        len(report["missing_data"])
    )

    print("")
    print(
        "Output JSON:",
        JSON_OUTPUT
    )

    print(
        "Output TXT:",
        TEXT_OUTPUT
    )

    print("")
    print(
        "Day 28 report generation completed."
    )


if __name__ == "__main__":
    main()