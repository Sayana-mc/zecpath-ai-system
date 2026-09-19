class RetryManager:
    """
    Controls retry attempts for failed or unclear answers.
    """

    def __init__(self, max_retries=2):
        self.max_retries = max_retries

    def should_retry(self, retry_count):
        return retry_count < self.max_retries

    def get_action(self, retry_count):
        if self.should_retry(retry_count):
            return {
                "action": "retry",
                "retry_count": retry_count + 1,
                "message": "Could you please repeat your answer?"
            }

        return {
            "action": "fallback",
            "retry_count": retry_count,
            "message": (
                "Thank you. We will record this answer and "
                "continue with the next question."
            )
        }