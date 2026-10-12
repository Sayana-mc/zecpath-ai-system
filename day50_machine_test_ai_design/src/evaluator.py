
import json
from pathlib import Path


ALLOWED_TASK_TYPES = {
    "coding",
    "debugging",
    "file_based",
    "mini_system_design",
}

METRIC_NAMES = {
    "efficiency",
    "code_quality",
    "problem_solving",
}


def load_json(path):
    """Load a JSON file from disk."""
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_config(config):
    """Validate scoring weights and policy configuration."""
    weights = config.get("weights", {})

    expected = {
        "correctness",
        "efficiency",
        "code_quality",
        "problem_solving",
        "time_management",
    }

    if set(weights) != expected:
        raise ValueError("Scoring weights must define all five categories.")

    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or value < 0
        for value in weights.values()
    ):
        raise ValueError("Scoring weights must be non-negative numbers.")

    if sum(weights.values()) != 100:
        raise ValueError("Scoring weights must add up to 100.")

    time_policy = config.get("time_policy", {})
    full_credit = time_policy.get("full_credit_ratio")
    deadline = time_policy.get("minimum_credit_ratio")
    minimum_factor = time_policy.get("minimum_time_factor")

    if not all(
        isinstance(value, (int, float)) and not isinstance(value, bool)
        for value in (full_credit, deadline, minimum_factor)
    ):
        raise ValueError("Time policy values must be numeric.")

    if not (0 < full_credit < deadline):
        raise ValueError("Time ratios must satisfy 0 < full credit < deadline.")

    if not (0 <= minimum_factor <= 1):
        raise ValueError("Minimum time factor must be between 0 and 1.")

    thresholds = config.get("decision_thresholds", {})
    strong = thresholds.get("strong")
    competent = thresholds.get("competent")

    if not (
        isinstance(strong, (int, float))
        and isinstance(competent, (int, float))
        and 0 <= competent < strong <= 100
    ):
        raise ValueError("Invalid decision thresholds.")

    safeguards = config.get("safeguards", {})
    if safeguards.get("automatic_rejection") is not False:
        raise ValueError("Automatic rejection must remain disabled.")

    if safeguards.get("human_review_required") is not True:
        raise ValueError("Human review must remain enabled.")


def validate_submission(data):
    """Check required fields and reject malformed evaluation inputs."""
    if not isinstance(data, dict):
        raise ValueError("Submission must be a JSON object.")

    for key in ("session_id", "candidate_id", "task", "time", "submission"):
        if key not in data:
            raise ValueError(f"Missing required field: {key}")

    task = data["task"]
    time_data = data["time"]
    submission = data["submission"]

    if not isinstance(task, dict) or not isinstance(time_data, dict):
        raise ValueError("Task and time must be JSON objects.")

    if not isinstance(submission, dict):
        raise ValueError("Submission details must be a JSON object.")

    if task.get("task_type") not in ALLOWED_TASK_TYPES:
        raise ValueError("Unsupported task type.")

    if not task.get("task_id") or not task.get("title"):
        raise ValueError("Task ID and title are required.")

    for field in ("allotted_seconds", "elapsed_seconds"):
        value = time_data.get(field)
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
        ):
            raise ValueError(f"{field} must be a non-negative integer.")

    if time_data["allotted_seconds"] <= 0:
        raise ValueError("Allotted time must be greater than zero.")

    if not isinstance(submission.get("code_snapshot", ""), str):
        raise ValueError("Code snapshot must be text.")

    if not isinstance(submission.get("answer_text", ""), str):
        raise ValueError("Answer text must be text.")

    results = submission.get("execution_results", [])
    if not isinstance(results, list):
        raise ValueError("Execution results must be a list.")

    seen_test_ids = set()
    for result in results:
        if not isinstance(result, dict):
            raise ValueError("Each execution result must be an object.")

        test_id = result.get("test_id")
        passed = result.get("passed")

        if not isinstance(test_id, str) or not test_id.strip():
            raise ValueError("Each result needs a test ID.")

        if test_id in seen_test_ids:
            raise ValueError("Duplicate test IDs are not allowed.")
        seen_test_ids.add(test_id)

        if not isinstance(passed, bool):
            raise ValueError("Test passed value must be true or false.")

    metrics = submission.get("metrics", {})
    if not isinstance(metrics, dict):
        raise ValueError("Metrics must be an object.")

    for metric in METRIC_NAMES:
        value = metrics.get(metric)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0 <= value <= 100
        ):
            raise ValueError(
                f"Metric '{metric}' must be a number between 0 and 100."
            )

    snapshots = submission.get("snapshot_history", [])
    if not isinstance(snapshots, list):
        raise ValueError("Snapshot history must be a list.")

    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            raise ValueError("Each snapshot must be an object.")
        if (
            isinstance(snapshot.get("elapsed_seconds"), bool)
            or not isinstance(snapshot.get("elapsed_seconds"), int)
            or snapshot["elapsed_seconds"] < 0
        ):
            raise ValueError("Snapshot time must be a non-negative integer.")
        if not isinstance(snapshot.get("content"), str):
            raise ValueError("Snapshot content must be text.")

    return data


def calculate_correctness(results):
    """Calculate correctness from supplied test results."""
    total = len(results)

    if total == 0:
        return 0.0, 0, 0

    passed = sum(1 for result in results if result["passed"])
    score = (passed / total) * 100

    return round(score, 2), passed, total


def calculate_time_management(time_data, config):
    """
    Calculate a separate time-management score.

    Correctness is not multiplied by a time factor.
    Time beyond the allotted deadline receives zero time-management points.
    """
    elapsed = time_data["elapsed_seconds"]
    allotted = time_data["allotted_seconds"]
    ratio = elapsed / allotted

    policy = config["time_policy"]
    full_credit_ratio = policy["full_credit_ratio"]
    deadline_ratio = policy["minimum_credit_ratio"]
    minimum_factor = policy["minimum_time_factor"]

    if ratio <= full_credit_ratio:
        factor = 1.0
    elif ratio <= deadline_ratio:
        progress = (ratio - full_credit_ratio) / (
            deadline_ratio - full_credit_ratio
        )
        factor = 1.0 - progress * (1.0 - minimum_factor)
    else:
        factor = 0.0

    score = round(factor * 100, 2)

    return {
        "elapsed_seconds": elapsed,
        "allotted_seconds": allotted,
        "time_ratio": round(ratio, 3),
        "time_management_score": score,
        "submitted_within_deadline": elapsed <= allotted,
    }


def evaluate_submission(data, config):
    """Generate a weighted score and a review-oriented report."""
    validate_config(config)
    validate_submission(data)

    submission = data["submission"]
    weights = config["weights"]

    correctness, passed, total = calculate_correctness(
        submission["execution_results"]
    )
    time_result = calculate_time_management(data["time"], config)

    raw_metrics = {
        "correctness": correctness,
        "efficiency": submission["metrics"]["efficiency"],
        "code_quality": submission["metrics"]["code_quality"],
        "problem_solving": submission["metrics"]["problem_solving"],
        "time_management": time_result["time_management_score"],
    }

    breakdown = {}
    for name, score in raw_metrics.items():
        weight = weights[name]
        breakdown[name] = {
            "raw_score": round(score, 2),
            "weight": weight,
            "weighted_points": round(score * weight / 100, 2),
        }

    final_score = round(
        sum(item["weighted_points"] for item in breakdown.values()), 2
    )

    thresholds = config["decision_thresholds"]
    if final_score >= thresholds["strong"]:
        performance_band = "STRONG"
    elif final_score >= thresholds["competent"]:
        performance_band = "COMPETENT"
    else:
        performance_band = "NEEDS_FURTHER_REVIEW"

    review_flags = []
    if total == 0:
        review_flags.append("NO_EXECUTION_TEST_RESULTS")
    if not time_result["submitted_within_deadline"]:
        review_flags.append("SUBMISSION_AFTER_DEADLINE")
    if not submission.get("code_snapshot", "").strip() and not (
        submission.get("answer_text", "").strip()
    ):
        review_flags.append("EMPTY_SUBMISSION")

    safeguards = config["safeguards"]

    return {
        "session_id": data["session_id"],
        "candidate_id": data["candidate_id"],
        "task": data["task"],
        "evaluation_status": "EVALUATED",
        "task_type": data["task"]["task_type"],
        "test_results": {
            "passed": passed,
            "total": total,
            "correctness_score": correctness,
        },
        "time_analysis": time_result,
        "score_breakdown": breakdown,
        "final_score": final_score,
        "maximum_score": 100,
        "performance_band": performance_band,
        "review_flags": review_flags,
        "capture_summary": {
            "code_snapshot_captured": bool(
                submission.get("code_snapshot", "").strip()
            ),
            "snapshot_count": len(submission.get("snapshot_history", [])),
            "execution_results_captured": total > 0,
            "answer_text_captured": bool(
                submission.get("answer_text", "").strip()
            ),
        },
        "decision": {
            "automatic_rejection": safeguards["automatic_rejection"],
            "human_review_required": safeguards["human_review_required"],
            "recommendation": "REVIEW_BY_HUMAN_EVALUATOR",
        },
        "limitations": [
            "Execution results are supplied input and are not independently verified.",
            "Efficiency, code quality, and problem-solving scores are supplied rubric scores.",
            "The submitted code is captured but never executed by this prototype.",
            "Scores are decision support and must not be the sole basis for hiring."
        ],
    }


def run_evaluation(input_path, config_path, output_path):
    data = load_json(input_path)
    config = load_json(config_path)
    report = evaluate_submission(data, config)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("DAY 50 - MACHINE TEST AI EVALUATION")
    print("-" * 42)
    print(f"Session ID: {report['session_id']}")
    print(f"Candidate ID: {report['candidate_id']}")
    print(f"Task type: {report['task_type']}")
    print(
        f"Tests passed: {report['test_results']['passed']}/"
        f"{report['test_results']['total']}"
    )
    print(f"Final score: {report['final_score']}/100")
    print(f"Performance band: {report['performance_band']}")
    print(f"Human review required: "
          f"{report['decision']['human_review_required']}")
    print(f"Report saved: {output.resolve()}")

    return report
