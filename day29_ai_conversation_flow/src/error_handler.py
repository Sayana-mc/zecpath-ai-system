class ConversationErrorHandler:
    def __init__(self, max_retries=2):
        self.max_retries = max_retries
    def handle_silence(self):
        return {
            "error_type": "silence",
            "action": "retry",
            "message": "I didn't hear a response. Please take your time and answer."
        }
    def handle_confusion(self):
        return {
            "error_type": "confusion",
            "action": "clarify",
            "message": "Let me rephrase the question in a simpler way."
        }
    def handle_repeated_answer(self):
        return {
            "error_type": "repeated_answer",
            "action": "follow_up",
            "message": "Could you provide some additional details?"
        }

    def handle_failure(self):
        return {
            "error_type": "maximum_retries",
            "action": "continue",
            "message": (
                "Thank you. I will record the available information "
                "and continue with the screening."
            )
        }