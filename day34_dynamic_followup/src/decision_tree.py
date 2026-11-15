class FollowUpDecisionTree:

    def decide(
        self,
        response_quality,
        confidence,
        repeated=False
    ):
        """
        Decide the next conversation action.
        """

        if repeated:
            return {
                "action": "move_forward",
                "reason": "Avoid repetitive questioning"
            }

        if response_quality == "incomplete":
            return {
                "action": "clarification",
                "reason": "Candidate response is incomplete"
            }

        if response_quality == "vague":
            return {
                "action": "example_based",
                "reason": "Candidate response is vague"
            }

        if confidence == "high":
            return {
                "action": "scenario_based",
                "reason": "Candidate gave a confident response"
            }

        return {
            "action": "deepening",
            "reason": "Additional detail can be explored"
        }