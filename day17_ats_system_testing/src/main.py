from pathlib import Path

from .testing_engine import (
    load_day14_results,
    create_manual_review_template,
    load_manual_review,
    validate_manual_review,
    merge_ai_and_manual_results,
    calculate_metrics,
    calculate_category_metrics,
    find_mismatches,
    save_json,
    save_mismatches,
)


BASE_DIR = Path(__file__).resolve().parent.parent

DAY14_OUTPUT = (
    BASE_DIR.parent
    / "day14_candidate_ranking"
    / "output"
    / "rankings"
)

INPUT_DIR = BASE_DIR / "input"

OUTPUT_DIR = BASE_DIR / "output"

MANUAL_REVIEW_FILE = (
    INPUT_DIR / "manual_review.csv"
)


def main():

    print()
    print("=" * 65)
    print("DAY 17 - ATS SYSTEM TESTING")
    print("=" * 65)

    print()
    print("Day 14 input:")
    print(DAY14_OUTPUT)

    print()
    print("Manual review file:")
    print(MANUAL_REVIEW_FILE)

    print()
    print("-" * 65)

    ai_records = load_day14_results(
        DAY14_OUTPUT
    )

    print(
        f"AI candidate-job records : "
        f"{len(ai_records)}"
    )

    if not MANUAL_REVIEW_FILE.exists():

        create_manual_review_template(
            ai_records,
            MANUAL_REVIEW_FILE,
        )

        print()
        print(
            "[CREATED] Manual review template:"
        )
        print(MANUAL_REVIEW_FILE)

        print()
        print(
            "ACTION REQUIRED:"
        )
        print(
            "Open input/manual_review.csv "
            "and fill manual_decision and "
            "profile_category."
        )

        return

    manual_records = load_manual_review(
        MANUAL_REVIEW_FILE
    )

    print(
        f"Manual review records : "
        f"{len(manual_records)}"
    )

    validate_manual_review(
        manual_records
    )

    merged_records = merge_ai_and_manual_results(
        ai_records,
        manual_records,
    )

    print(
        f"Matched testing records : "
        f"{len(merged_records)}"
    )

    if not merged_records:

        raise ValueError(
            "No AI/manual records could be matched."
        )

    metrics = calculate_metrics(
        merged_records
    )

    category_metrics = calculate_category_metrics(
        merged_records
    )

    mismatches = find_mismatches(
        merged_records
    )

    accuracy_file = (
        OUTPUT_DIR
        / "accuracy_metrics.json"
    )

    category_file = (
        OUTPUT_DIR
        / "category_metrics.json"
    )

    mismatch_file = (
        OUTPUT_DIR
        / "mismatch_cases.csv"
    )

    summary_file = (
        OUTPUT_DIR
        / "testing_summary.json"
    )

    save_json(
        accuracy_file,
        metrics,
    )

    save_json(
        category_file,
        category_metrics,
    )

    save_mismatches(
        mismatch_file,
        mismatches,
    )

    summary = {
        "test_records": len(merged_records),
        "mismatch_count": len(mismatches),
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "categories_tested": sorted(
            category_metrics.keys()
        ),
        "outputs": [
            str(accuracy_file),
            str(category_file),
            str(mismatch_file),
        ],
    }

    save_json(
        summary_file,
        summary,
    )

    print()
    print("=" * 65)
    print("ATS TESTING RESULTS")
    print("=" * 65)

    print(
        f"Total test cases : "
        f"{metrics['total_cases']}"
    )

    print(
        f"Accuracy         : "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Precision        : "
        f"{metrics['precision']:.4f}"
    )

    print(
        f"Recall           : "
        f"{metrics['recall']:.4f}"
    )

    print(
        f"F1 Score         : "
        f"{metrics['f1_score']:.4f}"
    )

    print()
    print(
        f"True Positives   : "
        f"{metrics['true_positive']}"
    )

    print(
        f"True Negatives   : "
        f"{metrics['true_negative']}"
    )

    print(
        f"False Positives  : "
        f"{metrics['false_positive']}"
    )

    print(
        f"False Negatives  : "
        f"{metrics['false_negative']}"
    )

    print()
    print(
        f"Mismatch cases   : "
        f"{len(mismatches)}"
    )

    print()
    print("Category testing:")

    for category, result in category_metrics.items():

        print(
            f"  {category:<15} "
            f"Accuracy={result['accuracy']:.4f} "
            f"Precision={result['precision']:.4f} "
            f"Recall={result['recall']:.4f}"
        )

    print()
    print("Output files:")
    print(
        "  output/accuracy_metrics.json"
    )
    print(
        "  output/category_metrics.json"
    )
    print(
        "  output/mismatch_cases.csv"
    )
    print(
        "  output/testing_summary.json"
    )

    print()
    print("=" * 65)
    print(
        "ATS system testing completed successfully."
    )
    print("=" * 65)


if __name__ == "__main__":
    main()