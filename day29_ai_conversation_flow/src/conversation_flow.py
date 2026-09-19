from conversation_state import ConversationState
class ConversationFlow:

    def __init__(self):
        self.state = ConversationState.START
        self.retry_count = 0
        self.max_retries = 2
        self.previous_answers = []

    def start(self):
        self.state = ConversationState.ASKING

        return {
            "state": self.state.value,
            "action": "ask_question",
            "message": "Could you please tell me about your experience?"
        }

    def process_response(self, response):

        if response is None:
            response = ""

        response = response.strip()

        # Silence handling
        if not response:
            self.state = ConversationState.WAITING

            return {
                "state": self.state.value,
                "action": "handle_silence",
                "message": "Take your time. Please answer when you are ready."
            }

        # Confusion handling
        confusion_words = [
            "i don't understand",
            "not understand",
            "what do you mean",
            "can you repeat",
            "confused"
        ]

        if any(word in response.lower() for word in confusion_words):

            self.state = ConversationState.CLARIFICATION

            return {
                "state": self.state.value,
                "action": "clarify",
                "message": (
                    "Sure. Let me explain the question more clearly. "
                    "Could you describe your previous work experience?"
                )
            }

        # Repeated answer detection
        if response.lower() in [
            answer.lower()
            for answer in self.previous_answers
        ]:

            self.retry_count += 1

            if self.retry_count > self.max_retries:
                self.state = ConversationState.FAILED

                return {
                    "state": self.state.value,
                    "action": "polite_failure",
                    "message": (
                        "Thank you. I will record the information "
                        "available and continue with the next question."
                    )
                }

            self.state = ConversationState.RETRY

            return {
                "state": self.state.value,
                "action": "retry_question",
                "message": (
                    "Thank you. Could you provide a little more "
                    "detail about your answer?"
                )
            }

        # Store valid answer
        self.previous_answers.append(response)

        # Follow-up trigger
        if len(response.split()) < 5:

            self.state = ConversationState.FOLLOW_UP

            return {
                "state": self.state.value,
                "action": "follow_up",
                "message": (
                    "Could you please provide a little more detail?"
                )
            }

        # Normal response
        self.state = ConversationState.ASKING

        return {
            "state": self.state.value,
            "action": "continue",
            "message": "Thank you. Let's continue with the next question."
        }

    def complete(self):

        self.state = ConversationState.COMPLETED

        return {
            "state": self.state.value,
            "action": "complete",
            "message": "Thank you for completing the screening."
        }