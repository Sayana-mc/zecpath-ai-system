class FollowUpEngine:
    """
    Generates adaptive follow-up actions based on candidate responses.
    """

    def __init__(self):
        self.followed_questions = set()

    def detect_response_quality(self, response):
        """
        Detect whether a response is complete, vague, or incomplete.
        """

        if not response or not response.strip():
            return "incomplete"

        text = response.strip().lower()
        words = text.split()

        vague_patterns = [
            "i don't know",
            "not sure",
            "maybe",
            "nothing much",
            "no idea",
            "i cannot say"
        ]

        if any(pattern in text for pattern in vague_patterns):
            return "vague"

        if len(words) <= 3:
            return "incomplete"

        return "complete"

    def generate_followup(
        self,
        question_id,
        question,
        response,
        confidence="normal"
    ):
        """
        Generate a follow-up question based on response quality.
        """

        quality = self.detect_response_quality(response)

        if question_id in self.followed_questions:
            return {
                "trigger": "none",
                "follow_up_question": None,
                "reason": "Question already followed up"
            }

        if quality == "incomplete":
            follow_up = (
                f"Could you please provide a little more detail "
                f"about your answer to: {question}"
            )

            trigger = "clarification"

        elif quality == "vague":
            follow_up = (
                "Could you explain your answer with a specific "
                "example from your experience?"
            )

            trigger = "example_based"

        elif confidence == "high":
            follow_up = (
                "Can you describe a challenging situation related "
                "to this and explain how you handled it?"
            )

            trigger = "scenario_based"

        else:
            follow_up = (
                "Could you explain this further and describe "
                "your approach?"
            )

            trigger = "deepening"

        self.followed_questions.add(question_id)

        return {
            "trigger": trigger,
            "follow_up_question": follow_up,
            "reason": quality
        }