"""Answer understanding integration for the root application."""

import json
import uuid
from typing import Any

from day25_answer_intent_engine.src.answer_understanding_engine import AnswerUnderstandingEngine
from day25_answer_intent_engine.src.intent_classifier import IntentClassifier
from day25_answer_intent_engine.src.information_extractor import extract_information
from day25_answer_intent_engine.src.answer_validator import validate_answer

try:
    from . import database
except ImportError:
    from src import database
from .schemas import (
    ScreeningAnswerCreate,
    ScreeningAnswerResponse,
)


class AnswerUnderstandingIntegration:
    """Wrapper for answer understanding engine with database persistence."""

    def __init__(self):
        self.engine = AnswerUnderstandingEngine()
        self.classifier = IntentClassifier()

    def understand_answer(
        self,
        session_id: str,
        transcript_id: str | None,
        question_id: str,
        question_text: str,
        expected_intent: str,
        raw_answer: str,
        cleaned_answer: str,
    ) -> ScreeningAnswerResponse:
        """Process candidate answer through understanding engine."""
        understanding = self.engine.understand(
            cleaned_answer,
            expected_intent=expected_intent,
        )

        detected_intent = understanding["intent"]
        intent_confidence = understanding["intent_confidence"]
        answer_status = understanding["answer_status"]
        validation = understanding["validation"]
        extracted_info = understanding["extracted_information"]

        needs_clarification = (
            validation.get("needs_clarification", False)
            or validation.get("vague", False)
            or validation.get("missing", False)
        )
        is_off_topic = (
            validation.get("is_off_topic", False)
            or validation.get("off_topic", False)
        )

        answer_id = str(uuid.uuid4())
        answer = ScreeningAnswerCreate(
            transcript_id=transcript_id,
            question_id=question_id,
            question_text=question_text,
            expected_intent=expected_intent,
            detected_intent=detected_intent,
            answer_status=answer_status.upper(),
            raw_answer=raw_answer,
            cleaned_answer=cleaned_answer,
            extracted_information=extracted_info,
            intent_confidence=intent_confidence,
            needs_clarification=needs_clarification,
            is_off_topic=is_off_topic,
        )

        answer_data = answer.model_dump()
        answer_data["answer_id"] = answer_id
        saved = database.save_screening_answer(session_id, answer_data)
        return ScreeningAnswerResponse(**saved)

    def get_answer(self, answer_id: str) -> ScreeningAnswerResponse | None:
        """Get answer by ID."""
        answer = database.get_screening_answer(answer_id)
        if not answer:
            return None
        if isinstance(answer["extracted_information"], str):
            answer["extracted_information"] = json.loads(answer["extracted_information"])
        return ScreeningAnswerResponse(**answer)

    def list_session_answers(self, session_id: str) -> list[ScreeningAnswerResponse]:
        """List all answers for a session."""
        answers = database.list_screening_answers(session_id)
        results = []
        for answer in answers:
            answer["extracted_information"] = json.loads(answer["extracted_information"])
            results.append(ScreeningAnswerResponse(**answer))
        return results


answer_understanding_integration = AnswerUnderstandingIntegration()