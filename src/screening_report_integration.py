"""Screening report generation integration for the root application."""

import json
import uuid
from typing import Any

from day28_ai_screening_report_generator.src.report_builder import ScreeningReportBuilder
from day28_ai_screening_report_generator.src.report_formatter import RecruiterReportFormatter

try:
    from . import database
except ImportError:
    from src import database
from .schemas import (
    ScreeningReportFullCreate,
    ScreeningReportFullResponse,
)


class ScreeningReportIntegration:
    """Wrapper for screening report generation with database persistence."""

    def __init__(self):
        self.builder = ScreeningReportBuilder({})
        self.formatter = RecruiterReportFormatter

    def format_report(self, report: dict[str, Any], format_type: str = "text") -> str:
        """Format report using the RecruiterReportFormatter."""
        formatter = self.formatter(report)
        if format_type == "html":
            # For now, wrap text in simple HTML
            text = formatter.format_text()
            return f"<pre>{text}</pre>"
        return formatter.format_text()

    def generate_report(
        self,
        session_id: str,
        candidate_id: str,
        opening_id: str,
    ) -> ScreeningReportFullResponse:
        """Generate comprehensive screening report for a session."""
        session = database.get_screening_session(session_id)
        if not session:
            raise ValueError("Session not found")

        candidate = database.get_candidate(candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        opening = database.get_opening(opening_id)
        if not opening:
            raise ValueError("Opening not found")

        answers = database.list_screening_answers(session_id)
        scores = database.list_screening_question_scores(session_id)
        aggregate = database.get_screening_aggregate_score(session_id)
        behavioral = database.get_behavioral_analysis(session_id)

        total_score = 0
        questions_evaluated = 0
        if aggregate:
            total_score = aggregate.get("overall_score", 0)
            questions_evaluated = aggregate.get("questions_evaluated", 0)

        report_data = {
            "candidate_id": candidate_id,
            "candidate_name": candidate.get("name"),
            "job_id": opening_id,
            "job_title": opening.get("title"),
            "screening_score": {
                "total_score": total_score,
                "questions_evaluated": questions_evaluated,
            },
            "answers": [
                {
                    "question_id": a["question_id"],
                    "question": a["question_text"],
                    "answer": a["cleaned_answer"],
                    "intent": a["detected_intent"],
                    "status": a["answer_status"].lower(),
                    "extracted_information": (
                        json.loads(a["extracted_information"])
                        if isinstance(a["extracted_information"], str)
                        else a["extracted_information"]
                    ),
                    "score": next((s for s in scores if s["answer_id"] == a["answer_id"]), None),
                }
                for a in answers
            ],
            "behavioral_analysis": {
                "communication_strength": self._get_communication_strength(behavioral),
                "hesitation_count": sum(b.get("hesitation_count", 0) for b in behavioral),
                "uncertainty_count": sum(b.get("uncertainty_count", 0) for b in behavioral),
                "average_response_length": self._get_avg_response_length(behavioral),
                "sentiment": behavioral[0].get("sentiment") if behavioral else None,
                "contradictions_detected": any(b.get("contradiction_detected") for b in behavioral),
            },
        }

        builder = ScreeningReportBuilder(report_data)
        report = builder.build_report()

        html_report = self.format_report(report, format_type="html")

        report_id = str(uuid.uuid4())
        report_record = ScreeningReportFullCreate(
            candidate_id=candidate_id,
            opening_id=opening_id,
            report_json=report,
            html_report=html_report,
        )

        saved = database.save_screening_report_full(session_id, {
            "report_id": report_id,
            "session_id": session_id,
            "candidate_id": candidate_id,
            "opening_id": opening_id,
            "report_json": report,
            "html_report": html_report,
            "pdf_report": None,
        })
        return ScreeningReportFullResponse(**saved)

    def get_report(self, report_id: str) -> ScreeningReportFullResponse | None:
        """Get report by ID."""
        report = database.get_screening_report_full(report_id)
        if not report:
            return None
        return ScreeningReportFullResponse(**report)

    def list_session_reports(self, session_id: str) -> list[ScreeningReportFullResponse]:
        """List all reports for a session."""
        reports = database.list_screening_reports_full(session_id)
        return [ScreeningReportFullResponse(**r) for r in reports]

    def _get_communication_strength(self, behavioral: list[dict[str, Any]]) -> str | None:
        """Determine communication strength from behavioral data."""
        if not behavioral:
            return None
        avg_confidence = sum(b.get("confidence_score", 0) for b in behavioral) / len(behavioral)
        if avg_confidence >= 70:
            return "Clear and confident communication"
        elif avg_confidence >= 40:
            return "Moderate communication clarity"
        return "Communication could be improved"

    def _get_avg_response_length(self, behavioral: list[dict[str, Any]]) -> str | None:
        """Get average response length category."""
        if not behavioral:
            return None
        lengths = [b.get("response_length_category") for b in behavioral if b.get("response_length_category")]
        if not lengths:
            return None
        return max(set(lengths), key=lengths.count)


screening_report_integration = ScreeningReportIntegration()