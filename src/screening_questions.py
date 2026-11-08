"""Load, validate, and filter the root application's screening question bank."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "screening"
    / "hr_screening_questions.json"
)
SUPPORTED_ANSWER_TYPES = {
    "TEXT",
    "NUMBER",
    "YES_NO",
    "SINGLE_CHOICE",
    "MULTIPLE_CHOICE",
    "DATE",
    "DURATION",
    "LOCATION",
    "CURRENCY",
    "NOTICE_PERIOD",
    "SKILL_LIST",
}
SUPPORTED_IMPORTANCE = {"HIGH", "MEDIUM", "LOW", "INFORMATIONAL"}
SUPPORTED_LANGUAGES = {"en", "ml", "hi"}
REQUIRED_FIELDS = {
    "question_id",
    "role_id",
    "role_label",
    "category",
    "question_text",
    "expected_answer_type",
    "mandatory",
    "scoring_importance",
    "display_order",
    "language",
    "is_active",
    "version",
    "created_at",
    "updated_at",
    "follow_up_eligible",
    "translations",
}


def load_dataset() -> dict[str, Any]:
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)
    errors = validate_dataset(dataset)
    if errors:
        raise ValueError("Invalid screening question dataset: " + "; ".join(errors))
    return dataset


def validate_dataset(dataset: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(dataset, dict):
        return ["dataset must be a JSON object"]
    roles = dataset.get("roles")
    categories = dataset.get("categories")
    questions = dataset.get("questions")
    if not isinstance(roles, dict) or not roles:
        errors.append("roles must be a non-empty object")
        roles = {}
    if not isinstance(categories, list) or not categories:
        errors.append("categories must be a non-empty list")
        categories = []
    if not isinstance(questions, list):
        return errors + ["questions must be a list"]

    question_ids: set[str] = set()
    duplicate_content: set[tuple[str, str, str]] = set()
    for index, question in enumerate(questions):
        prefix = f"questions[{index}]"
        if not isinstance(question, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = REQUIRED_FIELDS - question.keys()
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(sorted(missing))}")
            continue
        question_id = question["question_id"]
        if not isinstance(question_id, str) or not question_id.strip():
            errors.append(f"{prefix}.question_id must be non-empty text")
        elif question_id in question_ids:
            errors.append(f"duplicate question_id: {question_id}")
        else:
            question_ids.add(question_id)
        if question.get("role_id") not in roles:
            errors.append(f"{prefix}.role_id is not in the role registry")
        elif question.get("role_label") != roles[question["role_id"]]:
            errors.append(f"{prefix}.role_label does not match role_id")
        if question.get("category") not in categories:
            errors.append(f"{prefix}.category is not in the category registry")
        if question.get("expected_answer_type") not in SUPPORTED_ANSWER_TYPES:
            errors.append(f"{prefix}.expected_answer_type is not supported")
        if question.get("scoring_importance") not in SUPPORTED_IMPORTANCE:
            errors.append(f"{prefix}.scoring_importance is not supported")
        if not isinstance(question.get("mandatory"), bool):
            errors.append(f"{prefix}.mandatory must be boolean")
        if not isinstance(question.get("is_active"), bool):
            errors.append(f"{prefix}.is_active must be boolean")
        if not isinstance(question.get("follow_up_eligible"), bool):
            errors.append(f"{prefix}.follow_up_eligible must be boolean")
        if not isinstance(question.get("display_order"), int) or question["display_order"] < 1:
            errors.append(f"{prefix}.display_order must be a positive integer")
        if question.get("language") not in SUPPORTED_LANGUAGES:
            errors.append(f"{prefix}.language is not supported")
        translations = question.get("translations")
        if not isinstance(translations, dict) or set(translations) != SUPPORTED_LANGUAGES:
            errors.append(f"{prefix}.translations must define en, ml, and hi")
        else:
            for language, translation in translations.items():
                if not isinstance(translation, dict):
                    errors.append(f"{prefix}.translations.{language} must be an object")
                    continue
                status = translation.get("status")
                text = translation.get("question_text")
                if status == "AVAILABLE" and (
                    not isinstance(text, str) or not text.strip()
                ):
                    errors.append(
                        f"{prefix}.translations.{language} requires text when available"
                    )
                elif status == "PENDING" and text is not None:
                    errors.append(
                        f"{prefix}.translations.{language} pending text must be null"
                    )
                elif status not in {"AVAILABLE", "PENDING"}:
                    errors.append(
                        f"{prefix}.translations.{language}.status is invalid"
                    )
            english = translations.get("en", {})
            if (
                english.get("status") != "AVAILABLE"
                or english.get("question_text") != question.get("question_text")
            ):
                errors.append(f"{prefix}.question_text must match its English variant")
        content_key = (
            str(question.get("role_id", "")).casefold(),
            str(question.get("category", "")).casefold(),
            " ".join(str(question.get("question_text", "")).split()).casefold(),
        )
        if content_key in duplicate_content:
            errors.append(f"{prefix} duplicates question text for the same role/category")
        duplicate_content.add(content_key)
    return errors


def get_questions(
    role_id: str | None = None,
    category: str | None = None,
    language: str = "en",
    mandatory: bool | None = None,
    active_only: bool = True,
) -> list[dict[str, Any]]:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError("language must be one of en, ml, or hi")
    dataset = load_dataset()
    normalized_category = category.upper().replace(" ", "_") if category else None
    results = []
    for source in dataset["questions"]:
        if role_id and source["role_id"] != role_id:
            continue
        if normalized_category and source["category"] != normalized_category:
            continue
        if mandatory is not None and source["mandatory"] is not mandatory:
            continue
        if active_only and not source["is_active"]:
            continue
        translation = source["translations"][language]
        if translation["status"] != "AVAILABLE":
            continue
        results.append(
            {
                **source,
                "question_text": translation["question_text"],
                "language": language,
            }
        )
    return sorted(results, key=lambda question: (question["role_id"], question["display_order"]))
