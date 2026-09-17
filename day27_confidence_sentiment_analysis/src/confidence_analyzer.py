import re


class ConfidenceAnalyzer:

    def __init__(self, config):
        self.config = config

        confidence_config = config["confidence"]

        self.base_score = confidence_config["base_score"]
        self.hesitation_penalty = confidence_config["hesitation_penalty"]
        self.uncertainty_penalty = confidence_config["uncertainty_penalty"]
        self.contradiction_penalty = confidence_config["contradiction_penalty"]
        self.clear_response_bonus = confidence_config["clear_response_bonus"]

        self.min_score = confidence_config["minimum_score"]
        self.max_score = confidence_config["maximum_score"]

        self.hesitation_words = config["patterns"]["hesitation_words"]
        self.uncertainty_phrases = config["patterns"]["uncertainty_phrases"]

    def detect_hesitation(self, text):
        text_lower = text.lower()

        matches = []

        for word in self.hesitation_words:
            pattern = r"\b" + re.escape(word) + r"\b"

            if re.search(pattern, text_lower):
                matches.append(word)

        return {
            "detected": len(matches) > 0,
            "count": len(matches),
            "patterns": matches
        }

    def detect_uncertainty(self, text):
        text_lower = text.lower()

        matches = []

        for phrase in self.uncertainty_phrases:
            if phrase in text_lower:
                matches.append(phrase)

        return {
            "detected": len(matches) > 0,
            "count": len(matches),
            "patterns": matches
        }

    def calculate_response_length(self, text):
        words = text.split()
        word_count = len(words)

        if word_count <= self.config["response_length"]["short_word_limit"]:
            category = "short"
        elif word_count <= self.config["response_length"]["medium_word_limit"]:
            category = "medium"
        else:
            category = "long"

        return {
            "word_count": word_count,
            "category": category
        }

    def calculate_pace(self, text, duration_seconds):
        if duration_seconds <= 0:
            return {
                "words_per_minute": 0,
                "pace": "unknown"
            }

        word_count = len(text.split())

        words_per_minute = (
            word_count / duration_seconds
        ) * 60

        fast_limit = self.config["pace"]["fast_wpm"]
        slow_limit = self.config["pace"]["slow_wpm"]

        if words_per_minute > fast_limit:
            pace = "fast"
        elif words_per_minute < slow_limit:
            pace = "slow"
        else:
            pace = "normal"

        return {
            "words_per_minute": round(words_per_minute, 2),
            "pace": pace
        }

    def calculate_confidence_score(
        self,
        hesitation,
        uncertainty,
        contradiction,
        response_length
    ):

        score = self.base_score

        if hesitation["detected"]:
            score -= self.hesitation_penalty

        if uncertainty["detected"]:
            score -= self.uncertainty_penalty

        if contradiction:
            score -= self.contradiction_penalty

        if (
            not hesitation["detected"]
            and not uncertainty["detected"]
            and response_length["word_count"] > 5
        ):
            score += self.clear_response_bonus

        score = max(
            self.min_score,
            min(self.max_score, score)
        )

        return round(score, 2)

    def analyze(
        self,
        text,
        duration_seconds,
        contradiction=False
    ):

        hesitation = self.detect_hesitation(text)
        uncertainty = self.detect_uncertainty(text)

        response_length = self.calculate_response_length(text)

        pace = self.calculate_pace(
            text,
            duration_seconds
        )

        confidence_score = self.calculate_confidence_score(
            hesitation,
            uncertainty,
            contradiction,
            response_length
        )

        return {
            "confidence_score": confidence_score,
            "hesitation": hesitation,
            "uncertainty": uncertainty,
            "response_length": response_length,
            "pace": pace,
            "contradiction_detected": contradiction
        }