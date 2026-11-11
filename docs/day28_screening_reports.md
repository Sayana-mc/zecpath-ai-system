# Day 28 — AI Screening Report Generator

## 1. Overview
The Day 28 report generator aggregates candidate transcripts, intent validations, scoring dimensions, and behavioral indicators into an executive recruiter screening report.

## 2. Report Structure
- **Candidate & Job Identification:** Candidate ID, Candidate Name, Opening ID, Job Title, Timestamp.
- **Screening Summary:** Overall score, status (`COMPLETED`, `REVIEW_REQUIRED`), total questions evaluated, question completion rate.
- **Detailed Question Breakdown:**
  - Question text and candidate transcript.
  - Detected intent and validation status.
  - Multi-parameter scores (clarity, relevance, completeness, consistency).
  - Score explanation and structured entity extraction summary.
- **Communication & Behavioral Assessment:**
  - Communication strength category.
  - Aggregate hesitation and uncertainty metrics.
  - Pacing and sentiment distribution.
  - Contradiction alerts.
- **Recruiter Recommendation:** Suggestion based on aggregate performance (`PROCEED_TO_INTERVIEW`, `MANUAL_REVIEW`, `INELIGIBLE`).

## 3. Formatting & Persistence
- Exportable as structured JSON (`report_json`) and HTML (`html_report`).
- Persisted in `screening_reports_full` database table linked to candidate and session records.
- Accessible via REST API: `GET /api/v1/screening/sessions/{session_id}/report` and `GET /api/v1/screening/candidates/{candidate_id}/reports`.

