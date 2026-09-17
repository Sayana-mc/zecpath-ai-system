class SentimentAnalyzer:

    def __init__(self, config):
        sentiment_config = config["sentiment"]

        self.positive_words = sentiment_config["positive_words"]
        self.negative_words = sentiment_config["negative_words"]

    def analyze(self, text):

        text_lower = text.lower()

        positive_matches = []
        negative_matches = []

        words = text_lower.split()

        for word in words:

            clean_word = word.strip(
                ".,!?;:"
            )

            if clean_word in self.positive_words:
                positive_matches.append(clean_word)

            if clean_word in self.negative_words:
                negative_matches.append(clean_word)

        positive_count = len(positive_matches)
        negative_count = len(negative_matches)

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        total = positive_count + negative_count

        if total == 0:
            sentiment_score = 0
        else:
            sentiment_score = (
                (positive_count - negative_count)
                / total
            ) * 100

        return {
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 2),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_indicators": positive_matches,
            "negative_indicators": negative_matches
        }