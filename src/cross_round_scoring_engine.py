"""Day 41 & 51 Unified Cross-Round Aggregation & Scoring Engine with Day 42 Anomaly Detection."""

import uuid
from typing import Any, Mapping

try:
    from . import database
except ImportError:
    from src import database


ROLE_ROUND_WEIGHTS: dict[str, dict[str, float]] = {
    "software_engineer": {
        "ats": 10.0,
        "screening": 10.0,
        "hr_interview": 10.0,
        "technical_interview": 30.0,
        "machine_test": 40.0,
    },
    "python_developer": {
        "ats": 10.0,
        "screening": 10.0,
        "hr_interview": 10.0,
        "technical_interview": 30.0,
        "machine_test": 40.0,
    },
    "data_scientist": {
        "ats": 10.0,
        "screening": 15.0,
        "hr_interview": 15.0,
        "technical_interview": 25.0,
        "machine_test": 35.0,
    },
    "data_analyst": {
        "ats": 15.0,
        "screening": 20.0,
        "hr_interview": 15.0,
        "technical_interview": 25.0,
        "machine_test": 25.0,
    },
    "mern_developer": {
        "ats": 15.0,
        "screening": 15.0,
        "hr_interview": 20.0,
        "technical_interview": 25.0,
        "machine_test": 25.0,
    },
    "devops_engineer": {
        "ats": 10.0,
        "screening": 15.0,
        "hr_interview": 15.0,
        "technical_interview": 35.0,
        "machine_test": 25.0,
    },
    "default": {
        "ats": 20.0,
        "screening": 20.0,
        "hr_interview": 20.0,
        "technical_interview": 20.0,
        "machine_test": 20.0,
    },
}


class CrossRoundScoringEngine:
    """Unified cross-round aggregation engine fulfilling both Day 41 and Day 51 specifications."""

    def __init__(self, role_weights: dict[str, dict[str, float]] | None = None):
        self.role_weights = role_weights or ROLE_ROUND_WEIGHTS

    def get_role_weights(self, role: str) -> dict[str, float]:
        clean_role = role.lower().strip().replace(" ", "_")
        return self.role_weights.get(clean_role, self.role_weights["default"])

    @staticmethod
    def normalize_score(raw_score: float, max_score: float = 100.0, min_score: float = 0.0) -> float:
        """Converts raw score to a normalized 0-100 scale with validation."""
        if max_score <= min_score:
            raise ValueError("Maximum score must exceed minimum score.")
        if raw_score < min_score or raw_score > max_score:
            raise ValueError(f"Raw score {raw_score} is outside range [{min_score}, {max_score}].")
        normalized = ((raw_score - min_score) / (max_score - min_score)) * 100.0
        return round(normalized, 2)

    def detect_anomalies(self, round_scores: Mapping[str, float | None]) -> list[str]:
        """Day 42 Anomaly Detection: flags unusual score discrepancies or outliers across rounds."""
        anomalies = []
        completed = {k: v for k, v in round_scores.items() if v is not None}

        # Check bounds
        for r_name, score in completed.items():
            if score < 0.0 or score > 100.0:
                anomalies.append(f"Score for {r_name} ({score}) is outside standard bounds [0, 100].")

        # Check extreme discrepancy between practical and resume
        if "ats" in completed and "technical_interview" in completed:
            diff = abs(completed["ats"] - completed["technical_interview"])
            if diff >= 45.0:
                anomalies.append(
                    f"Discrepancy: Substantial divergence ({diff:.1f} pts) between resume ATS ({completed['ats']}) "
                    f"and Technical Interview ({completed['technical_interview']})."
                )

        if "technical_interview" in completed and "machine_test" in completed:
            t_diff = abs(completed["technical_interview"] - completed["machine_test"])
            if t_diff >= 40.0:
                anomalies.append(
                    f"Discrepancy: Noticeable divergence ({t_diff:.1f} pts) between Technical Interview and Machine Test."
                )

        return anomalies

    def calculate_hiring_fit(
        self,
        candidate_id: str,
        target_role: str,
        round_scores: Mapping[str, float | None],
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Calculates unified hiring fit % with exclude_and_renormalize policy for missing rounds."""
        weights = self.get_role_weights(target_role)

        # Filter completed rounds
        completed_rounds = {k: v for k, v in round_scores.items() if v is not None and k in weights}
        anomalies = self.detect_anomalies(round_scores)

        if not completed_rounds:
            return {
                "candidate_id": candidate_id,
                "target_role": target_role,
                "hiring_fit_score": 0.0,
                "fit_category": "NOT_RECOMMENDED",
                "completed_rounds_count": 0,
                "total_rounds_expected": len(weights),
                "round_breakdown": {},
                "anomalies": anomalies,
                "status": "NO_COMPLETED_ROUNDS",
            }

        # Renormalize weights for completed rounds
        completed_weight_sum = sum(weights[r] for r in completed_rounds)
        if completed_weight_sum <= 0:
            completed_weight_sum = 100.0

        renormalized_weights: dict[str, float] = {}
        weighted_sum = 0.0

        for r_name, score in completed_rounds.items():
            r_weight = (weights[r_name] / completed_weight_sum) * 100.0
            renormalized_weights[r_name] = round(r_weight, 2)
            weighted_sum += (score * (r_weight / 100.0))

        hiring_fit = round(weighted_sum, 2)

        # Categorization
        if hiring_fit >= 80.0:
            fit_category = "STRONG_FIT"
        elif hiring_fit >= 60.0:
            fit_category = "POTENTIAL_FIT"
        elif hiring_fit >= 50.0:
            fit_category = "LOW_FIT"
        else:
            fit_category = "NOT_RECOMMENDED"

        eval_id = f"AGG_{uuid.uuid4().hex[:8].upper()}"
        sess_id = session_id or f"SESS_{uuid.uuid4().hex[:6]}"

        record = {
            "evaluation_id": eval_id,
            "candidate_id": candidate_id,
            "session_id": sess_id,
            "target_role": target_role,
            "ats_score": round_scores.get("ats"),
            "screening_score": round_scores.get("screening"),
            "hr_interview_score": round_scores.get("hr_interview"),
            "technical_interview_score": round_scores.get("technical_interview"),
            "machine_test_score": round_scores.get("machine_test"),
            "hiring_fit_score": hiring_fit,
            "fit_category": fit_category,
            "weights_used": renormalized_weights,
            "round_breakdown": completed_rounds,
            "completed_rounds_count": len(completed_rounds),
            "anomalies_detected": anomalies,
        }
        try:
            saved = database.save_cross_round_evaluation(record)
            if isinstance(saved, dict) and "completed_rounds_count" not in saved:
                saved["completed_rounds_count"] = len(completed_rounds)
            return saved
        except Exception:
            return record

    def calculate_unified_fit(
        self,
        round_scores: Mapping[str, Any],
        target_role: str = "software_engineer",
        candidate_id: str = "default_cand",
        role_weights: dict[str, float] | None = None,
        missing_strategy: str = "exclude_and_renormalize",
    ) -> dict[str, Any]:
        """Convenience wrapper for unified 5-round fitting with validation."""
        for k, v in round_scores.items():
            if v is not None and not (0.0 <= float(v) <= 100.0):
                raise ValueError(f"Score for round {k} is out of range 0-100: {v}")

        res = self.calculate_hiring_fit(
            candidate_id=candidate_id,
            target_role=target_role,
            round_scores=round_scores,
        )
        weights = role_weights or self.get_role_weights(target_role)
        missing_rounds = [k for k in weights if k not in round_scores or round_scores[k] is None]
        raw_weights = res.get("weights_used", {})
        total_w = sum(raw_weights.values()) or 1.0
        effective_fractions = {k: round(v / total_w, 4) for k, v in raw_weights.items()}
        completed_count = res.get("completed_rounds_count")
        if completed_count is None:
            completed_count = len([k for k, v in round_scores.items() if v is not None and k in weights])

        return {
            "hiring_fit_percentage": res["hiring_fit_score"],
            "completed_rounds_count": completed_count,
            "missing_rounds": missing_rounds,
            "effective_weights": effective_fractions,
            "anomalies": res.get("anomalies_detected", res.get("anomalies", [])),
            "raw_result": res,
        }


cross_round_scoring_engine = CrossRoundScoringEngine()


def calculate_cross_round_score(
    candidate_id: str,
    opening_id: str,
    target_role: str,
    round_scores: Mapping[str, float | None],
    save_to_db: bool = True,
) -> dict[str, Any]:
    engine = CrossRoundScoringEngine()
    res = engine.calculate_unified_fit(
        round_scores=round_scores,
        target_role=target_role,
        candidate_id=candidate_id,
    )
    fit_score = res.get("hiring_fit_percentage", 0.0)
    if save_to_db:
        database.save_cross_round_evaluation(
            candidate_id=candidate_id,
            opening_id=opening_id,
            target_role=target_role,
            hiring_fit_percentage=fit_score,
            round_scores=round_scores,
            effective_weights=res.get("effective_weights", {}),
            completed_rounds=res.get("completed_rounds_count", len(round_scores)),
            missing_rounds=res.get("missing_rounds", []),
            anomalies=res.get("anomalies", []),
        )
    return res
