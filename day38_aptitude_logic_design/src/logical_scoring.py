class LogicalReasoningScorer:
    """
    Scores logical thinking and problem-solving clarity.
    Score range: 0-100.
    """

    def __init__(self):
        self.weights = {
            "logic": 40,
            "clarity": 30,
            "problem_solving": 30
        }

    def score_logic(self, answer):

        if not answer or not answer.strip():
            return 0

        text = answer.lower()

        logic_words = [
            "because",
            "therefore",
            "first",
            "then",
            "so",
            "reason",
            "calculate",
            "step"
        ]

        matches = sum(
            1 for word in logic_words
            if word in text
        )

        if matches >= 3:
            return 5

        if matches >= 1:
            return 4

        return 2

    def score_clarity(self, answer):

        if not answer or not answer.strip():
            return 0

        words = answer.split()

        if len(words) <= 3:
            return 2

        if len(words) <= 10:
            return 3

        if len(words) <= 30:
            return 5

        return 4

    def score_problem_solving(self, answer):

        if not answer or not answer.strip():
            return 0

        text = answer.lower()

        solution_words = [
            "identify",
            "analyze",
            "solve",
            "check",
            "fix",
            "test",
            "communicate",
            "escalate",
            "alternative"
        ]

        matches = sum(
            1 for word in solution_words
            if word in text
        )

        if matches >= 3:
            return 5

        if matches >= 1:
            return 4

        return 2

    def calculate_score(self, answer):

        logic = self.score_logic(answer)
        clarity = self.score_clarity(answer)
        problem_solving = self.score_problem_solving(answer)

        parameter_scores = {
            "logic": logic,
            "clarity": clarity,
            "problem_solving": problem_solving
        }

        weighted_score = (
            logic * self.weights["logic"] +
            clarity * self.weights["clarity"] +
            problem_solving * self.weights["problem_solving"]
        )

        normalized_score = (
            weighted_score / 5
        )

        return {
            "parameter_scores": parameter_scores,
            "weighted_score": weighted_score,
            "normalized_score": round(normalized_score, 2)
        }