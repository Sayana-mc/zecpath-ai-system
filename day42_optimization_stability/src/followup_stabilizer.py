class FollowUpStabilizer:

    def __init__(
        self,
        max_followups=2,
        duplicate_threshold=0.80
    ):
        self.max_followups = max_followups
        self.duplicate_threshold = duplicate_threshold

    def should_follow_up(
        self,
        response,
        previous_followups
    ):

        response = (
            response or ""
        ).strip()

        if not response:
            return True

        if len(response.split()) < 3:
            return True

        if len(previous_followups) >= self.max_followups:
            return False

        return True

    def select_followup(
        self,
        response,
        previous_followups
    ):

        if not self.should_follow_up(
            response,
            previous_followups
        ):
            return None

        response_length = len(
            response.split()
        )

        if response_length < 5:

            followup = (
                "Could you provide a little more detail?"
            )

        elif response_length < 12:

            followup = (
                "Could you give an example?"
            )

        else:

            followup = (
                "What was your specific contribution?"
            )

        if followup in previous_followups:
            return None

        return followup

    def stabilize_history(
        self,
        followups
    ):

        unique = []

        for question in followups:

            if question not in unique:
                unique.append(question)

        return unique[
            :self.max_followups
        ]