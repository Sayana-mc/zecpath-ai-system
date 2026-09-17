class BehavioralAnalyzer:

    def __init__(
        self,
        confidence_analyzer,
        sentiment_analyzer
    ):
        self.confidence_analyzer = confidence_analyzer
        self.sentiment_analyzer = sentiment_analyzer

    def detect_contradiction(
        self,
        expected_information,
        text
    ):

        text_lower = text.lower()

        if not expected_information:
            return False

        experience_years = expected_information.get(
            "experience_years"
        )

        if experience_years is not None:

            if (
                f"{experience_years} year" in text_lower
                or f"{experience_years} years" in text_lower
            ):
                return False

            return "year" in text_lower

        availability = expected_information.get(
            "availability"
        )

        if availability:
            return (
                availability.lower()
                not in text_lower
                and "join" in text_lower
            )

        return False

    def analyze(self, transcript):

        text = transcript["transcript"]

        duration = transcript.get(
            "duration_seconds",
            0
        )

        expected_information = transcript.get(
            "expected_information",
            {}
        )

        contradiction = self.detect_contradiction(
            expected_information,
            text
        )

        confidence = self.confidence_analyzer.analyze(
            text,
            duration,
            contradiction
        )

        sentiment = self.sentiment_analyzer.analyze(
            text
        )

        communication_strength = self.get_strength(
            confidence["confidence_score"],
            sentiment["sentiment"],
            contradiction
        )

        return {
            "answer_id": transcript["answer_id"],
            "question_id": transcript["question_id"],
            "question": transcript["question"],
            "transcript": text,
            "confidence_analysis": confidence,
            "sentiment_analysis": sentiment,
            "communication_strength": communication_strength
        }

    def get_strength(
        self,
        confidence_score,
        sentiment,
        contradiction
    ):

        if contradiction:
            return "needs_review"

        if confidence_score >= 70:
            if sentiment == "positive":
                return "strong"
            return "good"

        if confidence_score >= 50:
            return "moderate"

        return "needs_review"