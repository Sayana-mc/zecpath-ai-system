class ConversationDecisionTree:

    def decide(self, response):

        if response is None or not response.strip():

            return {
                "condition": "silence",
                "next_action": "retry"
            }

        text = response.lower()

        confusion_words = [
            "i don't understand",
            "what do you mean",
            "can you repeat",
            "confused"
        ]

        if any(word in text for word in confusion_words):

            return {
                "condition": "confusion",
                "next_action": "clarification"
            }

        if len(response.split()) < 5:

            return {
                "condition": "short_answer",
                "next_action": "follow_up"
            }

        return {
            "condition": "valid_answer",
            "next_action": "continue"
        }