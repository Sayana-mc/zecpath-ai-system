"""Complete screening pipeline integration for the root application."""

import uuid
from typing import Any

from . import database
from .stt_integration import stt_integration
from .answer_understanding_integration import answer_understanding_integration
from .screening_scoring_integration import screening_scoring_integration
from .behavioral_analysis_integration import behavioral_analysis_integration
from .screening_report_integration import screening_report_integration
from .conversation_flow_integration import conversation_flow_integration
from .edge_case_integration import edge_case_integration
from .screening_questions import get_questions, load_dataset


class ScreeningPipeline:
    """Complete end-to-end screening pipeline."""

    def __init__(self):
        self.dataset = load_dataset()

    def create_screening_session(
        self,
        candidate_id: str,
        opening_id: str,
        language: str = "en",
        role_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a new screening session with questions."""
        candidate = database.get_candidate(candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        if candidate["opening_id"] != opening_id:
            raise ValueError("Candidate does not belong to this opening")

        questions = get_questions(role_id=role_id, language=language, active_only=True)
        if not questions:
            questions = get_questions(language=language, active_only=True)

        session = conversation_flow_integration.create_session(
            candidate_id=candidate_id,
            opening_id=opening_id,
            language=language,
        )

        return {
            "session": session,
            "questions": questions,
            "next_question": questions[0] if questions else None,
        }

    def process_audio_response(
        self,
        session_id: str,
        audio_bytes: bytes,
        filename: str,
        mime_type: str,
        question_id: str | None = None,
    ) -> dict[str, Any]:
        """Process audio response through complete pipeline."""
        session = database.get_screening_session(session_id)
        if not session:
            raise ValueError("Session not found")

        audio_upload = stt_integration.upload_audio(
            session_id=session_id,
            file_bytes=audio_bytes,
            filename=filename,
            mime_type=mime_type,
            question_id=question_id,
        )

        transcript = stt_integration.process_audio(audio_upload.audio_id)

        question = self._get_question(question_id) if question_id else None
        if not question:
            return {
                "transcript": transcript,
                "error": "Question ID required for answer processing",
            }

        answer = answer_understanding_integration.understand_answer(
            session_id=session_id,
            transcript_id=transcript.transcript_id,
            question_id=question["question_id"],
            question_text=question["question_text"],
            expected_intent=self._map_category_to_intent(question["category"]),
            raw_answer=transcript.raw_text,
            cleaned_answer=transcript.cleaned_text,
        )

        score = screening_scoring_integration.score_question(
            session_id=session_id,
            answer_id=answer.answer_id,
            question_id=question["question_id"],
            question_text=question["question_text"],
            answer_text=answer.cleaned_answer,
            expected_intent=self._map_category_to_intent(question["category"]),
        )

        behavioral = behavioral_analysis_integration.analyze_answer(
            session_id=session_id,
            answer_id=answer.answer_id,
            text=answer.cleaned_answer,
            duration_seconds=0,
        )

        return {
            "transcript": transcript,
            "answer": answer,
            "score": score,
            "behavioral": behavioral,
            "next_question": self.get_next_question(session_id),
        }

    def process_text_response(
        self,
        session_id: str,
        question_id: str,
        text_answer: str,
    ) -> dict[str, Any]:
        """Process text response through complete pipeline."""
        session = database.get_screening_session(session_id)
        if not session:
            raise ValueError("Session not found")

        question = self._get_question(question_id)
        if not question:
            raise ValueError("Question not found")

        transcript_id = str(uuid.uuid4())
        transcript = database.save_screening_transcript(session_id, {
            "transcript_id": transcript_id,
            "session_id": session_id,
            "audio_id": None,
            "question_id": question_id,
            "raw_text": text_answer,
            "cleaned_text": text_answer,
            "language": session["language"],
            "language_probability": 1.0,
            "partial_answer": False,
            "processing_version": "text-v1",
            "segment_count": 0,
        })

        answer = answer_understanding_integration.understand_answer(
            session_id=session_id,
            transcript_id=transcript_id,
            question_id=question["question_id"],
            question_text=question["question_text"],
            expected_intent=self._map_category_to_intent(question["category"]),
            raw_answer=text_answer,
            cleaned_answer=text_answer,
        )

        score = screening_scoring_integration.score_question(
            session_id=session_id,
            answer_id=answer.answer_id,
            question_id=question["question_id"],
            question_text=question["question_text"],
            answer_text=answer.cleaned_answer,
            expected_intent=self._map_category_to_intent(question["category"]),
        )

        behavioral = behavioral_analysis_integration.analyze_answer(
            session_id=session_id,
            answer_id=answer.answer_id,
            text=answer.cleaned_answer,
            duration_seconds=0,
        )

        return {
            "transcript": transcript,
            "answer": answer,
            "score": score,
            "behavioral": behavioral,
            "next_question": self.get_next_question(session_id),
        }

    def get_next_question(self, session_id: str) -> dict[str, Any] | None:
        """Get next unanswered question for session."""
        session = database.get_screening_session(session_id)
        if not session:
            return None

        questions = get_questions(language=session["language"], active_only=True)
        answers = database.list_screening_answers(session_id)
        answered_ids = {a["question_id"] for a in answers}

        for question in questions:
            if question["question_id"] not in answered_ids:
                return question
        return None

    def complete_session(self, session_id: str) -> dict[str, Any]:
        """Complete screening session and generate final report."""
        session = database.get_screening_session(session_id)
        if not session:
            raise ValueError("Session not found")

        candidate_id = session["candidate_id"]
        opening_id = session["opening_id"]

        conversation_flow_integration.cancel_session(session_id)
        database.update_screening_session_status(session_id, "COMPLETED")

        aggregate = screening_scoring_integration.score_session(
            session_id=session_id,
            candidate_id=candidate_id,
        )

        report = screening_report_integration.generate_report(
            session_id=session_id,
            candidate_id=candidate_id,
            opening_id=opening_id,
        )

        behavioral_summary = behavioral_analysis_integration.get_session_summary(session_id)

        return {
            "session": session,
            "aggregate_score": aggregate,
            "report": report,
            "behavioral_summary": behavioral_summary,
        }

    def get_session_status(self, session_id: str) -> dict[str, Any]:
        """Get comprehensive session status."""
        session = database.get_screening_session(session_id)
        if not session:
            raise ValueError("Session not found")

        questions = get_questions(language=session["language"], active_only=True)
        answers = database.list_screening_answers(session_id)
        scores = screening_scoring_integration.list_question_scores(session_id)
        aggregate = screening_scoring_integration.get_aggregate_score(session_id)
        behavioral = behavioral_analysis_integration.get_session_summary(session_id)
        next_question = self.get_next_question(session_id)

        return {
            "session": session,
            "total_questions": len(questions),
            "answered_questions": len(answers),
            "remaining_questions": len(questions) - len(answers),
            "next_question": next_question,
            "question_scores": scores,
            "aggregate_score": aggregate,
            "behavioral_summary": behavioral,
        }

    def _get_question(self, question_id: str) -> dict[str, Any] | None:
        """Get question by ID from dataset."""
        for question in self.dataset["questions"]:
            if question["question_id"] == question_id:
                return question
        return None

    def _map_category_to_intent(self, category: str) -> str:
        """Map question category to expected intent."""
        mapping = {
            "INTRODUCTION": "skills",
            "EDUCATION": "skills",
            "EXPERIENCE": "experience",
            "SKILLS": "skills",
            "LOCATION": "availability",
            "SALARY": "salary_expectation",
            "NOTICE_PERIOD": "availability",
        }
        return mapping.get(category, "skills")


screening_pipeline = ScreeningPipeline()