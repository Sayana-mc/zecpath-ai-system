
import json
from pathlib import Path

from day54_optimization_refinement.src.accuracy_analyzer import (
    analyze_thresholds
)
from day54_optimization_refinement.src.benchmark import (
    benchmark_processing
)
from day54_optimization_refinement.src.intent_detector import (
    detect_intent
)
from day54_optimization_refinement.src.refined_scoring import (
    evaluate_candidate
)


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def build_markdown(config, analysis, benchmark, intent_result, scoring):
    baseline = analysis["configured_threshold_baseline"]
    best = analysis["best_threshold_by_f1_on_this_sample"]

    lines = [
        "# Day 54 — Optimization & Refinement Report",
        "",
        "## 1. Objective",
        "",
        "Evaluate scoring errors, compare thresholds, refine intent matching,",
        "check round consistency and benchmark local processing time.",
        "",
        "## 2. Dataset and limitations",
        "",
        f"- Labelled examples: {analysis['dataset_count']}",
        f"- Dataset type: {analysis['dataset_type']}",
        f"- Interpretation: {analysis['interpretation']}",
        "",
        "## 3. Baseline error analysis",
        "",
        f"- Threshold: {baseline['threshold']}",
        f"- True positives: {baseline['true_positive']}",
        f"- False positives: {baseline['false_positive']}",
        f"- True negatives: {baseline['true_negative']}",
        f"- False negatives: {baseline['false_negative']}",
        f"- Accuracy: {baseline['accuracy']:.2%}",
        f"- Precision: {baseline['precision']:.2%}",
        f"- Recall: {baseline['recall']:.2%}",
        f"- Specificity: {baseline['specificity']:.2%}",
        f"- F1 score: {baseline['f1_score']:.4f}",
        f"- False-positive IDs: {baseline['false_positive_ids']}",
        f"- False-negative IDs: {baseline['false_negative_ids']}",
        "",
        "## 4. Threshold comparison",
        "",
        "| Threshold | Accuracy | Precision | Recall | F1 | FP | FN |",
        "|---:|---:|---:|---:|---:|---:|---:|"
    ]

    for result in analysis["threshold_comparisons"]:
        lines.append(
            f"| {result['threshold']} "
            f"| {result['accuracy']:.2%} "
            f"| {result['precision']:.2%} "
            f"| {result['recall']:.2%} "
            f"| {result['f1_score']:.4f} "
            f"| {result['false_positive']} "
            f"| {result['false_negative']} |"
        )

    lines.extend([
        "",
        "### Best sample threshold",
        "",
        f"- Threshold with highest sample F1: {best['threshold']}",
        f"- Sample F1: {best['f1_score']:.4f}",
        "- Deployment approval: NOT APPROVED",
        f"- Reason: {analysis['approval_note']}",
        "",
        "## 5. Intent detection test",
        "",
        f"- Input: {intent_result['input']}",
        f"- Detected intent: {intent_result['result']['intent']}",
        f"- Status: {intent_result['result']['status']}",
        "",
        "## 6. Refined scoring example",
        "",
        f"- Advisory band: {scoring['advisory_band']}",
        f"- Status: {scoring['status']}",
        f"- Round average: {scoring['round_average']}",
        f"- Round score gap: {scoring['round_score_gap']}",
        f"- Review reasons: {scoring['review_reasons']}",
        "- Human review required: YES",
        "",
        "## 7. Processing benchmark",
        "",
        f"- Iterations per operation: {benchmark['iterations_per_operation']}",
        f"- Scoring average (ms): {benchmark['scoring']['average_milliseconds']}",
        f"- Intent average (ms): {benchmark['intent_detection']['average_milliseconds']}",
        f"- Note: {benchmark['measurement_note']}",
        "",
        "## 8. Optimization actions",
        "",
        "1. Evaluate false positives and false negatives against labelled outcomes.",
        "2. Compare candidate thresholds using precision, recall and F1.",
        "3. Keep threshold changes disabled until independently validated.",
        "4. Send unknown or ambiguous intents for clarification.",
        "5. Flag incomplete rounds and large score gaps for human review.",
        "6. Benchmark against a recorded baseline before claiming speed improvements.",
        "",
        "## 9. Conclusion",
        "",
        "This run demonstrates an optimization and measurement workflow. "
        "The synthetic dataset cannot establish improved real-world hiring accuracy. "
        "Final employment decisions must remain under qualified human review.",
        ""
    ])

    return "\n".join(lines)


def main():
    root = Path(__file__).resolve().parents[1]
    config = load_json(root / "config" / "optimization_config.json")
    dataset = load_json(root / "data" / "labelled_evaluations.json")
    examples = dataset["examples"]

    analysis = analyze_thresholds(examples, config["tuning"])

    intent_text = "Explain this candidate's role fit"
    intent_result = {
        "input": intent_text,
        "result": detect_intent(intent_text)
    }

    scoring = evaluate_candidate(
        score=82.25,
        round_scores=[85, 80, 75, 90, 80],
        completed_rounds=5,
        thresholds=config["thresholds"],
        consistency_config=config["consistency"],
        review_config=config["review"],
        intent=intent_result["result"]["intent"]
    )

    benchmark = benchmark_processing(
        config,
        iterations=config["benchmark"]["iterations"]
    )

    output_dir = root / "output"

    write_json(output_dir / "accuracy_analysis.json", analysis)
    write_json(output_dir / "benchmark_results.json", benchmark)
    (output_dir / "optimization_report.md").write_text(
        build_markdown(
            config, analysis, benchmark, intent_result, scoring
        ),
        encoding="utf-8"
    )

    print("=" * 64)
    print("DAY 54 - OPTIMIZATION & REFINEMENT")
    print("=" * 64)
    print(f"Labelled demo examples : {analysis['dataset_count']}")
    print(f"Baseline threshold     : {analysis['configured_threshold_baseline']['threshold']}")
    print(f"Baseline F1            : {analysis['configured_threshold_baseline']['f1_score']}")
    print(f"Best sample threshold  : {analysis['best_threshold_by_f1_on_this_sample']['threshold']}")
    print(f"Intent                 : {intent_result['result']['intent']}")
    print(f"Scoring status         : {scoring['status']}")
    print(f"Benchmark iterations   : {benchmark['iterations_per_operation']}")
    print("-" * 64)
    print("Generated:")
    print(output_dir / "accuracy_analysis.json")
    print(output_dir / "optimization_report.md")
    print(output_dir / "benchmark_results.json")
    print("=" * 64)


if __name__ == "__main__":
    main()
