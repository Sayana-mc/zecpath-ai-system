from pathlib import Path

from .experience_engine import (
    process_all_resumes,
)


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = (
    BASE_DIR / "input"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output"
    / "structured"
)

TARGET_ROLE = "Data Analyst"


def main():

    print(
        "Day 10 - Experience Parsing & Relevance Engine"
    )

    print("=" * 60)

    print(
        f"Input directory : {INPUT_DIR}"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    print(
        f"Target role     : {TARGET_ROLE}"
    )

    results = process_all_resumes(
        INPUT_DIR,
        OUTPUT_DIR,
        TARGET_ROLE,
    )

    print()

    print(
        f"Processed resumes: {len(results)}"
    )

    print(
        f"Successful: {len(results)}"
    )

    print()

    print(
        f"Structured output saved to:"
    )

    print(
        OUTPUT_DIR
    )


if __name__ == "__main__":
    main()