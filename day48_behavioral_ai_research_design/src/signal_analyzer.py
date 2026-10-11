
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_metrics(metrics, weights):
    if set(metrics) != set(weights):
        raise ValueError(
            "Metrics must match the configured signal names exactly."
        )

    for name, value in metrics.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric.")

        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1.")


def analyze_signals(sample, config):
    if not sample.get("consent_recorded", False):
        raise ValueError("Consent must be recorded before analysis.")

    metrics = sample.get("metrics", {})
    weights = config.get("weights", {})

    if not weights:
        raise ValueError("Signal weights are missing.")

    if not all(isinstance(w, (int, float)) and w >= 0 for w in weights.values()):
        raise ValueError("Weights must be non-negative numbers.")

    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("Signal weights must add up to 1.0.")

    validate_metrics(metrics, weights)

    weighted_score = sum(
        metrics[name] * weight
        for name, weight in weights.items()
    ) * 100

    if weighted_score >= 75:
        description = "Relatively consistent signals in this sample"
    elif weighted_score >= 50:
        description = "Variable signals in this sample"
    else:
        description = "Substantially variable signals in this sample"

    event_counts = sample.get("event_counts", {})
    for event_name, count in event_counts.items():
        if (
            isinstance(count, bool)
            or not isinstance(count, int)
            or count < 0
        ):
            raise ValueError(
                f"{event_name} must be a non-negative integer."
            )

    return {
        "session_id": sample.get("session_id", "unknown"),
        "candidate_id": sample.get("candidate_id", "unknown"),
        "data_source": sample.get("data_source", "unspecified"),
        "score_name": config["score_name"],
        "signal_consistency_index": round(weighted_score, 2),
        "signal_description": description,
        "signal_breakdown": {
            name: {
                "observed_value": value,
                "weight": weights[name],
                "weighted_points": round(value * weights[name] * 100, 2)
            }
            for name, value in metrics.items()
        },
        "event_counts": event_counts,
        "limitations": [
            "Descriptive index only; not a hiring or suitability score.",
            "Signals cannot reliably establish honesty, emotion, or intent.",
            "Input values are only as reliable as their measurement method.",
            "Human review and accessible alternatives are required."
        ],
        "human_review_required": True
    }


def run_analysis():
    config_path = BASE_DIR / "config" / "signal_mapping.json"
    sample_path = BASE_DIR / "data" / "sample_behavior_signals.json"
    output_path = BASE_DIR / "output" / "behavioral_analysis.json"

    config = load_json(config_path)
    sample = load_json(sample_path)
    report = analyze_signals(sample, config)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("DAY 48 - BEHAVIORAL AI ANALYSIS")
    print(f"Session ID: {report['session_id']}")
    print(f"Data source: {report['data_source']}")
    print(f"Signal consistency index: {report['signal_consistency_index']}/100")
    print(f"Description: {report['signal_description']}")
    print(f"Signals analyzed: {len(report['signal_breakdown'])}")
    print(f"Human review required: {report['human_review_required']}")
    print(f"Report saved: {output_path}")


if __name__ == "__main__":
    run_analysis()
