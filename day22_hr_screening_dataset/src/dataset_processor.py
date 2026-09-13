import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "hr_questions.json"
OUTPUT_FILE = BASE_DIR / "output" / "ai_screening_questions.json"


REQUIRED_FIELDS = [
    "question_id",
    "role",
    "category",
    "question",
    "expected_answer_type",
    "mandatory",
    "scoring_importance",
    "language",
    "template"
]


VALID_CATEGORIES = {
    "Introduction",
    "Education",
    "Experience",
    "Skills",
    "Location",
    "Salary",
    "Notice Period"
}


VALID_IMPORTANCE = {
    "high",
    "medium",
    "low"
}


def load_questions():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def validate_question(question):

    errors = []

    for field in REQUIRED_FIELDS:

        if field not in question:
            errors.append(
                f"Missing field: {field}"
            )

    if question.get("category") not in VALID_CATEGORIES:

        errors.append(
            "Invalid category"
        )

    if question.get("scoring_importance") not in VALID_IMPORTANCE:

        errors.append(
            "Invalid scoring importance"
        )

    if not isinstance(
        question.get("mandatory"),
        bool
    ):

        errors.append(
            "mandatory must be true or false"
        )

    return errors


def create_ai_object(question):

    return {
        "question_id": question["question_id"],
        "role": question["role"],
        "category": question["category"],
        "question": question["question"],
        "expected_answer_type": question[
            "expected_answer_type"
        ],
        "mandatory": question["mandatory"],
        "scoring_importance": question[
            "scoring_importance"
        ],
        "language": question["language"],
        "template": question["template"]
    }


def main():

    print("Starting HR Screening Dataset Processor...")

    questions = load_questions()

    valid_questions = []
    validation_errors = []

    for question in questions:

        errors = validate_question(question)

        if errors:

            validation_errors.append({
                "question_id": question.get(
                    "question_id",
                    "UNKNOWN"
                ),
                "errors": errors
            })

        else:

            valid_questions.append(
                create_ai_object(question)
            )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {
        "dataset_name": "HR Screening Question Bank",
        "version": "1.0",
        "total_questions": len(questions),
        "valid_questions": len(valid_questions),
        "invalid_questions": len(
            validation_errors
        ),
        "questions": valid_questions,
        "validation_errors": validation_errors
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("Dataset processing completed.")
    print(
        f"Total questions: {len(questions)}"
    )
    print(
        f"Valid questions: {len(valid_questions)}"
    )
    print(
        f"Invalid questions: {len(validation_errors)}"
    )
    print(
        f"Output file: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()