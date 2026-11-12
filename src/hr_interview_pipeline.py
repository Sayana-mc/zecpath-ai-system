"""Day 33-40 Unified HR Interview Pipeline Orchestrator."""

import uuid
from typing import Any

try:
    from . import database
except ImportError:
    from src import database
from .hr_interview_engine import hr_interview_engine, InterviewFlowStateMachine
from .hr_followup_engine import hr_followup_engine
from .hr_communication_evaluator import hr_communication_evaluator
from .hr_confidence_analyzer import hr_confidence_analyzer
from .hr_scoring_engine import hr_scoring_engine
from .hr_aptitude_engine import hr_aptitude_engine
from .hr_summary_generator import hr_summary_generator


class HRInterviewPipeline:
    """Orchestrates end-to-end AI HR Interview workflows across all integrated components."""

    def create_session(
        self,
        candidate_id: str,
        opening_id: str,
        experience_level: str = "FRESHER",
        role_type: str = "NON_TECHNICAL",
        recruiter_id: str | None = None,
    ) -> dict[str, Any]:
        return hr_interview_engine.create_interview_session(
            candidate_id=candidate_id,
            opening_id=opening_id,
            experience_level=experience_level,
            role_type=role_type,
            recruiter_id=recruiter_id,
        )

    def start_session(self, interview_id: str) -> dict[str, Any]:
        return hr_interview_engine.start_interview(interview_id)

    def get_session_status(self, interview_id: str) -> dict[str, Any]:
        session = database.get_hr_interview_session(interview_id)
        if not session:
            raise ValueError(f"Interview {interview_id} not found")

        questions = database.list_hr_interview_questions(interview_id)
        responses = database.list_hr_interview_responses(interview_id)
        followups = database.list_hr_interview_followups(interview_id)
        score = database.get_hr_interview_score(interview_id)
        report = database.get_hr_interview_report_by_interview(interview_id)

        return {
            "session": session,
            "total_questions": len(questions),
            "answered_questions": len(responses),
            "remaining_questions": max(0, len(questions) - len(responses)),
            "followup_count": len(followups),
            "score": score,
            "has_report": report is not None,
        }

    def process_answer(
        self,
        interview_id: str,
        question_id: str,
        answer_text: str,
    ) -> dict[str, Any]:
        """Processes candidate answer: records response, evaluates communication, analyzes confidence/signals, and determines follow-ups."""
        session = database.get_hr_interview_session(interview_id)
        if not session:
            raise ValueError(f"Interview {interview_id} not found")

        # 1. Detect quality
        quality = hr_followup_engine.detect_response_quality(answer_text)

        # 2. Record response
        response_id = f"HRRSP_{uuid.uuid4().hex[:8].upper()}"
        resp_record = {
            "response_id": response_id,
            "interview_id": interview_id,
            "question_id": question_id,
            "raw_response": answer_text,
            "cleaned_response": answer_text.strip(),
            "quality": quality,
            "follow_up_eligible": True,
            "follow_up_count": 0,
        }
        saved_response = database.save_hr_interview_response(interview_id, resp_record)

        # 3. Communication evaluation
        comm_eval = hr_communication_evaluator.evaluate_communication(
            interview_id=interview_id,
            text=answer_text,
            response_id=response_id,
        )

        # 4. Behavioral signals & contradiction analysis
        all_prev_responses = database.list_hr_interview_responses(interview_id)
        prev_responses = [r for r in all_prev_responses if r["response_id"] != response_id]
        signals = hr_confidence_analyzer.analyze_signals(
            interview_id=interview_id,
            text=answer_text,
            response_id=response_id,
            previous_answers=prev_responses,
        )

        # 5. Question & Follow-up determination
        questions = database.list_hr_interview_questions(interview_id)
        current_q = next((q for q in questions if q["question_id"] == question_id), None)
        q_text = current_q["question_text"] if current_q else "this question"

        conf_level = "high" if signals.get("confidence_score", 0) >= 80 else "normal"
        followup_decision = hr_followup_engine.evaluate_and_generate_followup(
            interview_id=interview_id,
            question_id=question_id,
            question_text=q_text,
            candidate_response=answer_text,
            confidence_level=conf_level,
        )

        # 6. Determine next question in queue
        answered_ids = {r["question_id"] for r in all_prev_responses}
        next_question = next((q for q in questions if q["question_id"] not in answered_ids), None)

        # Update current question in session
        if next_question:
            database.update_hr_interview_session_status(
                interview_id=interview_id,
                status="IN_PROGRESS",
                current_question_id=next_question["question_id"],
            )

        return {
            "response": saved_response,
            "communication_evaluation": comm_eval,
            "behavioral_signals": signals,
            "followup_decision": followup_decision,
            "next_question": next_question,
        }

    def process_followup(
        self,
        interview_id: str,
        parent_question_id: str,
        followup_type: str,
        followup_question: str,
        candidate_response: str,
    ) -> dict[str, Any]:
        """Saves candidate response to an adaptive follow-up question."""
        followup_id = f"HRFU_{uuid.uuid4().hex[:8].upper()}"
        followup_record = {
            "followup_id": followup_id,
            "interview_id": interview_id,
            "parent_question_id": parent_question_id,
            "followup_type": followup_type,
            "followup_question": followup_question,
            "candidate_response": candidate_response,
            "difficulty_level": "medium",
        }
        saved = database.save_hr_interview_followup(interview_id, followup_record)
        return saved

    def pause_session(self, interview_id: str) -> dict[str, Any]:
        updated = database.update_hr_interview_session_status(
            interview_id=interview_id,
            status="PAUSED",
        )
        if not updated:
            raise ValueError(f"Interview {interview_id} not found")
        return updated

    def resume_session(self, interview_id: str) -> dict[str, Any]:
        updated = database.update_hr_interview_session_status(
            interview_id=interview_id,
            status="IN_PROGRESS",
        )
        if not updated:
            raise ValueError(f"Interview {interview_id} not found")
        return updated

    def complete_session(self, interview_id: str) -> dict[str, Any]:
        """Concludes interview: marks COMPLETED, calculates overall HR scores, generates full report."""
        session = database.get_hr_interview_session(interview_id)
        if not session:
            raise ValueError(f"Interview {interview_id} not found")

        # Update session status to COMPLETED
        updated_session = database.update_hr_interview_session_status(
            interview_id=interview_id,
            status="COMPLETED",
            current_phase="COMPLETED",
        )

        # Calculate HR scores
        score_data = hr_scoring_engine.calculate_session_score(
            interview_id=interview_id,
            candidate_id=session["candidate_id"],
        )

        # Build & save report
        report = hr_summary_generator.generate_and_save_report(interview_id)

        return {
            "session": updated_session,
            "score": score_data,
            "report": report,
            "status": "COMPLETED",
        }

    def record_decision(
        self,
        interview_id: str,
        decision: str,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Records recruiter review decision (PROCEED, HOLD, REJECT, MANUAL_REVIEW) and comments."""
        updated = database.update_hr_interview_decision(
            interview_id=interview_id,
            decision=decision,
            notes=notes,
        )
        if not updated:
            raise ValueError(f"Interview report for {interview_id} not found")
        return updated


hr_interview_pipeline = HRInterviewPipeline()

