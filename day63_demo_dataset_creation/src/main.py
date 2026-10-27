"""Command-line entry point for the Day 63 demo dataset builder."""

from .dataset_builder import OUTPUT_FILE, build_demo_dataset


def main() -> None:
    dataset = build_demo_dataset()
    screened_count = sum(
        candidate["screening_output"] is not None
        for candidate in dataset["candidates"]
    )
    print("Demo dataset created.")
    print(f"Candidates: {dataset['candidate_count']}")
    print(f"Candidates with screening output: {screened_count}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
