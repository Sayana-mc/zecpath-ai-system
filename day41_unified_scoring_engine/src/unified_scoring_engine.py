import json
from pathlib import Path


class UnifiedScoringEngine:

    def __init__(self, config_path):
        self.config_path = Path(config_path)

        with open(
            self.config_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.weights = json.load(file)

    def get_weights(self, role):
        role_key = role.lower().strip()

        if role_key in self.weights:
            selected = self.weights[role_key]
        else:
            selected = self.weights["default"]

        self._validate_weights(selected)

        return selected

    def _validate_weights(self, weights):

        total = sum(weights.values())

        if abs(total - 1.0) > 0.001:
            raise ValueError(
                "Scoring weights must total 1.0"
            )

    def calculate_hiring_fit(
        self,
        ats_score,
        screening_score,
        hr_interview_score,
        role
    ):

        weights = self.get_weights(role)

        weighted_ats = (
            ats_score * weights["ats"]
        )

        weighted_screening = (
            screening_score * weights["screening"]
        )

        weighted_hr = (
            hr_interview_score
            * weights["hr_interview"]
        )

        hiring_fit = (
            weighted_ats
            + weighted_screening
            + weighted_hr
        )

        return round(hiring_fit, 2)

    def get_recommendation(self, hiring_fit):

        if hiring_fit >= 80:
            return "HIGH_FIT"

        if hiring_fit >= 65:
            return "MODERATE_FIT"

        if hiring_fit >= 50:
            return "LOW_FIT"

        return "NOT_RECOMMENDED"

    def evaluate_candidate(self, candidate):

        ats_score = float(
            candidate["ats_score"]
        )

        screening_score = float(
            candidate["screening_score"]
        )

        hr_score = float(
            candidate["hr_interview_score"]
        )

        role = candidate["role"]

        weights = self.get_weights(role)

        hiring_fit = self.calculate_hiring_fit(
            ats_score,
            screening_score,
            hr_score,
            role
        )

        recommendation = self.get_recommendation(
            hiring_fit
        )

        return {
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["candidate_name"],
            "role": role,

            "round_scores": {
                "ats_score": ats_score,
                "screening_score": screening_score,
                "hr_interview_score": hr_score
            },

            "weights": {
                "ats": weights["ats"],
                "screening": weights["screening"],
                "hr_interview": weights["hr_interview"]
            },

            "weighted_contribution": {
                "ats": round(
                    ats_score * weights["ats"],
                    2
                ),
                "screening": round(
                    screening_score * weights["screening"],
                    2
                ),
                "hr_interview": round(
                    hr_score * weights["hr_interview"],
                    2
                )
            },

            "hiring_fit_percentage": hiring_fit,

            "recommendation": recommendation
        }