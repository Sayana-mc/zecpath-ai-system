
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

ALLOWED_EVENTS = {
    "tab_switch_count",
    "focus_loss_count",
    "external_voice_events",
    "repeated_looking_away_events",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_events(events, thresholds):
    if set(events) != set(thresholds):
        raise ValueError(
            "Event names must match configured threshold names."
        )

    for name, count in events.items():
        if (
            isinstance(count, bool)
            or not isinstance(count, int)
            or count < 0
        ):
            raise ValueError(
                f"{name} must be a non-negative integer."
            )


def get_risk_level(score, risk_levels):
    if score <= risk_levels["low_max"]:
        return "LOW"
    if score <= risk_levels["moderate_max"]:
        return "MODERATE"
    return "HIGH"


def analyze_integrity(sample, config):
    if not sample.get("consent_recorded", False):
        raise ValueError("Recorded consent is required.")

    if not isinstance(sample.get("events"), dict):
        raise ValueError("Events must be provided as an object.")

    thresholds = config.get("thresholds", {})
    events = sample["events"]

    if not thresholds or set(thresholds) != ALLOWED_EVENTS:
        raise ValueError("Integrity threshold configuration is invalid.")

    for name, rule in thresholds.items():
        if (
            not isinstance(rule.get("warning_at"), int)
            or isinstance(rule.get("warning_at"), bool)
            or rule["warning_at"] < 1
            or not isinstance(rule.get("risk_points"), int)
            or isinstance(rule.get("risk_points"), bool)
            or rule["risk_points"] < 0
        ):
            raise ValueError(f"Invalid threshold rule: {name}")

    validate_events(events, thresholds)

    flags = []
    risk_score = 0

    for name, count in events.items():
        rule = thresholds[name]

        if count >= rule["warning_at"]:
            risk_score += rule["risk_points"]

            flags.append({
                "event": name,
                "observed_count": count,
                "threshold": rule["warning_at"],
                "risk_tag": rule["tag"],
                "severity": "WARNING",
                "message": (
                    f"{name} reached the configured review threshold."
                )
            })

    bonus_rule = config.get("combined_pattern_bonus", {})
    minimum_categories = bonus_rule.get(
        "minimum_flagged_categories", 3
    )
    bonus_points = bonus_rule.get("risk_points", 0)

    if len(flags) >= minimum_categories:
        risk_score += bonus_points
        flags.append({
            "event": "combined_pattern",
            "observed_count": len(flags),
            "threshold": minimum_categories,
            "risk_tag": "MULTIPLE_SIGNAL_PATTERN",
            "severity": "REVIEW",
            "message": (
                "Multiple event categories crossed configured thresholds."
            )
        })

    risk_score = min(risk_score, 100)

    risk_levels = config["risk_levels"]
    risk_level = get_risk_level(risk_score, risk_levels)

    if flags:
        status = "REVIEW_REQUIRED"
        alert = (
            "Integrity review warning: please verify the recorded events "
            "and allow the candidate to explain them."
        )
    else:
        status = "NO_THRESHOLD_EXCEEDED"
        alert = "No configured event threshold was exceeded."

    behavior_context = sample.get("behavioral_context", {})

    return {
        "session_id": sample.get("session_id", "unknown"),
        "candidate_id": sample.get("candidate_id", "unknown"),
        "data_source": sample.get("data_source", "unspecified"),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "status": status,
        "warning_message": alert,
        "flags": flags,
        "event_counts": events,
        "behavioral_context": {
            "source": behavior_context.get("source", "not_provided"),
            "signal_consistency_index": behavior_context.get(
                "signal_consistency_index"
            ),
            "used_in_risk_score": False
        },
        "decision": "HUMAN_REVIEW_ONLY",
        "automatic_rejection": False,
        "limitations": [
            "Flags indicate events for review, not confirmed cheating.",
            "External audio events require a separate validated detector.",
            "Tab and focus events require a suitable event collector.",
            "Looking away can have innocent or accessibility-related causes.",
            "Synthetic or unverified event counts must not support real decisions."
        ]
    }


def run_analysis():
    config = load_json(BASE_DIR / "config" / "integrity_rules.json")
    sample = load_json(BASE_DIR / "data" / "sample_interview_events.json")

    report = analyze_integrity(sample, config)

    output_path = BASE_DIR / "output" / "integrity_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("DAY 49 - MALPRACTICE & INTEGRITY DETECTION")
    print(f"Session ID: {report['session_id']}")
    print(f"Risk score: {report['risk_score']}/100")
    print(f"Risk level: {report['risk_level']}")
    print(f"Status: {report['status']}")
    print(f"Flags generated: {len(report['flags'])}")
    print(f"Decision: {report['decision']}")
    print(f"Automatic rejection: {report['automatic_rejection']}")
    print(f"Report saved: {output_path}")


if __name__ == "__main__":
    run_analysis()
