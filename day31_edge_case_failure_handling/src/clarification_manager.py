class ClarificationManager:
    """
    Generates polite clarification messages
    for unclear or incomplete answers.
    """

    def clarify(self, case_type):

        messages = {
            "missing_answer":
                "I didn't receive an answer. Could you please answer the question?",

            "incomplete_answer":
                "Could you please provide a little more detail?",

            "language_mixing":
                "Could you please answer clearly in one language?",

            "poor_audio":
                "I couldn't hear that clearly. Could you please repeat your answer?",

            "background_noise":
                "There seems to be some background noise. Could you please repeat your answer?"
        }

        return {
            "action": "clarify",
            "message": messages.get(
                case_type,
                "Could you please clarify your answer?"
            )
        }