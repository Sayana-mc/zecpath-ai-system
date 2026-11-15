class BehavioralSignalAnalyzer:

    def detect_contradiction(
        self,
        answer,
        previous_information
    ):
        if not previous_information:
            return {
                "contradiction": False,
                "reason": None
            }

        answer_lower = answer.lower()

        previous_years = previous_information.get(
            "experience_years"
        )

        if previous_years is not None:
            if (
                f"{previous_years} year" in answer_lower
                or f"{previous_years} years" in answer_lower
            ):
                return {
                    "contradiction": False,
                    "reason": None
                }

            if "year" in answer_lower:
                return {
                    "contradiction": True,
                    "reason": "Experience duration differs from previous information."
                }

        return {
            "contradiction": False,
            "reason": None
        }

    def calculate_stress_score(
        self,
        hesitation,
        uncertainty,
        repeated_words,
        sentiment
    ):
        score = 0

        score += hesitation.get(
            "hesitation_count", 0
        ) * 10

        score += hesitation.get(
            "pause_count", 0
        ) * 15

        score += uncertainty.get(
            "count", 0
        ) * 15

        score += repeated_words.get(
            "count", 0
        ) * 10

        if sentiment.get("sentiment") == "negative":
            score += 10

        return max(0, min(100, score))

    def analyze(
        self,
        answer,
        hesitation,
        uncertainty,
        repeated_words,
        sentiment,
        previous_information=None
    ):
        contradiction = self.detect_contradiction(
            answer,
            previous_information
        )

        stress_score = self.calculate_stress_score(
            hesitation,
            uncertainty,
            repeated_words,
            sentiment
        )

        return {
            "stress_score": stress_score,
            "contradiction": contradiction
        }