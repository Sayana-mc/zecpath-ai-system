import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "hr_questions.json"


def load_questions():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def test_dataset_is_not_empty():

    questions = load_questions()

    assert len(questions) > 0


def test_required_categories_exist():

    questions = load_questions()

    categories = {
        question["category"]
        for question in questions
    }

    required_categories = {
        "Introduction",
        "Education",
        "Experience",
        "Skills",
        "Location",
        "Salary",
        "Notice Period"
    }

    assert required_categories.issubset(
        categories
    )


def test_question_ids_are_unique():

    questions = load_questions()

    ids = [
        question["question_id"]
        for question in questions
    ]

    assert len(ids) == len(set(ids))


def test_required_fields_exist():

    questions = load_questions()

    required_fields = {
        "question_id",
        "role",
        "category",
        "question",
        "expected_answer_type",
        "mandatory",
        "scoring_importance",
        "language",
        "template"
    }

    for question in questions:

        assert required_fields.issubset(
            question.keys()
        )


def test_mandatory_field_is_boolean():

    questions = load_questions()

    for question in questions:

        assert isinstance(
            question["mandatory"],
            bool
        )