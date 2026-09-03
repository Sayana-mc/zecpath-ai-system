from pathlib import Path

from src.education_engine import process_all_resumes


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = (
    PROJECT_ROOT / "input"
)

OUTPUT_DIR = (
    PROJECT_ROOT / "output" / "structured"
)


def main():
    print(
        "Day 11 - Education & Certification Parsing"
    )

    print("=" * 55)

    print(
        f"Input directory : {INPUT_DIR}"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    results = process_all_resumes(
        INPUT_DIR,
        OUTPUT_DIR,
        target_role="data analyst",
    )

    successful = sum(
        1
        for result in results
        if result.get("status") == "success"
    )

    print()
    print(
        f"Processed resumes: {len(results)}"
    )

    print(
        f"Successful: {successful}"
    )

    print()
    print(
        "Structured academic profiles saved to:"
    )

    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()