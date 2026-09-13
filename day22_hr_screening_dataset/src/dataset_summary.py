import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "hr_questions.json"


def main():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        questions = json.load(file)

    categories = Counter(
        question["category"]
        for question in questions
    )

    roles = Counter(
        question["role"]
        for question in questions
    )

    importance = Counter(
        question["scoring_importance"]
        for question in questions
    )

    print()
    print("HR SCREENING DATASET SUMMARY")
    print("=============================")

    print(
        f"Total Questions: {len(questions)}"
    )

    print()
    print("Categories:")

    for category, count in categories.items():

        print(
            f"{category}: {count}"
        )

    print()
    print("Roles:")

    for role, count in roles.items():

        print(
            f"{role}: {count}"
        )

    print()
    print("Scoring Importance:")

    for level, count in importance.items():

        print(
            f"{level}: {count}"
        )


if __name__ == "__main__":
    main()