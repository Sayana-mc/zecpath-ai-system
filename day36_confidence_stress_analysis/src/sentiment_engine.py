class SentimentEngine:
    """
    Simple rule-based sentiment scoring engine.

    Produces:
    - Positive indicators
    - Negative indicators
    - Neutral sentiment
    - Sentiment score
    """

    POSITIVE_WORDS = [
        "confident",
        "success",
        "successful",
        "achieved",
        "improved",
        "completed",
        "enjoy",
        "love",
        "excellent",
        "strong",
        "good",
        "positive"
    ]

    NEGATIVE_WORDS = [
        "difficult",
        "problem",
        "failed",
        "failure",
        "worried",
        "stress",
        "stressed",
        "confused",
        "weak",
        "bad",
        "negative",
        "afraid"
    ]

    def analyze(self, answer):
        if not answer or not answer.strip():
            return {
                "sentiment": "neutral",
                "score": 50,
                "positive_count": 0,
                "negative_count": 0
            }

        words = answer.lower().split()

        positive_count = sum(
            1 for word in words
            if word.strip(".,!?") in self.POSITIVE_WORDS
        )

        negative_count = sum(
            1 for word in words
            if word.strip(".,!?") in self.NEGATIVE_WORDS
        )

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        score = 50 + (
            positive_count * 10
        ) - (
            negative_count * 10
        )

        score = max(0, min(100, score))

        return {
            "sentiment": sentiment,
            "score": score,
            "positive_count": positive_count,
            "negative_count": negative_count
        }