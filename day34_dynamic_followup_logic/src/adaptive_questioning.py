class AdaptiveQuestioning:

    def __init__(self):
        self.difficulty_levels = {
            "simple": 1,
            "medium": 2,
            "advanced": 3
        }

    def determine_level(self, response, confidence):
        """
        Adapt question difficulty based on response quality
        and confidence.
        """

        if not response or not response.strip():
            return "simple"

        words = len(response.split())

        # High-confidence answers should receive
        # advanced/scenario-based questions.
        if confidence == "high" and words >= 8:
            return "advanced"

        # Detailed normal-confidence responses
        # can move to medium difficulty.
        if confidence == "high" or words >= 8:
            return "medium"

        return "simple"

    def create_question(self, topic, level):

        if level == "simple":
            return (
                f"Can you explain your experience with {topic}?"
            )

        if level == "medium":
            return (
                f"Can you describe how you used {topic} "
                f"in a real situation?"
            )

        return (
            f"Imagine you face a challenging situation involving "
            f"{topic}. How would you analyze the problem and solve it?"
        )