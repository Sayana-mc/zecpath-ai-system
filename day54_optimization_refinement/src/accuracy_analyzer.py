
def calculate_metrics(examples, threshold):
    tp = fp = tn = fn = 0
    false_positives = []
    false_negatives = []

    for item in examples:
        actual = item["ground_truth_suitable"]
        predicted = item["score"] >= threshold

        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
            false_positives.append(item["id"])
        elif not predicted and not actual:
            tn += 1
        else:
            fn += 1
            false_negatives.append(item["id"])

    total = len(examples)
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "threshold": threshold,
        "sample_count": total,
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "specificity": round(specificity, 4),
        "f1_score": round(f1, 4),
        "false_positive_ids": false_positives,
        "false_negative_ids": false_negatives
    }


def analyze_thresholds(examples, tuning_config):
    if not examples:
        raise ValueError("At least one labelled example is required.")

    for item in examples:
        if not isinstance(item.get("ground_truth_suitable"), bool):
            raise ValueError(
                f"{item.get('id')}: ground_truth_suitable must be boolean."
            )

        score = item.get("score")
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError(f"{item.get('id')}: score must be numeric.")

        if not 0 <= score <= 100:
            raise ValueError(f"{item.get('id')}: score must be 0-100.")

    minimum = tuning_config["minimum_threshold"]
    maximum = tuning_config["maximum_threshold"]
    step = tuning_config["step"]

    if (
        isinstance(minimum, bool)
        or isinstance(maximum, bool)
        or isinstance(step, bool)
        or not all(isinstance(v, int) for v in (minimum, maximum, step))
        or not 0 <= minimum < maximum <= 100
        or step <= 0
    ):
        raise ValueError("Invalid threshold tuning configuration.")

    results = [
        calculate_metrics(examples, threshold)
        for threshold in range(minimum, maximum + 1, step)
    ]

    # Maximize F1. On a tie, prefer the higher threshold as a
    # conservative choice for reducing false-positive predictions.
    best = max(results, key=lambda result: (
        result["f1_score"],
        result["threshold"]
    ))

    configured_80 = calculate_metrics(examples, 80)

    return {
        "dataset_count": len(examples),
        "dataset_type": "SYNTHETIC_LABELLED_EXAMPLES",
        "interpretation": (
            "Metrics measure agreement with the supplied demo labels only. "
            "They are not evidence of real-world hiring accuracy."
        ),
        "configured_threshold_baseline": configured_80,
        "threshold_comparisons": results,
        "best_threshold_by_f1_on_this_sample": best,
        "threshold_change_approved": False,
        "approval_note": (
            "Do not deploy a new threshold based on this small synthetic "
            "sample. Validate on representative, independently labelled "
            "data and review false positives and false negatives first."
        )
    }
