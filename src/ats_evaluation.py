"""Small, dependency-free metrics helpers for human-reviewed ATS labels."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def binary_metrics(
    expected: list[bool], predicted: list[bool]
) -> dict[str, Any]:
    if not expected or len(expected) != len(predicted):
        raise ValueError("Expected and predicted labels must be non-empty and aligned.")
    true_positive = sum(actual and guess for actual, guess in zip(expected, predicted))
    false_positive = sum(not actual and guess for actual, guess in zip(expected, predicted))
    false_negative = sum(actual and not guess for actual, guess in zip(expected, predicted))
    true_negative = sum(not actual and not guess for actual, guess in zip(expected, predicted))
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "sample_count": len(expected),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": (true_positive + true_negative) / len(expected),
        "confusion_matrix": {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "true_negative": true_negative,
        },
    }


def load_reviewed_pairs(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    return [
        row
        for row in rows
        if row.get("review_status") == "REVIEWED"
        and row.get("expected_match") in {"true", "false"}
        and row.get("predicted_match") in {"true", "false"}
    ]
