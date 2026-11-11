# Days 33–40: Database Schema Changes

All schema changes are strictly additive and backward compatible with existing migrations in `src/database.py`.

---

## 1. New SQLite Tables

### `hr_interview_sessions`
- `interview_id` (TEXT, PK)
- `candidate_id` (TEXT, FK -> candidates)
- `opening_id` (TEXT, FK -> openings)
- `status` (TEXT): `CREATED`, `IN_PROGRESS`, `PAUSED`, `COMPLETED`, `CANCELLED`
- `current_phase` (TEXT): `CREATED`, `INTRODUCTION`, `CORE_HR_QUESTIONS`, `ROLE_BASED_EVALUATION`, `CLOSING`, `COMPLETED`
- `current_question_id` (TEXT, Nullable)
- `experience_level` (TEXT): `FRESHER`, `EXPERIENCED`
- `role_type` (TEXT): `TECHNICAL`, `NON_TECHNICAL`
- `recruiter_id` (TEXT, Nullable)
- `created_at` (TEXT), `updated_at` (TEXT)

### `hr_interview_questions`
- `question_id` (TEXT, PK)
- `interview_id` (TEXT, FK -> hr_interview_sessions)
- `category` (TEXT)
- `question_text` (TEXT)
- `role_type` (TEXT), `experience_level` (TEXT), `difficulty` (TEXT)
- `expected_answer_criteria` (TEXT, Nullable)
- `evaluation_parameters` (TEXT, JSON string)
- `follow_up_eligibility` (INTEGER, Boolean)
- `question_order` (INTEGER)
- `active_status` (INTEGER, Boolean)
- `created_at` (TEXT)

### `hr_interview_responses`
- `response_id` (TEXT, PK)
- `interview_id` (TEXT, FK -> hr_interview_sessions)
- `question_id` (TEXT, FK -> hr_interview_questions)
- `raw_response` (TEXT), `cleaned_response` (TEXT)
- `quality` (TEXT): `incomplete`, `vague`, `complete`
- `follow_up_eligible` (INTEGER, Boolean)
- `follow_up_count` (INTEGER)
- `created_at` (TEXT), `updated_at` (TEXT)

### `hr_interview_followups`
- `followup_id` (TEXT, PK)
- `interview_id` (TEXT, FK -> hr_interview_sessions)
- `parent_question_id` (TEXT, FK -> hr_interview_questions)
- `followup_type` (TEXT): `clarification`, `deepening`, `example_based`, `scenario_based`
- `followup_question` (TEXT)
- `candidate_response` (TEXT, Nullable)
- `difficulty_level` (TEXT)
- `created_at` (TEXT), `updated_at` (TEXT)

### `hr_communication_evaluations`
- `evaluation_id` (TEXT, PK)
- `interview_id` (TEXT, FK -> hr_interview_sessions)
- `response_id` (TEXT, Nullable)
- `fluency_score` (REAL), `grammar_score` (REAL), `vocabulary_score` (REAL)
- `clarity_score` (REAL), `structure_score` (REAL), `filler_control_score` (REAL)
- `total_communication_score` (REAL)
- `fillers_detected` (TEXT, JSON list)
- `evidence` (TEXT, JSON dict)
- `created_at` (TEXT)

### `hr_behavioral_signals`
- `signal_id` (TEXT, PK)
- `interview_id` (TEXT, FK -> hr_interview_sessions)
- `response_id` (TEXT, Nullable)
- `hesitation_count` (INTEGER), `pause_count` (INTEGER), `uncertainty_count` (INTEGER), `repeated_word_count` (INTEGER)
- `sentiment` (TEXT), `sentiment_score` (REAL), `stress_score` (REAL), `confidence_score` (REAL)
- `contradiction_detected` (INTEGER, Boolean), `contradiction_reason` (TEXT, Nullable)
- `disclaimer` (TEXT)
- `created_at` (TEXT)

### `hr_aptitude_evaluations`
- `aptitude_id` (TEXT, PK)
- `interview_id` (TEXT, FK -> hr_interview_sessions)
- `question_id` (TEXT)
- `category` (TEXT), `candidate_answer` (TEXT)
- `logic_score` (REAL), `clarity_score` (REAL), `problem_solving_score` (REAL), `decision_making_score` (REAL), `communication_score` (REAL), `overall_score` (REAL)
- `evaluation_details` (TEXT, JSON dict)
- `created_at` (TEXT)

### `hr_interview_scores`
- `score_id` (TEXT, PK)
- `interview_id` (TEXT, FK -> hr_interview_sessions)
- `candidate_id` (TEXT, FK -> candidates)
- `relevance_score` (REAL), `communication_score` (REAL), `confidence_score` (REAL), `consistency_score` (REAL), `overall_hr_score` (REAL)
- `score_status` (TEXT): `EXCELLENT`, `STRONG`, `MODERATE`, `DEVELOPING`
- `breakdown` (TEXT, JSON dict)
- `created_at` (TEXT), `updated_at` (TEXT)

### `hr_interview_reports`
- `report_id` (TEXT, PK)
- `interview_id` (TEXT, FK -> hr_interview_sessions)
- `candidate_id` (TEXT, FK -> candidates)
- `opening_id` (TEXT, FK -> openings)
- `report_json` (TEXT, JSON dict)
- `html_report` (TEXT, HTML string)
- `version` (INTEGER)
- `recruiter_decision` (TEXT, Nullable)
- `recruiter_notes` (TEXT, Nullable)
- `created_at` (TEXT), `updated_at` (TEXT)

