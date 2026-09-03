from pathlib import Path

from src.segmentation_engine import process_all_resumes


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = (
    BASE_DIR.parent /
    "day5_extraction" /
    "output"
)

OUTPUT_DIR = (
    BASE_DIR /
    "output" /
    "labeled"
)


def main():

    print("Day 8 - Resume Section Segmentation")
    print("=" * 50)

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    if not INPUT_DIR.exists():

        print(
            f"\nERROR: Input directory does not exist:\n"
            f"{INPUT_DIR}"
        )

        return

    results = process_all_resumes(
        INPUT_DIR,
        OUTPUT_DIR
    )

    print(
        f"\nProcessed resumes: {len(results)}"
    )

    success_count = sum(
        1
        for result in results
        if result.get("status") == "success"
    )

    print(
        f"Successful: {success_count}"
    )

    print(
        f"\nLabeled output saved to:\n"
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()