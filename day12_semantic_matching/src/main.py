from pathlib import Path

from .matching_engine import (
    process_all_matches
)


BASE_DIR = Path(__file__).resolve().parent.parent

RESUME_DIR = (
    BASE_DIR /
    "input" /
    "resumes"
)

JOB_DIR = (
    BASE_DIR /
    "input" /
    "jobs"
)

OUTPUT_DIR = (
    BASE_DIR /
    "output" /
    "matches"
)


def main():

    print(
        "Day 12 - Semantic Matching Engine"
    )

    print("=" * 55)

    print(
        f"Resume directory : {RESUME_DIR}"
    )

    print(
        f"Job directory    : {JOB_DIR}"
    )

    print(
        f"Output directory : {OUTPUT_DIR}"
    )

    print()

    results = process_all_matches(
        RESUME_DIR,
        JOB_DIR,
        OUTPUT_DIR
    )

    print(
        f"Processed resumes: {len(results)}"
    )

    print(
        "Semantic matching completed."
    )

    print(
        f"Results saved to: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()