class RecommendationEngine:

    def get_recommendation(self, final_score):
        if final_score >= 80:
            return {
                "recommendation": "HIGH_FIT",
                "reason": "Strong overall candidate score."
            }

        if final_score >= 65:
            return {
                "recommendation": "MODERATE_FIT",
                "reason": "Candidate meets a reasonable level but requires review."
            }

        if final_score >= 50:
            return {
                "recommendation": "LOW_FIT",
                "reason": "Candidate shows limited overall suitability."
            }

        return {
            "recommendation": "NOT_RECOMMENDED",
            "reason": "Overall score is below the minimum recommendation threshold."
        }