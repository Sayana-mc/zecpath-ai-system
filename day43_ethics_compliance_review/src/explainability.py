from typing import Dict


class ExplainabilityGenerator:

    def generate(self, candidate: Dict) -> Dict:

        components = candidate.get("score_components", {})

        reasons = []

        if components.get("skills", 0) >= 70:
            reasons.append("Relevant skills contributed positively to the score.")

        if components.get("experience", 0) >= 70:
            reasons.append("Relevant experience contributed positively to the score.")

        if components.get("communication", 0) >= 70:
            reasons.append("Communication performance contributed positively to the score.")

        if components.get("consistency", 0) >= 70:
            reasons.append("Response consistency contributed positively to the score.")

        if not reasons:
            reasons.append(
                "The candidate requires additional human review."
            )

        return {
            "candidate_id": candidate.get("candidate_id"),
            "final_score": candidate.get("final_score"),
            "decision": candidate.get("decision"),
            "score_components": components,
            "explanation": reasons,
            "human_review_recommended": candidate.get("final_score", 0) < 65
        }