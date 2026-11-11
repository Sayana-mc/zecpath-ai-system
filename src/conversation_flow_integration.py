"""Conversation flow integration for the root application."""

import uuid
from typing import Any

from day29_ai_conversation_flow.src.conversation_flow import ConversationFlow
from day29_ai_conversation_flow.src.conversation_state import ConversationState
from day29_ai_conversation_flow.src.decision_tree import ConversationDecisionTree
from day29_ai_conversation_flow.src.error_handler import ConversationErrorHandler as ErrorHandler

from src import database
from .schemas import (
    ScreeningSessionCreate,
    ScreeningSessionResponse,
    ScreeningSessionStatusUpdate,
)


class ConversationFlowIntegration:
    """Wrapper for conversation flow management with session persistence."""

    def __init__(self):
        self.flows: dict[str, ConversationFlow] = {}
        self.decision_tree = ConversationDecisionTree()
        self.error_handler = ErrorHandler()

    def create_session(
        self,
        candidate_id: str,
        opening_id: str,
        language: str = "en",
        source: str = "MANUAL",
    ) -> ScreeningSessionResponse:
        """Create new screening session with conversation flow."""
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "candidate_id": candidate_id,
            "opening_id": opening_id,
            "language": language,
            "source": source,
        }
        saved = database.create_screening_session(session_data)
        self.flows[session_id] = ConversationFlow()
        return ScreeningSessionResponse(**saved)

    def start_session(self, session_id: str) -> dict[str, Any]:
        """Start the conversation flow for a session."""
        session = database.get_screening_session(session_id)
        if not session:
            raise ValueError("Session not found")

        flow = self.flows.get(session_id) or ConversationFlow()
        self.flows[session_id] = flow

        result = flow.start()
        database.update_screening_session_status(session_id, "IN_PROGRESS")
        return result

    def process_response(
        self,
        session_id: str,
        response: str,
        question_id: str | None = None,
    ) -> dict[str, Any]:
        """Process candidate response through conversation flow."""
        session = database.get_screening_session(session_id)
        if not session:
            raise ValueError("Session not found")

        flow = self.flows.get(session_id)
        if not flow:
            flow = ConversationFlow()
            self.flows[session_id] = flow

        result = flow.process_response(response)

        if result["action"] in {"continue", "ask_question"}:
            database.update_screening_session_status(session_id, "IN_PROGRESS")
        elif result["action"] == "handle_silence":
            pass  # Keep IN_PROGRESS
        elif result["action"] == "clarify":
            pass  # Keep IN_PROGRESS
        elif result["action"] in {"retry_question", "follow_up"}:
            pass  # Keep IN_PROGRESS
        elif result["action"] == "complete":
            database.update_screening_session_status(session_id, "COMPLETED")
        elif result["action"] == "polite_failure":
            database.update_screening_session_status(session_id, "COMPLETED")

        return result

    def get_next_question(
        self,
        session_id: str,
        questions: list[dict[str, Any]],
        answered_question_ids: list[str],
    ) -> dict[str, Any] | None:
        """Get next question in conversation flow."""
        for question in questions:
            if question["question_id"] not in answered_question_ids:
                return question
        return None

    def handle_error(
        self,
        session_id: str,
        error_type: str,
        error_message: str,
    ) -> dict[str, Any]:
        """Handle conversation error with recovery strategy."""
        return self.error_handler.handle_error(
            error_type,
            error_message,
            self.flows.get(session_id, ConversationFlow()).state.value,
        )

    def pause_session(self, session_id: str) -> None:
        """Pause conversation flow."""
        database.update_screening_session_status(session_id, "INTERRUPTED")

    def resume_session(self, session_id: str) -> None:
        """Resume conversation flow."""
        database.update_screening_session_status(session_id, "IN_PROGRESS")

    def cancel_session(self, session_id: str) -> None:
        """Cancel conversation flow."""
        database.update_screening_session_status(session_id, "CANCELLED")
        self.flows.pop(session_id, None)

    def get_session_state(self, session_id: str) -> str | None:
        """Get current conversation state."""
        flow = self.flows.get(session_id)
        if flow:
            return flow.state.value
        session = database.get_screening_session(session_id)
        return session["status"] if session else None


conversation_flow_integration = ConversationFlowIntegration()