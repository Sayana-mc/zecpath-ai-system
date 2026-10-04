class RefinedScoringEngine:

    def __init__(
        self,
        min_score=0,
        max_score=100,
        anomaly_difference_threshold=40,
        default_score=50
    ):
        self.min_score = min_score
        self.max_score = max_score
        self.anomaly_difference_threshold = (
            anomaly_difference_threshold
        )
        self.default_score = default_score

    def validate_score(self, score):

        if score is None:
            return self.default_score

        try:
            score = float(score)
        except (TypeError, ValueError):
            return self.default_score

        score = max(
            self.min_score,
            min(self.max_score, score)
        )

        return round(score, 2)

    def detect_anomaly(
        self,
        scores
    ):

        valid_scores = [
            self.validate_score(score)
            for score in scores
        ]

        if not valid_scores:
            return False

        highest = max(valid_scores)
        lowest = min(valid_scores)

        difference = highest - lowest

        return (
            difference
            > self.anomaly_difference_threshold
        )

    def calculate_refined_score(
        self,
        relevance,
        communication,
        confidence,
        consistency
    ):

        scores = [
            self.validate_score(relevance),
            self.validate_score(communication),
            self.validate_score(confidence),
            self.validate_score(consistency)
        ]

        anomaly = self.detect_anomaly(scores)

        refined_score = sum(scores) / len(scores)

        return {
            "component_scores": {
                "relevance": scores[0],
                "communication": scores[1],
                "confidence": scores[2],
                "consistency": scores[3]
            },
            "refined_score": round(
                refined_score,
                2
            ),
            "anomaly_detected": anomaly
        }