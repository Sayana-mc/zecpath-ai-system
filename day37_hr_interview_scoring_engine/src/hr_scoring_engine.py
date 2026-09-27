class HRInterviewScoringEngine:
    """
    HR Interview Scoring Engine

    Evaluates:
    - Answer relevance
    - Communication
    - Confidence
    - Consistency

    Produces an explainable normalized HR interview score.
    """

    def __init__(self, config):
        self.config = config

        self.weights = config["weights"]

        self.minimum_score = config["score_range"]["minimum"]
        self.maximum_score = config["score_range"]["maximum"]

    def calculate_weighted_score(
        self,
        relevance,
        communication,
        confidence,
        consistency
    ):
        """
        Calculate weighted HR interview score.
        """

        scores = {
            "answer_relevance": relevance,
            "communication": communication,
            "confidence": confidence,
            "consistency": consistency
        }

        weighted_score = 0

        for parameter, score in scores.items():
            weight = self.weights[parameter]
            weighted_score += score * weight

        return round(weighted_score, 2)

    def normalize_score(self, weighted_score):
        """
        Normalize weighted score to 0-100.
        """

        score_range = (
            self.maximum_score - self.minimum_score
        )

        if score_range == 0:
            return 0

        normalized = (
            (weighted_score - self.minimum_score)
            / score_range
        ) * 100

        return round(
            max(0, min(100, normalized)),
            2
        )

    def generate_breakdown(
        self,
        relevance,
        communication,
        confidence,
        consistency
    ):
        """
        Generate explainable scoring breakdown.
        """

        scores = {
            "answer_relevance": relevance,
            "communication": communication,
            "confidence": confidence,
            "consistency": consistency
        }

        breakdown = {}

        for parameter, score in scores.items():
            weight = self.weights[parameter]

            contribution = score * weight

            breakdown[parameter] = {
                "raw_score": score,
                "weight": weight,
                "weighted_contribution": round(
                    contribution,
                    2
                )
            }

        return breakdown

    def calculate_candidate_score(
        self,
        responses,
        relevance,
        communication,
        confidence,
        consistency
    ):
        """
        Calculate complete candidate HR interview score.

        responses:
            Number of interview responses/questions.
        """

        if responses <= 0:
            responses = 1

        weighted_score = self.calculate_weighted_score(
            relevance,
            communication,
            confidence,
            consistency
        )

        normalized_score = self.normalize_score(
            weighted_score
        )

        breakdown = self.generate_breakdown(
            relevance,
            communication,
            confidence,
            consistency
        )

        return {
            "questions_evaluated": responses,
            "parameter_scores": {
                "answer_relevance": relevance,
                "communication": communication,
                "confidence": confidence,
                "consistency": consistency
            },
            "weighted_score": weighted_score,
            "normalized_score": normalized_score,
            "explainable_breakdown": breakdown
        }