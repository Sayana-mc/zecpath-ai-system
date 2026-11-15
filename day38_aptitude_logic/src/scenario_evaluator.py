class ScenarioEvaluator:
    """
    Evaluates situational judgment answers.

    Evaluation dimensions:
    - Decision making
    - Communication
    - Problem solving
    """

    def __init__(self):

        self.expected_indicators = {
            "decision_making": [
                "assess",
                "identify",
                "prioritize",
                "decide"
            ],
            "communication": [
                "communicate",
                "inform",
                "team",
                "manager"
            ],
            "problem_solving": [
                "solve",
                "fix",
                "analyze",
                "alternative",
                "escalate"
            ]
        }

    def evaluate(self, answer):

        if not answer or not answer.strip():

            return {
                "decision_making": 0,
                "communication": 0,
                "problem_solving": 0,
                "overall_score": 0
            }

        text = answer.lower()

        scores = {}

        for category, indicators in self.expected_indicators.items():

            matches = sum(
                1
                for indicator in indicators
                if indicator in text
            )

            if matches >= 2:
                score = 5
            elif matches == 1:
                score = 3
            else:
                score = 1

            scores[category] = score

        overall_score = round(
            (
                scores["decision_making"]
                + scores["communication"]
                + scores["problem_solving"]
            ) / 15 * 100,
            2
        )

        scores["overall_score"] = overall_score

        return scores