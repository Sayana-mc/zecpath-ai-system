from typing import Dict, List


class FairnessReviewer:

    def __init__(self, config: Dict):
        self.threshold = config["fairness"]["score_difference_threshold"]

    def review_scores(self, candidates: List[Dict]) -> Dict:

        scores = [
            candidate["final_score"]
            for candidate in candidates
            if isinstance(candidate.get("final_score"), (int, float))
        ]

        if not scores:
            return {
                "status": "REVIEW_REQUIRED",
                "candidate_count": 0,
                "score_range": None,
                "notes": ["No valid candidate scores available."]
            }

        minimum = min(scores)
        maximum = max(scores)
        difference = maximum - minimum

        notes = [
            "Review scoring consistency across candidates.",
            "Do not use demographic attributes as scoring features.",
            "Human review should remain available for uncertain decisions."
        ]

        if difference > self.threshold:
            status = "REVIEW_REQUIRED"
            notes.append(
                "Large score variation detected; inspect scoring inputs and evidence."
            )
        else:
            status = "NO_IMMEDIATE_ANOMALY"

        return {
            "status": status,
            "candidate_count": len(scores),
            "minimum_score": minimum,
            "maximum_score": maximum,
            "score_difference": round(difference, 2),
            "notes": notes
        }