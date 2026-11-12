"""Day 39: HR Interview Summary and Recruiter Report Generator."""

import json
import uuid
from typing import Any

try:
    from . import database
except ImportError:
    from src import database


class HRInterviewSummaryGenerator:
    """Generates structured, explainable recruiter dossiers from HR interview data."""

    def __init__(self):
        self.risk_keywords = [
            "confused",
            "uncertain",
            "don't know",
            "not sure",
            "no experience",
            "cannot commit",
            "unable",
        ]

    def identify_strengths(self, score_data: dict[str, Any], responses: list[dict[str, Any]]) -> list[str]:
        strengths: list[str] = []
        if score_data.get("communication_score", 0) >= 75:
            strengths.append("Strong and articulated communication skills.")
        if score_data.get("confidence_score", 0) >= 75:
            strengths.append("Maintained clear composure and confidence across responses.")
        if score_data.get("relevance_score", 0) >= 75:
            strengths.append("Provided direct, highly relevant answers aligned with question topics.")
        if score_data.get("consistency_score", 0) >= 75:
            strengths.append("Demonstrated factual consistency across all interview stages.")
        if not strengths:
            strengths.append("Candidate participated constructively in the structured HR interview.")
        return strengths

    def identify_improvement_areas(self, score_data: dict[str, Any], responses: list[dict[str, Any]]) -> list[str]:
        improvements: list[str] = []
        if score_data.get("communication_score", 0) < 65:
            improvements.append("Could benefit from structuring complex ideas more concisely.")
        if score_data.get("confidence_score", 0) < 65:
            improvements.append("Frequent use of uncertainty qualifiers or hesitation markers.")
        if score_data.get("relevance_score", 0) < 65:
            improvements.append("Some answers were broad and would benefit from specific examples.")
        if score_data.get("consistency_score", 0) < 70:
            improvements.append("Discrepancies identified in experience duration or background details.")
        return improvements

    def extract_teamwork_insights(self, responses: list[dict[str, Any]]) -> list[str]:
        insights = []
        for r in responses:
            text = r.get("cleaned_response", "").lower()
            if any(k in text for k in ["team", "collaborat", "peer", "cross-functional", "conflict"]):
                insights.append("Emphasized collaboration and proactive alignment with teammates.")
                break
        if not insights:
            insights.append("Standard workplace collaboration principles acknowledged.")
        return insights

    def extract_career_goals(self, responses: list[dict[str, Any]]) -> list[str]:
        goals = []
        for r in responses:
            text = r.get("cleaned_response", "").lower()
            if any(k in text for k in ["goal", "grow", "future", "lead", "architect", "learn", "aspire"]):
                goals.append("Aimed at progressive technical growth, ownership, and impactful delivery.")
                break
        if not goals:
            goals.append("Expressed commitment to role-focused professional growth.")
        return goals

    def extract_availability(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        info = {"notice_period": "Not explicitly stated", "immediate_joining": False}
        for r in responses:
            text = r.get("cleaned_response", "").lower()
            if "immediately" in text or "immediate" in text:
                info["notice_period"] = "Immediate"
                info["immediate_joining"] = True
            elif "month" in text or "days" in text or "weeks" in text:
                info["notice_period"] = "Standard notice period indicated in response"
        return info

    def generate_natural_language_summary(
        self,
        candidate_name: str,
        overall_score: float,
        strengths: list[str],
        improvement_areas: list[str],
        has_contradictions: bool,
    ) -> str:
        summary_lines = [
            f"{candidate_name} completed the structured AI HR interview session with an overall score of {overall_score}/100.",
        ]
        if strengths:
            summary_lines.append(f"Key strengths observed: {'; '.join(strengths)}.")
        if improvement_areas:
            summary_lines.append(f"Noted improvement opportunities: {'; '.join(improvement_areas)}.")
        if has_contradictions:
            summary_lines.append("Review flag: Discrepancies noted in responses; recruiter human verification is recommended.")
        else:
            summary_lines.append("Factual consistency was maintained throughout the session.")
        return " ".join(summary_lines)

    def generate_html_report(self, report_data: dict[str, Any]) -> str:
        details = report_data["interview_details"]
        score_val = report_data["performance"]["overall_hr_score"]
        status_val = report_data["performance"]["score_status"]
        strengths_html = "".join(f"<li>{s}</li>" for s in report_data["strengths"])
        improvements_html = "".join(f"<li>{i}</li>" for i in report_data["improvement_areas"])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ZecPath AI HR Interview Report - {details['candidate_name']}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 30px auto; padding: 0 20px; }}
    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85em; background: #e2e8f0; }}
    .score-badge {{ font-size: 1.4em; font-weight: bold; color: #2563eb; }}
    .card {{ background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin-bottom: 20px; }}
    h2 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
    h3 {{ color: #334155; margin-top: 24px; }}
    ul {{ padding-left: 20px; }}
  </style>
</head>
<body>
  <h2>ZecPath AI HR Interview Report</h2>
  <div class="card">
    <p><strong>Candidate:</strong> {details['candidate_name']} ({details['candidate_id']})</p>
    <p><strong>Job Opening:</strong> {details['job_title']} ({details['job_id']})</p>
    <p><strong>Overall HR Score:</strong> <span class="score-badge">{score_val}/100</span> ({status_val})</p>
    <p><strong>Status:</strong> {details['status']} | <strong>Phase:</strong> {details['current_phase']}</p>
  </div>
  <h3>Executive Summary</h3>
  <p>{report_data['summary']}</p>
  <h3>Key Strengths</h3>
  <ul>{strengths_html}</ul>
  <h3>Improvement Opportunities</h3>
  <ul>{improvements_html if improvements_html else '<li>No material shortcomings identified.</li>'}</ul>
  <h3>Recruiter Review Recommendation</h3>
  <p><strong>Suggested Action:</strong> {report_data['recruiter_review']['suggested_action']}</p>
</body>
</html>"""

    def generate_summary_report(
        self,
        session: dict[str, Any],
        candidate: dict[str, Any],
        score_data: dict[str, Any],
        questions: list[dict[str, Any]],
        responses: list[dict[str, Any]],
        comm_evals: list[dict[str, Any]] | None = None,
        signals: list[dict[str, Any]] | None = None,
        aptitude_evals: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Generates 11-section report dictionary in memory."""
        candidate_name = candidate.get("candidate_name") or candidate.get("name") or "Candidate"
        job_title = candidate.get("opening_title") or candidate.get("job_title") or "Position"
        overall_score = score_data.get("overall_hr_score", 0.0)

        strengths = self.identify_strengths(score_data, responses)
        improvements = self.identify_improvement_areas(score_data, responses)
        teamwork = self.extract_teamwork_insights(responses)
        career_goals = self.extract_career_goals(responses)
        availability = self.extract_availability(responses)
        has_contradictions = any(s.get("contradiction_detected") for s in (signals or []))

        risk_flags = []
        if has_contradictions:
            risk_flags.append("Contradictions detected between statements.")
        if score_data.get("human_review_required"):
            risk_flags.append("Overall score or completeness warrants human recruiter verification.")

        if overall_score >= 75 and not has_contradictions:
            suggested_action = "PROCEED_TO_FINAL_ROUND"
        elif overall_score >= 60:
            suggested_action = "MANUAL_RECRUITER_REVIEW"
        else:
            suggested_action = "HOLD_OR_REJECT"

        natural_summary = self.generate_natural_language_summary(
            candidate_name=candidate_name,
            overall_score=overall_score,
            strengths=strengths,
            improvement_areas=improvements,
            has_contradictions=has_contradictions,
        )

        apt_list = aptitude_evals or []
        return {
            "interview_details": {
                "interview_id": session.get("interview_id", "N/A"),
                "candidate_id": session.get("candidate_id", "N/A"),
                "candidate_name": candidate_name,
                "job_id": session.get("opening_id", "N/A"),
                "job_title": job_title,
                "status": session.get("status", "COMPLETED"),
                "current_phase": session.get("current_phase", "COMPLETED"),
                "experience_level": session.get("experience_level", "EXPERIENCED"),
                "role_type": session.get("role_type", "TECHNICAL"),
            },
            "candidate_summary": {
                "name": candidate_name,
                "skills": candidate.get("skills", []),
                "experience_level": session.get("experience_level", "EXPERIENCED"),
            },
            "performance": {
                "overall_hr_score": overall_score,
                "score_status": score_data.get("score_status", "PROVISIONAL"),
                "breakdown": score_data.get("breakdown", {}),
            },
            "performance_breakdown": {
                "overall_hr_score": overall_score,
                "score_status": score_data.get("score_status", "PROVISIONAL"),
                "breakdown": score_data.get("breakdown", {}),
            },
            "strengths": strengths,
            "identified_strengths": strengths,
            "improvement_areas": improvements,
            "areas_for_improvement": improvements,
            "teamwork_workplace_responses": teamwork,
            "teamwork_and_culture": teamwork,
            "career_goals": career_goals,
            "career_alignment": career_goals,
            "availability_commitment": availability,
            "availability_and_expectations": availability,
            "aptitude_evaluation": {
                "evaluated_count": len(apt_list),
                "evaluations": apt_list,
            },
            "aptitude_assessment": {
                "evaluated_count": len(apt_list),
                "evaluations": apt_list,
            },
            "risk_review_flags": risk_flags,
            "review_flags_and_contradictions": risk_flags,
            "recruiter_review": {
                "suggested_action": suggested_action,
                "recruiter_decision": None,
                "recruiter_notes": None,
            },
            "recruiter_review_and_decision": {
                "suggested_action": suggested_action,
                "recruiter_decision": None,
                "recruiter_notes": None,
            },
            "summary": natural_summary,
            "summary_recommendation": suggested_action,
        }

    def generate_and_save_report(
        self,
        interview_id: str,
    ) -> dict[str, Any]:
        """Generates comprehensive report and saves to database."""
        session = database.get_hr_interview_session(interview_id)
        if not session:
            raise ValueError(f"Interview {interview_id} not found")

        candidate = database.get_candidate(session["candidate_id"])
        opening = database.get_opening(session["opening_id"])
        score_record = database.get_hr_interview_score(interview_id) or {}
        responses = database.list_hr_interview_responses(interview_id)
        aptitudes = database.list_hr_aptitude_evaluations(interview_id)
        signals = database.get_hr_behavioral_signals(interview_id)

        candidate_name = candidate.get("name", "Candidate") if candidate else "Candidate"
        job_title = opening.get("title", "Position") if opening else "Position"

        overall_score = score_record.get("overall_hr_score", 0.0)
        strengths = self.identify_strengths(score_record, responses)
        improvements = self.identify_improvement_areas(score_record, responses)
        teamwork = self.extract_teamwork_insights(responses)
        career_goals = self.extract_career_goals(responses)
        availability = self.extract_availability(responses)
        has_contradictions = any(s.get("contradiction_detected") for s in signals)

        # Risk and review flags
        risk_flags = []
        if has_contradictions:
            risk_flags.append("Contradictions detected between statements.")
        if score_record.get("human_review_required"):
            risk_flags.append("Overall score or completeness warrants human recruiter verification.")

        # Recruiter review recommendation
        if overall_score >= 75 and not has_contradictions:
            suggested_action = "PROCEED_TO_FINAL_ROUND"
        elif overall_score >= 60:
            suggested_action = "MANUAL_RECRUITER_REVIEW"
        else:
            suggested_action = "HOLD_OR_REJECT"

        natural_summary = self.generate_natural_language_summary(
            candidate_name=candidate_name,
            overall_score=overall_score,
            strengths=strengths,
            improvement_areas=improvements,
            has_contradictions=has_contradictions,
        )

        report_payload = {
            "interview_details": {
                "interview_id": interview_id,
                "candidate_id": session["candidate_id"],
                "candidate_name": candidate_name,
                "job_id": session["opening_id"],
                "job_title": job_title,
                "status": session["status"],
                "current_phase": session["current_phase"],
                "experience_level": session["experience_level"],
                "role_type": session["role_type"],
            },
            "candidate_summary": {
                "name": candidate_name,
                "skills": candidate.get("skills", []) if candidate else [],
                "experience_level": session["experience_level"],
            },
            "performance": {
                "overall_hr_score": overall_score,
                "score_status": score_record.get("score_status", "PROVISIONAL"),
                "breakdown": score_record.get("breakdown", {}),
            },
            "performance_breakdown": {
                "overall_hr_score": overall_score,
                "score_status": score_record.get("score_status", "PROVISIONAL"),
                "breakdown": score_record.get("breakdown", {}),
            },
            "strengths": strengths,
            "identified_strengths": strengths,
            "improvement_areas": improvements,
            "areas_for_improvement": improvements,
            "teamwork_workplace_responses": teamwork,
            "teamwork_and_culture": teamwork,
            "career_goals": career_goals,
            "career_alignment": career_goals,
            "availability_commitment": availability,
            "availability_and_expectations": availability,
            "aptitude_evaluation": {
                "evaluated_count": len(aptitudes),
                "evaluations": aptitudes,
            },
            "aptitude_assessment": {
                "evaluated_count": len(aptitudes),
                "evaluations": aptitudes,
            },
            "risk_review_flags": risk_flags,
            "review_flags_and_contradictions": risk_flags,
            "recruiter_review": {
                "suggested_action": suggested_action,
                "recruiter_decision": None,
                "recruiter_notes": None,
            },
            "recruiter_review_and_decision": {
                "suggested_action": suggested_action,
                "recruiter_decision": None,
                "recruiter_notes": None,
            },
            "summary": natural_summary,
            "summary_recommendation": suggested_action,
        }

        html_report = self.generate_html_report(report_payload)

        report_id = f"HRREP_{uuid.uuid4().hex[:8].upper()}"
        report_record = {
            "report_id": report_id,
            "interview_id": interview_id,
            "candidate_id": session["candidate_id"],
            "opening_id": session["opening_id"],
            "report_json": report_payload,
            "html_report": html_report,
            "version": 1,
            "recruiter_decision": None,
            "recruiter_notes": None,
        }
        saved_report = database.save_hr_interview_report(report_record)
        return saved_report

    generate_and_save_dossier = generate_and_save_report


hr_summary_generator = HRInterviewSummaryGenerator()

