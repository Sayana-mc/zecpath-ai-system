class ScoreAnomalyDetector:

    def __init__(
        self,
        difference_threshold=40
    ):
        self.difference_threshold = (
            difference_threshold
        )

    def analyze(self, scores):

        if not scores:
            return {
                "anomaly_detected": False,
                "reason": "No scores available"
            }

        values = [
            float(score)
            for score in scores
        ]

        highest = max(values)
        lowest = min(values)

        difference = highest - lowest

        if difference > self.difference_threshold:

            return {
                "anomaly_detected": True,
                "reason": (
                    "Large difference between "
                    "component scores"
                ),
                "difference": round(
                    difference,
                    2
                )
            }

        return {
            "anomaly_detected": False,
            "reason": "Scores within expected range",
            "difference": round(
                difference,
                2
            )
        }