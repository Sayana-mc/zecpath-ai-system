import re


class CommunicationScorer:
    """
    Evaluates candidate communication using:

    - Fluency
    - Grammar quality
    - Vocabulary range
    - Clarity
    - Filler words
    - Answer structure

    Final score: 0-100
    """

    FILLER_WORDS = {
        "um",
        "uh",
        "like",
        "actually",
        "basically",
        "you know",
        "sort of",
        "kind of"
    }

    def __init__(self):
        self.weights = {
            "fluency": 20,
            "grammar": 20,
            "vocabulary": 15,
            "clarity": 20,
            "structure": 15,
            "filler_control": 10
        }

    def word_count(self, answer):
        return len(answer.split())

    def sentence_count(self, answer):
        sentences = re.split(r"[.!?]+", answer.strip())
        return len([s for s in sentences if s.strip()])

    def calculate_fluency(self, answer):
        words = self.word_count(answer)

        if words == 0:
            return 0

        if words < 5:
            return 8

        if words < 10:
            return 12

        if words < 20:
            return 16

        return 20

    def calculate_grammar(self, answer):
        if not answer.strip():
            return 0

        score = 20

        common_errors = [
            "i am have",
            "he have",
            "she have",
            "they is",
            "i has",
            "we was",
            "he go",
            "she go"
        ]

        text = answer.lower()

        for error in common_errors:
            if error in text:
                score -= 3

        return max(score, 0)

    def calculate_vocabulary(self, answer):
        words = re.findall(r"\b[a-zA-Z]+\b", answer.lower())

        if not words:
            return 0

        unique_words = set(words)
        diversity = len(unique_words) / len(words)

        if diversity >= 0.8:
            return 15

        if diversity >= 0.6:
            return 12

        if diversity >= 0.4:
            return 9

        return 6

    def calculate_clarity(self, answer):
        if not answer.strip():
            return 0

        words = self.word_count(answer)
        sentences = self.sentence_count(answer)

        if words <= 3:
            return 7

        if sentences >= 2 and words >= 10:
            return 20

        if words >= 8:
            return 16

        return 12

    def detect_fillers(self, answer):
        text = answer.lower()
        detected = []

        for filler in self.FILLER_WORDS:
            pattern = r"\b" + re.escape(filler) + r"\b"

            if re.search(pattern, text):
                detected.append(filler)

        return detected

    def calculate_filler_control(self, answer):
        fillers = self.detect_fillers(answer)

        if not answer.strip():
            return 0

        if len(fillers) == 0:
            return 10

        if len(fillers) == 1:
            return 8

        if len(fillers) == 2:
            return 6

        return 4

    def calculate_structure(self, answer):
        words = self.word_count(answer)
        sentences = self.sentence_count(answer)

        if words == 0:
            return 0

        if words >= 15 and sentences >= 2:
            return 15

        if words >= 8:
            return 12

        if words >= 4:
            return 9

        return 5

    def evaluate(self, answer):

        scores = {
            "fluency": self.calculate_fluency(answer),
            "grammar": self.calculate_grammar(answer),
            "vocabulary": self.calculate_vocabulary(answer),
            "clarity": self.calculate_clarity(answer),
            "structure": self.calculate_structure(answer),
            "filler_control": self.calculate_filler_control(answer)
        }

        total = sum(scores.values())

        return {
            "parameter_scores": scores,
            "communication_score": round(total, 2),
            "score_range": "0-100",
            "filler_words": self.detect_fillers(answer),
            "word_count": self.word_count(answer),
            "sentence_count": self.sentence_count(answer)
        }