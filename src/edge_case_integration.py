"""Edge case handling integration for the root application."""

import uuid
from typing import Any

from day31_edge_case_failure_handling.src.edge_case_handler import EdgeCaseHandler
from day31_edge_case_failure_handling.src.retry_manager import RetryManager
from day31_edge_case_failure_handling.src.clarification_manager import ClarificationManager

from src import database
from .schemas import (
    ScreeningAnswerResponse,
)


class EdgeCaseIntegration:
    """Wrapper for edge case handling with database persistence."""

    def __init__(self):
        self.edge_handler = EdgeCaseHandler()
        self.retry_manager = RetryManager()
        self.clarification_manager = ClarificationManager()

    def handle_audio_failure(
        self,
        audio_id: str,
        error_type: str,
        error_message: str,
    ) -> dict[str, Any]:
        """Handle audio processing failure."""
        audio = database.get_screening_audio(audio_id)
        if not audio:
            raise ValueError("Audio not found")

        database.update_screening_audio_status(audio_id, "FAILED")

        return self.edge_handler.handle_audio_error(
            audio_id,
            error_type,
            error_message,
        )

    def handle_transcript_failure(
        self,
        transcript_id: str,
        error_type: str,
        error_message: str,
    ) -> dict[str, Any]:
        """Handle transcript processing failure."""
        return self.edge_handler.handle_transcript_error(
            transcript_id,
            error_type,
            error_message,
        )

    def handle_empty_transcript(self) -> dict[str, Any]:
        """Handle empty or missing transcript."""
        return {
            "action": "PROMPT_AGAIN",
            "message": "I didn't receive an answer. Could you please answer the question?",
            "status": "RETRY_REQUESTED",
        }

    def handle_low_confidence(self) -> dict[str, Any]:
        """Handle low STT confidence."""
        return {
            "action": "CLARIFY",
            "message": "I'm sorry, I couldn't hear that clearly. Could you please repeat your answer?",
            "status": "CLARIFICATION_REQUESTED",
        }

    def handle_missing_answer(
        self,
        session_id: str,
        question_id: str,
        question_text: str,
        is_mandatory: bool,
    ) -> dict[str, Any]:
        """Handle missing or empty candidate answer."""
        return self.edge_handler.handle_missing_answer(
            session_id,
            question_id,
            question_text,
            is_mandatory,
        )

    def handle_partial_answer(
        self,
        answer_id: str,
        text: str,
        expected_intent: str,
    ) -> dict[str, Any]:
        """Handle incomplete/partial candidate answer."""
        answer = database.get_screening_answer(answer_id)
        if not answer:
            raise ValueError("Answer not found")

        return self.edge_handler.handle_partial_answer(
            answer_id,
            text,
            expected_intent,
        )

    def handle_language_mixing(
        self,
        transcript_id: str,
        detected_languages: list[str],
        confidence_scores: list[float],
    ) -> dict[str, Any]:
        """Handle mixed-language transcript."""
        return self.edge_handler.handle_language_mixing(
            transcript_id,
            detected_languages,
            confidence_scores,
        )

    def get_retry_decision(
        self,
        session_id: str,
        question_id: str,
        attempt_count: int,
        error_type: str,
    ) -> dict[str, Any]:
        """Get retry decision for failed processing."""
        return self.retry_manager.get_retry_decision(
            session_id,
            question_id,
            attempt_count,
            error_type,
        )

    def record_retry_attempt(
        self,
        session_id: str,
        question_id: str,
        attempt_count: int,
        success: bool,
    ) -> None:
        """Record retry attempt outcome."""
        self.retry_manager.record_attempt(
            session_id,
            question_id,
            attempt_count,
            success,
        )

    def request_clarification(
        self,
        session_id: str,
        answer_id: str,
        clarification_type: str,
        question_text: str,
        candidate_answer: str,
    ) -> dict[str, Any]:
        """Generate clarification request for unclear answer."""
        clarification_id = str(uuid.uuid4())
        return self.clarification_manager.create_clarification(
            clarification_id,
            session_id,
            answer_id,
            clarification_type,
            question_text,
            candidate_answer,
        )

    def resolve_clarification(
        self,
        clarification_id: str,
        resolved_answer: str,
    ) -> dict[str, Any]:
        """Resolve clarification with new answer."""
        return self.clarification_manager.resolve_clarification(
            clarification_id,
            resolved_answer,
        )


edge_case_integration = EdgeCaseIntegration()