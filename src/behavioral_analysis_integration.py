"""Behavioral analysis integration for the root application."""

import uuid
from typing import Any

from day27_confidence_sentiment_analysis.src.sentiment_analyzer import SentimentAnalyzer
from day27_confidence_sentiment_analysis.src.confidence_analyzer import ConfidenceAnalyzer
from day27_confidence_sentiment_analysis.src.behavioral_analyzer import BehavioralAnalyzer

from src import database
from .schemas import (
    BehavioralAnalysisCreate,
    BehavioralAnalysisResponse,
)


class BehavioralAnalysisIntegration:
    """Wrapper for behavioral analysis with database persistence."""

    def __init__(self):
        config = {
            "sentiment": {
                "positive_words": [
                    "excellent", "great", "good", "strong", "confident", "experienced",
                    "skilled", "proficient", "expert", "passionate", "motivated",
                    "eager", "excited", "interested", "enthusiastic", "positive"
                ],
                "negative_words": [
                    "poor", "weak", "bad", "difficult", "struggle", "unfamiliar",
                    "inexperienced", "limited", "none", "never", "cannot", "unable",
                    "worried", "concerned", "uncertain", "unsure", "negative"
                ],
            },
            "confidence": {
                "base_score": 50,
                "hesitation_penalty": 5,
                "uncertainty_penalty": 10,
                "contradiction_penalty": 15,
                "clear_response_bonus": 10,
                "minimum_score": 0,
                "maximum_score": 100,
            },
            "patterns": {
                "hesitation_words": [
                    "um", "uh", "er", "ah", "like", "you know", "i mean",
                    "sort of", "kind of", "basically", "actually"
                ],
                "uncertainty_phrases": [
                    "i think", "i guess", "maybe", "perhaps", "not sure",
                    "i don't know", "i'm not certain", "could be", "might be",
                    "possibly", "probably"
                ],
            },
            "response_length": {
                "short_word_limit": 10,
                "medium_word_limit": 50,
            },
            "pace": {
                "fast_wpm": 160,
                "slow_wpm": 80,
            },
        }
        self.sentiment_analyzer = SentimentAnalyzer(config)
        self.confidence_analyzer = ConfidenceAnalyzer(config)
        self.behavioral_analyzer = BehavioralAnalyzer(
            confidence_analyzer=self.confidence_analyzer,
            sentiment_analyzer=self.sentiment_analyzer,
        )

    def analyze_answer(
        self,
        session_id: str,
        answer_id: str,
        text: str,
        duration_seconds: float | None = None,
        previous_answers: list[dict[str, Any]] | None = None,
    ) -> BehavioralAnalysisResponse:
        """Analyze candidate answer for behavioral signals."""
        if previous_answers is None:
            previous_answers = []

        sentiment_result = self.sentiment_analyzer.analyze(text)
        confidence_result = self.confidence_analyzer.analyze(
            text,
            duration_seconds or 0,
            contradiction=False,
        )

        contradiction = self.behavioral_analyzer.detect_contradiction(
            previous_answers,
            text,
        )

        analysis_id = str(uuid.uuid4())
        analysis = BehavioralAnalysisCreate(
            answer_id=answer_id,
            sentiment=sentiment_result["sentiment"].upper(),
            sentiment_score=sentiment_result["sentiment_score"],
            confidence_score=confidence_result["confidence_score"],
            hesitation_count=confidence_result["hesitation"]["count"],
            uncertainty_count=confidence_result["uncertainty"]["count"],
            contradiction_detected=bool(contradiction),
            contradiction_details=json.dumps({"detected": True}) if contradiction else None,
            response_length_category=(
                confidence_result["response_length"]["category"].upper()
                if confidence_result["response_length"].get("category")
                else "MEDIUM"
            ),
            words_per_minute=confidence_result["pace"]["words_per_minute"],
            pace_category=(
                confidence_result["pace"]["pace"].upper()
                if confidence_result["pace"].get("pace")
                else "UNKNOWN"
            ),
            processing_version="behavioral-v1",
        )

        analysis_data = analysis.model_dump()
        analysis_data["analysis_id"] = analysis_id
        saved = database.save_behavioral_analysis(session_id, analysis_data)
        return BehavioralAnalysisResponse(**saved)

    def analyze_text(self, text: str, duration_seconds: float = 0.0) -> dict[str, Any]:
        """Analyze standalone text without database persistence."""
        sentiment_result = self.sentiment_analyzer.analyze(text)
        confidence_result = self.confidence_analyzer.analyze(
            text,
            duration_seconds,
            contradiction=False,
        )
        return {
            "sentiment": sentiment_result["sentiment"].upper(),
            "sentiment_score": sentiment_result["sentiment_score"],
            "confidence_score": confidence_result["confidence_score"],
            "hesitation_count": confidence_result["hesitation"]["count"],
            "uncertainty_count": confidence_result["uncertainty"]["count"],
            "words_per_minute": confidence_result["pace"]["words_per_minute"],
            "pace_category": confidence_result["pace"]["pace"],
            "response_length_category": confidence_result["response_length"]["category"],
        }

    def get_session_analysis(self, session_id: str) -> list[BehavioralAnalysisResponse]:
        """Get all behavioral analyses for a session."""
        analyses = database.get_behavioral_analysis(session_id)
        return [BehavioralAnalysisResponse(**a) for a in analyses]

    def get_session_summary(self, session_id: str) -> dict[str, Any]:
        """Get aggregate behavioral summary for session."""
        analyses = self.get_session_analysis(session_id)
        if not analyses:
            return {}

        total_hesitation = sum(a.hesitation_count for a in analyses)
        total_uncertainty = sum(a.uncertainty_count for a in analyses)
        contradictions = sum(1 for a in analyses if a.contradiction_detected)
        sentiments = [a.sentiment for a in analyses if a.sentiment]
        avg_confidence = sum(a.confidence_score or 0 for a in analyses) / len(analyses)

        return {
            "total_hesitation_count": total_hesitation,
            "total_uncertainty_count": total_uncertainty,
            "contradictions_detected": contradictions,
            "sentiment_distribution": {
                s: sentiments.count(s) for s in set(sentiments)
            },
            "average_confidence_score": round(avg_confidence, 2),
        }


behavioral_analysis_integration = BehavioralAnalysisIntegration()