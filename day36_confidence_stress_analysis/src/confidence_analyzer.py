import re


class ConfidenceAnalyzer:
    """
    Analyzes candidate responses for confidence-related indicators.

    Indicators:
    - Hesitation phrases
    - Repeated words
    - Uncertainty phrases
    - Long-pause markers
    """

    HESITATION_PHRASES = [
        "um",
        "uh",
        "hmm",
        "actually",
        "well",
        "let me think"
    ]

    UNCERTAINTY_PHRASES = [
        "i think",
        "maybe",
        "perhaps",
        "probably",
        "i am not sure",
        "not sure",
        "i guess",
        "might be",
        "i don't know"
    ]

    PAUSE_MARKERS = [
        "...",
        "[pause]",
        "[long pause]",
        "<pause>"
    ]

    def detect_hesitation(self, answer):
        text = answer.lower()

        hesitation_count = sum(
            text.count(phrase)
            for phrase in self.HESITATION_PHRASES
        )

        pause_count = sum(
            text.count(marker)
            for marker in self.PAUSE_MARKERS
        )

        return {
            "hesitation_count": hesitation_count,
            "pause_count": pause_count,
            "detected": (
                hesitation_count > 0
                or pause_count > 0
            )
        }

    def detect_repeated_words(self, answer):
        words = re.findall(
            r"\b[a-zA-Z]+\b",
            answer.lower()
        )

        repeated = []

        for index in range(len(words) - 1):
            if words[index] == words[index + 1]:
                repeated.append(words[index])

        return {
            "repeated_words": repeated,
            "count": len(repeated)
        }

    def detect_uncertainty(self, answer):
        text = answer.lower()

        detected = [
            phrase
            for phrase in self.UNCERTAINTY_PHRASES
            if phrase in text
        ]

        return {
            "phrases": detected,
            "count": len(detected),
            "detected": len(detected) > 0
        }

    def calculate_confidence_score(self, answer):
        if not answer or not answer.strip():
            return 0

        hesitation = self.detect_hesitation(answer)
        repeated = self.detect_repeated_words(answer)
        uncertainty = self.detect_uncertainty(answer)

        score = 100

        score -= hesitation["hesitation_count"] * 5
        score -= hesitation["pause_count"] * 10
        score -= repeated["count"] * 5
        score -= uncertainty["count"] * 10

        return max(0, min(100, score))

    def analyze(self, answer):
        return {
            "confidence_score": self.calculate_confidence_score(answer),
            "hesitation": self.detect_hesitation(answer),
            "repeated_words": self.detect_repeated_words(answer),
            "uncertainty": self.detect_uncertainty(answer)
        }