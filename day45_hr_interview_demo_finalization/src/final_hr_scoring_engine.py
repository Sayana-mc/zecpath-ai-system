class FinalHRScoringEngine:
    """
    Final HR interview scoring engine.

    Scores:
    - Relevance
    - Communication
    - Confidence
    - Consistency
    """

    def calculate_question_score(
        self,
        relevance,
        communication,
        confidence,
        consistency
    ):
        values = [
            relevance,
            communication,
            confidence,
            consistency
        ]

        values = [
            max(0.0, min(100.0, float(value)))
            for value in values
        ]

        score = sum(values) / len(values)

        return {
            "relevance": values[0],
            "communication": values[1],
            "confidence": values[2],
            "consistency": values[3],
            "overall_score": round(score, 2)
        }

    def calculate_candidate_score(self, question_scores):
        if not question_scores:
            return 0.0

        total = sum(
            item["overall_score"]
            for item in question_scores
        )

        return round(total / len(question_scores), 2)