
import json
from pathlib import Path


REQUIRED_ROUNDS = {
    "ats",
    "screening",
    "hr_interview",
    "technical_interview",
    "machine_test",
}


def load_json(path):
    """Load JSON configuration or candidate data."""
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_config(config):
    """Validate role weights, normalization and safeguards."""
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a JSON object.")

    roles = config.get("roles")
    if not isinstance(roles, dict) or not roles:
        raise ValueError("At least one role must be configured.")

    for role, weights in roles.items():
        if not isinstance(weights, dict) or set(weights) != REQUIRED_ROUNDS:
            raise ValueError(
                f"Role '{role}' must define weights for all five rounds."
            )

        for round_name, weight in weights.items():
            if (
                isinstance(weight, bool)
                or not isinstance(weight, (int, float))
                or weight < 0
            ):
                raise ValueError(
                    f"Invalid weight for {role}.{round_name}."
                )

        if sum(weights.values()) != 100:
            raise ValueError(
                f"Weights for '{role}' must add up to 100."
            )

    default_role = config.get("default_role")
    if default_role not in roles:
        raise ValueError("Default role must exist in the roles configuration.")

    normalization = config.get("normalization", {})
    minimum = normalization.get("minimum_score")
    maximum = normalization.get("maximum_score")

    if (
        isinstance(minimum, bool)
        or isinstance(maximum, bool)
        or not isinstance(minimum, (int, float))
        or not isinstance(maximum, (int, float))
        or maximum <= minimum
    ):
        raise ValueError("Invalid normalization range.")

    thresholds = config.get("decision_thresholds", {})
    strong = thresholds.get("strong_fit")
    potential = thresholds.get("potential_fit")

    if not (
        isinstance(strong, (int, float))
        and isinstance(potential, (int, float))
        and 0 <= potential < strong <= 100
    ):
        raise ValueError("Invalid decision thresholds.")

    safeguards = config.get("safeguards", {})
    if safeguards.get("automatic_rejection") is not False:
        raise ValueError("Automatic rejection must remain disabled.")

    if safeguards.get("human_review_required") is not True:
        raise ValueError("Human review must remain enabled.")

    if safeguards.get("missing_round_policy") != "exclude_and_renormalize":
        raise ValueError("Unsupported missing-round policy.")


def normalize_score(score, maximum_score, minimum_score=0):
    """Convert a raw score to the common 0-100 scale."""
    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or isinstance(maximum_score, bool)
        or not isinstance(maximum_score, (int, float))
        or isinstance(minimum_score, bool)
        or not isinstance(minimum_score, (int, float))
    ):
        raise ValueError("Scores and score limits must be numeric.")

    if maximum_score <= minimum_score:
        raise ValueError("Maximum score must exceed minimum score.")

    if score < minimum_score or score > maximum_score:
        raise ValueError("Raw score is outside its permitted range.")

    normalized = (
        (score - minimum_score) / (maximum_score - minimum_score)
    ) * 100

    return round(normalized, 2)


def validate_candidate(candidate, config):
    """Validate the candidate object and completed evaluation records."""
    if not isinstance(candidate, dict):
        raise ValueError("Candidate data must be a JSON object.")

    for key in ("candidate_id", "session_id", "evaluations"):
        if not candidate.get(key):
            raise ValueError(f"Missing required candidate field: {key}")

    if not isinstance(candidate["evaluations"], dict):
        raise ValueError("Evaluations must be a JSON object.")

    role = candidate.get("role", config["default_role"])
    if role not in config["roles"]:
        raise ValueError(f"Unknown role: {role}")

    for round_name, evaluation in candidate["evaluations"].items():
        if round_name not in REQUIRED_ROUNDS:
            raise ValueError(f"Unsupported evaluation round: {round_name}")

        if not isinstance(evaluation, dict):
            raise ValueError(f"{round_name} evaluation must be an object.")

        status = evaluation.get("status")
        if status not in {"completed", "pending", "not_applicable"}:
            raise ValueError(f"Invalid status for {round_name}.")

        if status == "completed":
            if "score" not in evaluation or "maximum_score" not in evaluation:
                raise ValueError(
                    f"{round_name} needs score and maximum_score."
                )

            normalize_score(
                evaluation["score"],
                evaluation["maximum_score"],
            )

        elif "score" in evaluation and evaluation["score"] is not None:
            raise ValueError(
                f"{round_name} must not have a score when status is {status}."
            )

    return candidate


def classify_fit(score, thresholds):
    """Classify the score into a descriptive band, not a hiring decision."""
    if score >= thresholds["strong_fit"]:
        return "STRONG_FIT"
    if score >= thresholds["potential_fit"]:
        return "POTENTIAL_FIT"
    return "NEEDS_REVIEW"


def aggregate_candidate(candidate, config):
    """
    Aggregate completed rounds using configured weights.

    Missing or not-applicable rounds are excluded from the denominator.
    Their absence is reported and never silently treated as a zero score.
    """
    validate_config(config)
    validate_candidate(candidate, config)

    role = candidate.get("role", config["default_role"])
    weights = config["roles"][role]
    evaluations = candidate["evaluations"]

    minimum = config["normalization"]["minimum_score"]
    maximum = config["normalization"]["maximum_score"]

    round_details = {}
    weighted_sum = 0.0
    available_weight = 0.0
    missing_rounds = []
    not_applicable_rounds = []

    for round_name in sorted(REQUIRED_ROUNDS):
        evaluation = evaluations.get(round_name)

        if evaluation is None or evaluation["status"] == "pending":
            missing_rounds.append(round_name)
            round_details[round_name] = {
                "status": "missing" if evaluation is None else "pending",
                "configured_weight_percent": weights[round_name],
                "normalized_score": None,
                "weighted_contribution": None,
                "explanation": "Excluded from score until completed."
            }
            continue

        if evaluation["status"] == "not_applicable":
            not_applicable_rounds.append(round_name)
            round_details[round_name] = {
                "status": "not_applicable",
                "configured_weight_percent": weights[round_name],
                "normalized_score": None,
                "weighted_contribution": None,
                "explanation": "Excluded by the recorded evaluation status."
            }
            continue

        raw_score = evaluation["score"]
        raw_maximum = evaluation["maximum_score"]

        # First convert the raw score to 0-100, then map to the
        # configured common score range.
        percentage = normalize_score(raw_score, raw_maximum, 0)
        normalized = normalize_score(
            percentage,
            100,
            minimum,
        ) if minimum == 0 else round(
            minimum + (percentage / 100) * (maximum - minimum), 2
        )

        # Aggregation uses percentage-normalized values. The configured
        # normalization range is expected to be 0-100 for this model.
        if minimum != 0 or maximum != 100:
            normalized = round(
                ((normalized - minimum) / (maximum - minimum)) * 100, 2
            )

        contribution = normalized * weights[round_name] / 100

        weighted_sum += contribution
        available_weight += weights[round_name]

        round_details[round_name] = {
            "status": "completed",
            "raw_score": raw_score,
            "raw_maximum_score": raw_maximum,
            "normalized_score": normalized,
            "configured_weight_percent": weights[round_name],
            "effective_weight_percent": None,
            "weighted_contribution": round(contribution, 2),
            "explanation": (
                f"{normalized:.2f}/100 normalized score multiplied by "
                f"{weights[round_name]}% configured weight."
            )
        }

    if available_weight == 0:
        hiring_fit_score = None
        effective_weights = {}
        fit_band = "NOT_EVALUATED"
    else:
        hiring_fit_score = round(
            (weighted_sum / available_weight) * 100, 2
        )
        effective_weights = {}

        for round_name, details in round_details.items():
            if details["status"] == "completed":
                effective_weight = (
                    weights[round_name] / available_weight
                ) * 100
                details["effective_weight_percent"] = round(
                    effective_weight, 2
                )
                effective_weights[round_name] = round(
                    effective_weight, 2
                )

        fit_band = classify_fit(
            hiring_fit_score,
            config["decision_thresholds"],
        )

    all_rounds_completed = (
        not missing_rounds and not not_applicable_rounds
    )

    return {
        "candidate_id": candidate["candidate_id"],
        "session_id": candidate["session_id"],
        "target_role": role,
        "scoring_version": "day51-v1",
        "score_status": (
            "COMPLETE" if all_rounds_completed and available_weight > 0
            else "PARTIAL" if available_weight > 0
            else "NOT_EVALUATED"
        ),
        "hiring_fit_score_percent": hiring_fit_score,
        "maximum_score": 100,
        "fit_band": fit_band,
        "configured_role_weights_percent": weights,
        "effective_weights_percent": effective_weights,
        "round_scores": round_details,
        "missing_rounds": missing_rounds,
        "not_applicable_rounds": not_applicable_rounds,
        "available_weight_percent": round(available_weight, 2),
        "transparency": {
            "formula": (
                "Sum(normalized round score * configured round weight) "
                "/ sum(weights for completed rounds)"
            ),
            "missing_round_policy": "exclude_and_renormalize",
            "normalization_scale": "0-100",
            "scores_are_probabilities": False,
            "human_review_required": True,
            "automatic_rejection": False
        },
        "recommendation": (
            "HUMAN_REVIEW_REQUIRED"
            if available_weight > 0
            else "COLLECT_REQUIRED_EVALUATIONS"
        )
    }


def run_aggregation(input_path, config_path, output_path):
    """Load data, aggregate scores and write a unified candidate object."""
    config = load_json(config_path)
    candidate = load_json(input_path)
    report = aggregate_candidate(candidate, config)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("DAY 51 - CROSS-ROUND AGGREGATION ENGINE")
    print("-" * 45)
    print(f"Candidate ID: {report['candidate_id']}")
    print(f"Target role: {report['target_role']}")
    print(f"Score status: {report['score_status']}")

    if report["hiring_fit_score_percent"] is None:
        print("Hiring Fit Score: Not evaluated")
    else:
        print(
            f"Hiring Fit Score: "
            f"{report['hiring_fit_score_percent']:.2f}%"
        )

    print(f"Fit band: {report['fit_band']}")
    print(f"Missing rounds: {report['missing_rounds']}")
    print(f"Human review required: "
          f"{report['transparency']['human_review_required']}")
    print(f"Report saved: {output.resolve()}")

    return report
