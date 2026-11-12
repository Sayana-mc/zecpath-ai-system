"""Screening scoring integration for the root application."""

import json
import uuid
from typing import Any

from day26_screening_scoring_engine.src.scoring_engine import ScreeningScoringEngine
from day26_screening_scoring_engine.src.question_scorer import QuestionScorer

try:
    from . import database
except ImportError:
    from src import database
from .schemas import (
    ScreeningQuestionScoreCreate,
    ScreeningQuestionScoreResponse,
    ScreeningAggregateScoreResponse,
)


class ScreeningScoringIntegration:
    """Wrapper for screening scoring engine with database persistence."""

    def __init__(self):
        scoring_config = {
            "parameters": {
                "clarity": {"weight": 0.20},
                "relevance": {"weight": 0.35},
                "completeness": {"weight": 0.25},
                "consistency": {"weight": 0.20},
            },
            "score_range": {"minimum": 0, "maximum": 5},
        }
        self.engine = ScreeningScoringEngine(scoring_config)
        self.question_scorer = QuestionScorer(scoring_config)

    @property
    def scorer(self):
        return self

    def score_answer(
        self,
        question_text: str,
        answer_text: str,
        expected_intent: str,
        extracted_data: dict[str, Any] | None = None,
    ) -> Any:
        intent = expected_intent.lower()
        if intent == "skill_experience":
            intent = "skills"
        result = self.question_scorer.calculate_score(
            answer=answer_text,
            expected_intent=intent,
            previous_information=extracted_data or {},
        )
        class ScoreWrapper:
            def __init__(self, res):
                self.clarity = res["parameter_scores"]["clarity"]
                self.relevance = res["parameter_scores"]["relevance"]
                self.completeness = res["parameter_scores"]["completeness"]
                self.consistency = res["parameter_scores"]["consistency"]
                self.weighted_score = res["weighted_score"]
                self.normalized_score = res["normalized_score"]
                self.explanation = "Scored based on clarity, relevance, completeness, consistency."
        return ScoreWrapper(result)

    def score_question(
        self,
        session_id: str,
        answer_id: str,
        question_id: str,
        question_text: str,
        answer_text: str,
        expected_intent: str,
        previous_information: dict[str, Any] | None = None,
    ) -> ScreeningQuestionScoreResponse:
        """Score a single question answer."""
        if previous_information is None:
            previous_information = {}

        result = self.question_scorer.calculate_score(
            answer=answer_text,
            expected_intent=expected_intent,
            previous_information=previous_information,
        )

        explanation = self._generate_explanation(
            result["parameter_scores"],
            expected_intent,
        )

        score_id = str(uuid.uuid4())
        score = ScreeningQuestionScoreCreate(
            answer_id=answer_id,
            question_id=question_id,
            clarity_score=result["parameter_scores"]["clarity"],
            relevance_score=result["parameter_scores"]["relevance"],
            completeness_score=result["parameter_scores"]["completeness"],
            consistency_score=result["parameter_scores"]["consistency"],
            weighted_score=result["weighted_score"],
            normalized_score=result["normalized_score"],
            explanation=explanation,
            human_review_required=self._needs_human_review(result["parameter_scores"]),
            scoring_version="screening-v1",
        )

        score_data = score.model_dump()
        score_data["score_id"] = score_id
        saved = database.save_screening_question_score(session_id, score_data)
        return ScreeningQuestionScoreResponse(**saved)

    def score_session(
        self,
        session_id: str,
        candidate_id: str,
    ) -> ScreeningAggregateScoreResponse:
        """Score all answers in a session and create aggregate score."""
        answers = database.list_screening_answers(session_id)
        if not answers:
            raise ValueError("No answers found for session")

        scores = database.list_screening_question_scores(session_id)
        if not scores:
            raise ValueError("No question scores found for session")

        overall_score = sum(s["normalized_score"] for s in scores) / len(scores)
        questions_evaluated = len(scores)
        questions_answered = sum(1 for a in answers if a["answer_status"] != "MISSING")
        questions_missing = sum(1 for a in answers if a["answer_status"] == "MISSING")
        human_review_required = any(s.get("human_review_required") for s in scores)

        aggregate_id = str(uuid.uuid4())
        aggregate = {
            "aggregate_id": aggregate_id,
            "session_id": session_id,
            "candidate_id": candidate_id,
            "overall_score": round(overall_score, 2),
            "score_status": "REVIEW_REQUIRED" if human_review_required else "PROVISIONAL",
            "questions_evaluated": questions_evaluated,
            "questions_answered": questions_answered,
            "questions_missing": questions_missing,
            "human_review_required": human_review_required,
            "scoring_version": "screening-v1",
        }

        saved = database.save_screening_aggregate_score(aggregate)
        return ScreeningAggregateScoreResponse(**saved)

    def get_aggregate_score(self, session_id: str) -> ScreeningAggregateScoreResponse | None:
        """Get latest aggregate score for session."""
        score = database.get_screening_aggregate_score(session_id)
        if not score:
            return None
        return ScreeningAggregateScoreResponse(**score)

    def list_question_scores(self, session_id: str) -> list[ScreeningQuestionScoreResponse]:
        """List all question scores for a session."""
        scores = database.list_screening_question_scores(session_id)
        return [ScreeningQuestionScoreResponse(**s) for s in scores]

    def _generate_explanation(
        self,
        parameter_scores: dict[str, int],
        expected_intent: str,
    ) -> str:
        """Generate human-readable explanation for scores."""
        explanations = []

        if parameter_scores["clarity"] >= 4:
            explanations.append("The answer is clearly expressed.")
        elif parameter_scores["clarity"] <= 2:
            explanations.append("The answer provides limited detail or clarity.")

        if parameter_scores["relevance"] >= 4:
            explanations.append("The answer is relevant to the expected topic.")
        elif parameter_scores["relevance"] <= 2:
            explanations.append("The answer does not directly address the expected topic.")

        if parameter_scores["completeness"] >= 4:
            explanations.append("The answer contains sufficient information.")
        elif parameter_scores["completeness"] <= 2:
            explanations.append("The answer contains limited information.")

        if parameter_scores["consistency"] >= 4:
            explanations.append("The answer is consistent with available candidate information.")
        elif parameter_scores["consistency"] <= 2:
            explanations.append("The answer may be inconsistent with available candidate information.")

        if not explanations:
            explanations.append("The answer received moderate scores across evaluation parameters.")

        return " ".join(explanations)

    def _needs_human_review(self, parameter_scores: dict[str, int]) -> bool:
        """Determine if human review is needed based on scores."""
        return any(score <= 2 for score in parameter_scores.values())


screening_scoring_integration = ScreeningScoringIntegration()