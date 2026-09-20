import json
from pathlib import Path

from screening_pipeline import ScreeningPipeline


def main():

    print("=" * 60)
    print("DAY 32 - FINAL AI SCREENING SYSTEM")
    print("=" * 60)

    pipeline = ScreeningPipeline()

    candidate_answers = {

        "Q001":
            "I have experience with Python, SQL, Excel and Power BI.",

        "Q002":
            "I have completed data analyst and data science internships.",

        "Q003":
            "I am available to join immediately.",

        "Q004":
            "My expected salary is around 4 LPA."
    }

    result = pipeline.process_candidate(
        candidate_id="C001",
        answers=candidate_answers
    )

    print()
    print("Candidate ID:", result["candidate_id"])
    print("Screening ID:", result["screening_id"])
    print("Status:", result["status"])
    print("Total Questions:", result["total_questions"])

    print()
    print("SCREENING ANSWERS")
    print("-" * 60)

    for answer in result["answers"]:

        print(
            answer["question_id"],
            "->",
            answer["status"]
        )

        print(
            "Question:",
            answer["question"]
        )

        print(
            "Answer:",
            answer["answer"]
        )

        print()

    output_path = (
        Path(__file__).resolve().parents[1]
        / "output"
        / "final_screening_demo.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    print("=" * 60)
    print("END-TO-END SCREENING DEMO COMPLETED")
    print("Output:", output_path)
    print("=" * 60)


if __name__ == "__main__":
    main()