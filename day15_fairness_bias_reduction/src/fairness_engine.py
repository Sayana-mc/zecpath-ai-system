import json
from pathlib import Path
from typing import Any, Dict, List

from .normalization import normalize_candidate
from .bias_reduction import (
    mask_personal_attributes,
    reduce_keyword_dependence,
)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load fairness configuration with safe defaults."""

    defaults = {
        "score_min": 0,
        "score_max": 100,
        "keyword_weight_limit": 0.35,
        "semantic_weight": 0.65,
        "bias_gap_warning": 0.20,
        "mask_personal_attributes": True,
        "personal_attributes": [
            "candidate_name",
            "name",
            "email",
            "phone",
            "mobile",
            "address",
            "date_of_birth",
            "dob",
            "gender",
            "age",
            "photo",
            "nationality",
            "religion",
            "marital_status",
        ],
    }

    path = Path(config_path)

    if not path.exists():
        return defaults

    try:
        with open(path, "r", encoding="utf-8") as file:
            config = json.load(file)

        if not isinstance(config, dict):
            return defaults

        defaults.update(config)
        return defaults

    except (OSError, json.JSONDecodeError):
        return defaults


def load_ranking_files(input_dir: str) -> List[Dict[str, Any]]:
    """
    Load Day 14 ranked candidate files.

    Expected files:
        JOB001_ranked_candidates.json
        JOB002_ranked_candidates.json
        ...
    """

    input_path = Path(input_dir)
    candidates: List[Dict[str, Any]] = []

    if not input_path.exists():
        return candidates

    for file_path in sorted(
        input_path.glob("JOB*_ranked_candidates.json")
    ):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

        except (OSError, json.JSONDecodeError):
            continue

        if not isinstance(data, dict):
            continue

        ranked = data.get("ranked_candidates", [])

        if not isinstance(ranked, list):
            continue

        for candidate in ranked:

            if not isinstance(candidate, dict):
                continue

            record = normalize_candidate(candidate)

            # Job-level metadata from the ranking file
            record["job_id"] = data.get(
                "job_id",
                record.get("job_id", "UNKNOWN"),
            )

            record["job_title"] = data.get(
                "job_title",
                record.get("job_title", "Unknown Job"),
            )

            candidates.append(record)

    return candidates


def normalize_score_range(
    scores: List[float],
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> List[float]:
    """
    Apply min-max normalization to a list of scores.

    Formula:

        normalized =
            minimum +
            ((score - low) / (high - low))
            * (maximum - minimum)

    The returned values are always inside the requested range.
    """

    if not scores:
        return []

    try:
        numeric_scores = [float(score) for score in scores]
    except (TypeError, ValueError):
        return [minimum for _ in scores]

    low = min(numeric_scores)
    high = max(numeric_scores)

    # If every score is identical, use the midpoint.
    if high == low:
        midpoint = (minimum + maximum) / 2
        return [
            round(midpoint, 2)
            for _ in numeric_scores
        ]

    normalized: List[float] = []

    for score in numeric_scores:

        value = (
            (score - low)
            / (high - low)
        )

        scaled = (
            minimum
            + value * (maximum - minimum)
        )

        scaled = max(
            minimum,
            min(maximum, scaled),
        )

        normalized.append(
            round(scaled, 2)
        )

    return normalized


def calculate_bias_indicators(
    candidates: List[Dict[str, Any]],
    warning_threshold: float = 0.20,
) -> Dict[str, Any]:
    """
    Calculate score-distribution indicators.

    IMPORTANT:
    These indicators are warning signals only.

    A large score gap does NOT prove discrimination because
    protected-group information is intentionally not used here.
    """

    if not candidates:
        return {
            "candidate_count": 0,
            "average_score": 0.0,
            "minimum_score": 0.0,
            "maximum_score": 0.0,
            "score_gap": 0.0,
            "bias_warning": False,
        }

    scores: List[float] = []

    for candidate in candidates:
        try:
            score = float(
                candidate.get(
                    "fairness_score",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            score = 0.0

        scores.append(
            max(0.0, min(100.0, score))
        )

    minimum = min(scores)
    maximum = max(scores)
    average = sum(scores) / len(scores)

    # Score gap is represented as a proportion of the 0-100 range.
    gap = (maximum - minimum) / 100.0

    return {
        "candidate_count": len(scores),
        "average_score": round(average, 2),
        "minimum_score": round(minimum, 2),
        "maximum_score": round(maximum, 2),
        "score_gap": round(gap, 4),
        "bias_warning": gap > warning_threshold,
    }


def process_candidates(
    candidates: List[Dict[str, Any]],
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Apply Day 15 fairness processing.

    Processing order:

    1. Candidate normalization
    2. Keyword-dependence analysis/reduction
    3. Score normalization
    4. Personal attribute masking
    5. Fairness status assignment

    Personal/protected attributes are NEVER used to calculate
    the fairness score.
    """

    if not candidates:
        return []

    keyword_limit = float(
        config.get(
            "keyword_weight_limit",
            0.35,
        )
    )

    score_min = float(
        config.get(
            "score_min",
            0,
        )
    )

    score_max = float(
        config.get(
            "score_max",
            100,
        )
    )

    personal_attributes = config.get(
        "personal_attributes",
        [],
    )

    # ---------------------------------------------------------
    # STEP 1: Normalize all candidate records
    # ---------------------------------------------------------

    normalized_candidates: List[Dict[str, Any]] = []

    for candidate in candidates:

        if not isinstance(candidate, dict):
            continue

        record = normalize_candidate(candidate)

        # -----------------------------------------------------
        # STEP 2: Reduce keyword dependence
        # -----------------------------------------------------

        record = reduce_keyword_dependence(
            record,
            keyword_limit=keyword_limit,
        )

        normalized_candidates.append(record)

    # ---------------------------------------------------------
    # STEP 3: Normalize fairness scores across the candidate
    #         population for each job.
    # ---------------------------------------------------------

    scores = []

    for record in normalized_candidates:

        try:
            score = float(
                record.get(
                    "fairness_pre_adjusted_score",
                    record.get(
                        "final_ats_score",
                        0.0,
                    ),
                )
            )
        except (TypeError, ValueError):
            score = 0.0

        scores.append(score)

    normalized_scores = normalize_score_range(
        scores,
        minimum=score_min,
        maximum=score_max,
    )

    # ---------------------------------------------------------
    # STEP 4: Assign normalized scores
    # ---------------------------------------------------------

    processed: List[Dict[str, Any]] = []

    for record, normalized_score in zip(
        normalized_candidates,
        normalized_scores,
    ):

        record["fairness_score"] = round(
            normalized_score,
            2,
        )

        # Keep an explicit indicator showing that the
        # score has gone through the Day 15 fairness pipeline.
        record["fairness_status"] = "FAIRNESS_CHECKED"

        # Protected/non-essential attributes are masked AFTER
        # scoring so they cannot influence the score.
        if config.get(
            "mask_personal_attributes",
            True,
        ):
            record = mask_personal_attributes(
                record,
                personal_attributes,
            )

        processed.append(record)

    return processed