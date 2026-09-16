from question_scorer import QuestionScorer


class ScreeningScoringEngine:

    def __init__(self, scoring_config):
        self.question_scorer = QuestionScorer(
            scoring_config
        )

    def score_question(self, question_data):

        answer = question_data.get("answer", "")
        expected_intent = question_data.get(
            "expected_intent",
            "unknown"
        )

        previous_information = question_data.get(
            "previous_information",
            {}
        )

        result = self.question_scorer.calculate_score(
            answer=answer,
            expected_intent=expected_intent,
            previous_information=previous_information
        )

        explanation = self._generate_explanation(
            result["parameter_scores"],
            expected_intent
        )

        return {
            "answer_id": question_data["answer_id"],
            "candidate_id": question_data["candidate_id"],
            "question_id": question_data["question_id"],
            "question": question_data["question"],
            "answer": answer,
            "intent": expected_intent,
            "parameter_scores": result["parameter_scores"],
            "weighted_score": result["weighted_score"],
            "normalized_score": result["normalized_score"],
            "explanation": explanation
        }

    def score_candidate(self, candidate_answers):

        if not candidate_answers:
            return {
                "candidate_id": None,
                "total_screening_score": 0,
                "questions_evaluated": 0,
                "question_scores": []
            }

        question_scores = []

        for answer in candidate_answers:
            result = self.score_question(answer)
            question_scores.append(result)

        total_score = sum(
            item["normalized_score"]
            for item in question_scores
        ) / len(question_scores)

        candidate_id = candidate_answers[0]["candidate_id"]

        return {
            "candidate_id": candidate_id,
            "questions_evaluated": len(question_scores),
            "total_screening_score": round(
                total_score,
                2
            ),
            "question_scores": question_scores
        }

    def _generate_explanation(
        self,
        parameter_scores,
        expected_intent
    ):

        explanations = []

        if parameter_scores["clarity"] >= 4:
            explanations.append(
                "The answer is clearly expressed."
            )
        elif parameter_scores["clarity"] <= 2:
            explanations.append(
                "The answer provides limited detail or clarity."
            )

        if parameter_scores["relevance"] >= 4:
            explanations.append(
                "The answer is relevant to the expected topic."
            )
        elif parameter_scores["relevance"] <= 2:
            explanations.append(
                "The answer does not directly address the expected topic."
            )

        if parameter_scores["completeness"] >= 4:
            explanations.append(
                "The answer contains sufficient information."
            )
        elif parameter_scores["completeness"] <= 2:
            explanations.append(
                "The answer contains limited information."
            )

        if parameter_scores["consistency"] >= 4:
            explanations.append(
                "The answer is consistent with the available candidate information."
            )
        elif parameter_scores["consistency"] <= 2:
            explanations.append(
                "The answer may be inconsistent with the available candidate information."
            )

        if not explanations:
            explanations.append(
                "The answer received moderate scores across the evaluation parameters."
            )

        return explanations