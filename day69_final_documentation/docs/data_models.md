# ZecPath Data Models

Defined in `src/schemas.py` (Pydantic) and persisted in SQLite (`src/database.py`):

- **Openings & Candidates:** `openings`, `candidates`, `processing_jobs`, `recruiter_accounts`, `recruiter_login_attempts`.
- **Assessments:** `eligibility_evaluations`, `screening_sessions`, `hr_interview_sessions`, `technical_interview_sessions`, `machine_test_assignments`, `machine_test_submissions`, `integrity_records`, `behavioral_records`.
- **Aggregation & Decisions:** `role_weight_configurations`, `cross_round_evaluations` (with `input_fingerprint`), `decision_thresholds`, `final_recommendations`, `recommendation_decision_history`, `hiring_intelligence_reports`.
- **Governance:** `audit_events` (SHA-256 hash chain), `candidate_consents`, `retention_policies`.
