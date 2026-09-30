class HREvaluator:
    """
    Evaluates simulated HR interview responses.

    Scores:
    - Relevance
    - Communication
    - Confidence
    - Consistency
    """

    def _score_relevance(self, answer):
        words = answer.lower().split()

        if len(words) >= 12:
            return 5

        if len(words) >= 6:
            return 4

        if len(words) >= 3:
            return 3

        return 2

    def _score_communication(self, answer):
        words = answer.split()

        if len(words) >= 12:
            return 5

        if len(words) >= 7:
            return 4

        if len(words) >= 4:
            return 3

        return 2

    def _score_confidence(self, answer):
        hesitation_words = [
            "maybe",
            "perhaps",
            "i think",
            "not sure",
            "i don't know",
            "possibly"
        ]

        text = answer.lower()

        hesitation_count = sum(
            1 for word in hesitation_words
            if word in text
        )

        if hesitation_count >= 2:
            return 2

        if hesitation_count == 1:
            return 3

        return 5

    def _score_consistency(self, answer):
        contradiction_words = [
            "but",
            "however",
            "not sure",
            "don't know"
        ]

        text = answer.lower()

        if any(
            phrase in text
            for phrase in contradiction_words
        ):
            return 3

        return 5

    def evaluate_response(self, response):
        answer = response["answer"]

        relevance = self._score_relevance(answer)
        communication = self._score_communication(answer)
        confidence = self._score_confidence(answer)
        consistency = self._score_consistency(answer)

        total = (
            relevance
            + communication
            + confidence
            + consistency
        )

        normalized = round(
            (total / 20) * 100,
            2
        )

        return {
            "question_id": response["question_id"],
            "relevance": relevance,
            "communication": communication,
            "confidence": confidence,
            "consistency": consistency,
            "score": normalized
        }

    def evaluate_session(self, session):
        evaluated = []

        for response in session["responses"]:
            evaluated.append(
                self.evaluate_response(response)
            )

        average_score = round(
            sum(item["score"] for item in evaluated)
            / len(evaluated),
            2
        )

        return {
            "candidate_id": session["candidate_id"],
            "candidate_type": session["candidate_type"],
            "question_scores": evaluated,
            "overall_ai_score": average_score
        }