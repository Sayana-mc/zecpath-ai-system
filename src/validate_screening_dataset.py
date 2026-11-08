"""Command-line validation for the root screening question dataset."""

import json

from .screening_questions import DATASET_PATH, validate_dataset


def main() -> int:
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)
    errors = validate_dataset(dataset)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        f"Valid dataset: {len(dataset['questions'])} questions, "
        f"{len(dataset['roles'])} registered roles, "
        f"{len(dataset['categories'])} categories."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
