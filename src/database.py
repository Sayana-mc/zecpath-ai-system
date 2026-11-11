"""SQLite persistence for the local Zecpath ATS API."""

import hashlib
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator


def _database_path() -> Path:
    configured_path = os.environ.get("ZECPATH_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / "data" / "zecpath.sqlite3"


def _init_db() -> None:
    """Initializes tables and migrations for the current database path."""
    with _connection():
        pass


@contextmanager
def _connection() -> Generator[sqlite3.Connection, None, None]:
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS openings (
            opening_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            required_skills TEXT NOT NULL,
            preferred_skills TEXT NOT NULL,
            minimum_education TEXT,
            minimum_years_experience REAL,
            status TEXT NOT NULL CHECK (status IN ('OPEN', 'CLOSED')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            skills TEXT NOT NULL,
            resume_text TEXT NOT NULL DEFAULT '',
            resume_data TEXT NOT NULL DEFAULT '{}',
            resume_filename TEXT,
            application_status TEXT NOT NULL CHECK (
                application_status IN (
                    'APPLIED', 'IN_REVIEW', 'SHORTLISTED', 'INTERVIEW',
                    'OFFER', 'HIRED', 'REJECTED', 'WITHDRAWN'
                )
            ),
            score REAL,
            score_evidence TEXT,
            location TEXT,
            relocation_willingness INTEGER,
            work_mode_preference TEXT,
            availability_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE (opening_id, email)
        );
        CREATE INDEX IF NOT EXISTS candidates_opening_idx
            ON candidates(opening_id, application_status);
        CREATE TABLE IF NOT EXISTS processing_jobs (
            job_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            candidate_id TEXT,
            status TEXT NOT NULL CHECK (
                status IN ('QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED')
            ),
            result TEXT,
            error TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS screening_reports (
            report_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            report_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS screening_reports_candidate_idx
            ON screening_reports(candidate_id, created_at);
        CREATE TABLE IF NOT EXISTS recruiter_sessions (
            token_hash TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS recruiter_accounts (
            username TEXT PRIMARY KEY,
            password_salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS recruiter_sessions_expiry_idx
            ON recruiter_sessions(expires_at);
        CREATE TABLE IF NOT EXISTS eligibility_configurations (
            opening_id TEXT PRIMARY KEY REFERENCES openings(opening_id) ON DELETE CASCADE,
            version INTEGER NOT NULL,
            configuration_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS eligibility_evaluations (
            evaluation_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            configuration_version INTEGER NOT NULL,
            input_fingerprint TEXT NOT NULL,
            result_json TEXT NOT NULL,
            evaluated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS eligibility_latest_idx
            ON eligibility_evaluations(candidate_id, opening_id, evaluated_at);
        CREATE TABLE IF NOT EXISTS screening_sessions (
            session_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            status TEXT NOT NULL CHECK (
                status IN ('CREATED', 'IN_PROGRESS', 'INTERRUPTED', 'COMPLETED', 'CANCELLED')
            ),
            language TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            source TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS screening_sessions_candidate_idx
            ON screening_sessions(candidate_id, opening_id, created_at);
        CREATE TABLE IF NOT EXISTS transcript_segments (
            segment_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
            question_id TEXT,
            speaker TEXT NOT NULL CHECK (
                speaker IN ('CANDIDATE', 'RECRUITER', 'AI', 'SYSTEM', 'FOLLOW_UP')
            ),
            raw_text TEXT NOT NULL,
            normalized_text TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            confidence REAL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
            language TEXT,
            source TEXT NOT NULL,
            processing_version TEXT NOT NULL,
            sequence_number INTEGER NOT NULL CHECK (sequence_number > 0),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(session_id, sequence_number)
        );
        CREATE INDEX IF NOT EXISTS transcript_segments_session_idx
            ON transcript_segments(session_id, sequence_number);
        CREATE TABLE IF NOT EXISTS screening_interactions (
            interaction_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
            question_id TEXT NOT NULL,
            candidate_answer TEXT,
            answer_type TEXT,
            validation_status TEXT NOT NULL CHECK (
                validation_status IN ('PENDING', 'VALID', 'INVALID', 'SKIPPED', 'UNANSWERED')
            ),
            display_order INTEGER NOT NULL CHECK (display_order > 0),
            follow_up_to TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(session_id, display_order)
        );
        CREATE INDEX IF NOT EXISTS screening_interactions_session_idx
            ON screening_interactions(session_id, display_order);
        CREATE TABLE IF NOT EXISTS recruiter_login_attempts (
            key_hash TEXT PRIMARY KEY,
            attempts INTEGER NOT NULL,
            window_started REAL NOT NULL,
            blocked_until REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS screening_audio (
            audio_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
            question_id TEXT,
            file_path TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            duration_seconds REAL,
            mime_type TEXT,
            source TEXT NOT NULL CHECK (source IN ('UPLOAD', 'RECORDING')),
            status TEXT NOT NULL CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS screening_audio_session_idx
            ON screening_audio(session_id, created_at);
        CREATE TABLE IF NOT EXISTS screening_transcripts (
            transcript_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
            audio_id TEXT REFERENCES screening_audio(audio_id) ON DELETE SET NULL,
            question_id TEXT,
            raw_text TEXT NOT NULL,
            cleaned_text TEXT NOT NULL,
            language TEXT,
            language_probability REAL,
            partial_answer INTEGER NOT NULL CHECK (partial_answer IN (0, 1)),
            processing_version TEXT NOT NULL,
            segment_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS screening_transcripts_session_idx
            ON screening_transcripts(session_id, question_id);
        CREATE TABLE IF NOT EXISTS screening_answers (
            answer_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
            transcript_id TEXT REFERENCES screening_transcripts(transcript_id) ON DELETE SET NULL,
            question_id TEXT NOT NULL,
            question_text TEXT NOT NULL,
            expected_intent TEXT NOT NULL,
            detected_intent TEXT,
            answer_status TEXT NOT NULL CHECK (answer_status IN ('VALID', 'INVALID', 'PARTIAL', 'VAGUE', 'OFF_TOPIC', 'UNCLEAR', 'MISSING')),
            raw_answer TEXT NOT NULL,
            cleaned_answer TEXT NOT NULL,
            extracted_information TEXT NOT NULL DEFAULT '{}',
            intent_confidence REAL,
            needs_clarification INTEGER NOT NULL CHECK (needs_clarification IN (0, 1)),
            is_off_topic INTEGER NOT NULL CHECK (is_off_topic IN (0, 1)),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS screening_answers_session_idx
            ON screening_answers(session_id, question_id);
        CREATE TABLE IF NOT EXISTS screening_question_scores (
            score_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
            answer_id TEXT NOT NULL REFERENCES screening_answers(answer_id) ON DELETE CASCADE,
            question_id TEXT NOT NULL,
            clarity_score INTEGER NOT NULL CHECK (clarity_score BETWEEN 0 AND 5),
            relevance_score INTEGER NOT NULL CHECK (relevance_score BETWEEN 0 AND 5),
            completeness_score INTEGER NOT NULL CHECK (completeness_score BETWEEN 0 AND 5),
            consistency_score INTEGER NOT NULL CHECK (consistency_score BETWEEN 0 AND 5),
            weighted_score REAL NOT NULL,
            normalized_score REAL NOT NULL,
            explanation TEXT NOT NULL,
            human_review_required INTEGER NOT NULL CHECK (human_review_required IN (0, 1)),
            scoring_version TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS screening_question_scores_session_idx
            ON screening_question_scores(session_id, question_id);
        CREATE TABLE IF NOT EXISTS screening_aggregate_scores (
            aggregate_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            overall_score REAL NOT NULL,
            score_status TEXT NOT NULL CHECK (score_status IN ('PROVISIONAL', 'FINAL', 'REVIEW_REQUIRED')),
            questions_evaluated INTEGER NOT NULL,
            questions_answered INTEGER NOT NULL,
            questions_missing INTEGER NOT NULL,
            human_review_required INTEGER NOT NULL CHECK (human_review_required IN (0, 1)),
            scoring_version TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS screening_aggregate_scores_session_idx
            ON screening_aggregate_scores(session_id);
        CREATE TABLE IF NOT EXISTS behavioral_analysis (
            analysis_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
            answer_id TEXT REFERENCES screening_answers(answer_id) ON DELETE SET NULL,
            sentiment TEXT CHECK (sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE', 'MIXED', 'UNCERTAIN')),
            sentiment_score REAL,
            confidence_score REAL,
            hesitation_count INTEGER NOT NULL DEFAULT 0,
            uncertainty_count INTEGER NOT NULL DEFAULT 0,
            contradiction_detected INTEGER NOT NULL CHECK (contradiction_detected IN (0, 1)),
            contradiction_details TEXT,
            response_length_category TEXT CHECK (response_length_category IN ('SHORT', 'MEDIUM', 'LONG')),
            words_per_minute REAL,
            pace_category TEXT CHECK (pace_category IN ('FAST', 'NORMAL', 'SLOW', 'UNKNOWN')),
            processing_version TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS behavioral_analysis_session_idx
            ON behavioral_analysis(session_id);
        CREATE TABLE IF NOT EXISTS screening_reports_full (
            report_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            report_json TEXT NOT NULL,
            html_report TEXT,
            pdf_report BLOB,
            version INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL CHECK (status IN ('GENERATING', 'COMPLETED', 'FAILED')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS screening_reports_full_session_idx
            ON screening_reports_full(session_id);

        CREATE TABLE IF NOT EXISTS hr_interview_sessions (
            interview_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            status TEXT NOT NULL CHECK (status IN ('CREATED', 'IN_PROGRESS', 'PAUSED', 'COMPLETED', 'CANCELLED', 'FAILED')),
            current_phase TEXT NOT NULL CHECK (current_phase IN ('CREATED', 'INTRODUCTION', 'CORE_HR_QUESTIONS', 'ROLE_BASED_EVALUATION', 'CLOSING', 'COMPLETED')),
            current_question_id TEXT,
            experience_level TEXT NOT NULL CHECK (experience_level IN ('FRESHER', 'EXPERIENCED')),
            role_type TEXT NOT NULL CHECK (role_type IN ('TECHNICAL', 'NON_TECHNICAL')),
            recruiter_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hr_interview_sessions_cand_idx ON hr_interview_sessions(candidate_id);
        CREATE INDEX IF NOT EXISTS hr_interview_sessions_open_idx ON hr_interview_sessions(opening_id);

        CREATE TABLE IF NOT EXISTS hr_interview_questions (
            question_id TEXT PRIMARY KEY,
            interview_id TEXT NOT NULL REFERENCES hr_interview_sessions(interview_id) ON DELETE CASCADE,
            category TEXT NOT NULL,
            question_text TEXT NOT NULL,
            role_type TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            difficulty TEXT NOT NULL DEFAULT 'simple',
            expected_answer_criteria TEXT,
            evaluation_parameters TEXT,
            follow_up_eligibility INTEGER NOT NULL DEFAULT 1,
            question_order INTEGER NOT NULL DEFAULT 0,
            active_status INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hr_interview_questions_interview_idx ON hr_interview_questions(interview_id);

        CREATE TABLE IF NOT EXISTS hr_interview_responses (
            response_id TEXT PRIMARY KEY,
            interview_id TEXT NOT NULL REFERENCES hr_interview_sessions(interview_id) ON DELETE CASCADE,
            question_id TEXT NOT NULL REFERENCES hr_interview_questions(question_id) ON DELETE CASCADE,
            raw_response TEXT NOT NULL,
            cleaned_response TEXT NOT NULL,
            quality TEXT NOT NULL CHECK (quality IN ('complete', 'vague', 'incomplete')),
            follow_up_eligible INTEGER NOT NULL DEFAULT 1,
            follow_up_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hr_interview_responses_interview_idx ON hr_interview_responses(interview_id);

        CREATE TABLE IF NOT EXISTS hr_interview_followups (
            followup_id TEXT PRIMARY KEY,
            interview_id TEXT NOT NULL REFERENCES hr_interview_sessions(interview_id) ON DELETE CASCADE,
            parent_question_id TEXT NOT NULL,
            followup_type TEXT NOT NULL CHECK (followup_type IN ('clarification', 'deepening', 'example_based', 'scenario_based')),
            followup_question TEXT NOT NULL,
            candidate_response TEXT,
            difficulty_level TEXT NOT NULL DEFAULT 'simple',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hr_interview_followups_interview_idx ON hr_interview_followups(interview_id);

        CREATE TABLE IF NOT EXISTS hr_communication_evaluations (
            evaluation_id TEXT PRIMARY KEY,
            interview_id TEXT NOT NULL REFERENCES hr_interview_sessions(interview_id) ON DELETE CASCADE,
            response_id TEXT,
            fluency_score REAL NOT NULL,
            grammar_score REAL NOT NULL,
            vocabulary_score REAL NOT NULL,
            clarity_score REAL NOT NULL,
            structure_score REAL NOT NULL,
            filler_control_score REAL NOT NULL,
            total_communication_score REAL NOT NULL,
            fillers_detected TEXT,
            evidence TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hr_comm_eval_interview_idx ON hr_communication_evaluations(interview_id);

        CREATE TABLE IF NOT EXISTS hr_behavioral_signals (
            signal_id TEXT PRIMARY KEY,
            interview_id TEXT NOT NULL REFERENCES hr_interview_sessions(interview_id) ON DELETE CASCADE,
            response_id TEXT,
            hesitation_count INTEGER NOT NULL DEFAULT 0,
            pause_count INTEGER NOT NULL DEFAULT 0,
            uncertainty_count INTEGER NOT NULL DEFAULT 0,
            repeated_word_count INTEGER NOT NULL DEFAULT 0,
            sentiment TEXT NOT NULL CHECK (sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE', 'MIXED', 'UNCERTAIN')),
            sentiment_score REAL NOT NULL DEFAULT 0.0,
            stress_score REAL NOT NULL DEFAULT 0.0,
            confidence_score REAL NOT NULL DEFAULT 0.0,
            contradiction_detected INTEGER NOT NULL DEFAULT 0,
            contradiction_reason TEXT,
            disclaimer TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hr_behavioral_signals_interview_idx ON hr_behavioral_signals(interview_id);

        CREATE TABLE IF NOT EXISTS hr_aptitude_evaluations (
            aptitude_id TEXT PRIMARY KEY,
            interview_id TEXT NOT NULL REFERENCES hr_interview_sessions(interview_id) ON DELETE CASCADE,
            question_id TEXT NOT NULL,
            category TEXT NOT NULL CHECK (category IN ('logical_reasoning', 'situational_judgment', 'problem_solving', 'decision_making', 'analytical_thinking', 'prioritization')),
            candidate_answer TEXT NOT NULL,
            logic_score REAL NOT NULL,
            clarity_score REAL NOT NULL,
            problem_solving_score REAL NOT NULL,
            decision_making_score REAL NOT NULL,
            communication_score REAL NOT NULL,
            overall_score REAL NOT NULL,
            evaluation_details TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hr_aptitude_eval_interview_idx ON hr_aptitude_evaluations(interview_id);

        CREATE TABLE IF NOT EXISTS hr_interview_scores (
            score_id TEXT PRIMARY KEY,
            interview_id TEXT NOT NULL REFERENCES hr_interview_sessions(interview_id) ON DELETE CASCADE,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            relevance_score REAL NOT NULL,
            communication_score REAL NOT NULL,
            confidence_score REAL NOT NULL,
            consistency_score REAL NOT NULL,
            overall_hr_score REAL NOT NULL,
            score_status TEXT NOT NULL CHECK (score_status IN ('PROVISIONAL', 'FINAL', 'REVIEW_REQUIRED')),
            breakdown TEXT NOT NULL,
            human_review_required INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hr_scores_interview_idx ON hr_interview_scores(interview_id);

        CREATE TABLE IF NOT EXISTS hr_interview_reports (
            report_id TEXT PRIMARY KEY,
            interview_id TEXT NOT NULL REFERENCES hr_interview_sessions(interview_id) ON DELETE CASCADE,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            report_json TEXT NOT NULL,
            html_report TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            recruiter_decision TEXT CHECK (recruiter_decision IN ('PROCEED', 'HOLD', 'REJECT', 'MANUAL_REVIEW') OR recruiter_decision IS NULL),
            recruiter_notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hr_reports_interview_idx ON hr_interview_reports(interview_id);

        CREATE TABLE IF NOT EXISTS technical_interview_sessions (
            session_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            target_role TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED')),
            current_stage TEXT NOT NULL DEFAULT 'CREATED',
            total_questions INTEGER NOT NULL DEFAULT 0,
            overall_score REAL DEFAULT 0.0,
            rubric_breakdown TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS tech_int_sess_candidate_idx ON technical_interview_sessions(candidate_id);

        CREATE TABLE IF NOT EXISTS technical_interview_questions (
            question_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES technical_interview_sessions(session_id) ON DELETE CASCADE,
            question_text TEXT NOT NULL,
            topic TEXT NOT NULL,
            question_type TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            sequence_order INTEGER NOT NULL DEFAULT 1,
            expected_criteria TEXT DEFAULT '[]',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS tech_int_q_sess_idx ON technical_interview_questions(session_id);

        CREATE TABLE IF NOT EXISTS technical_interview_responses (
            response_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES technical_interview_sessions(session_id) ON DELETE CASCADE,
            question_id TEXT NOT NULL REFERENCES technical_interview_questions(question_id) ON DELETE CASCADE,
            raw_answer TEXT NOT NULL,
            score REAL NOT NULL DEFAULT 0.0,
            depth_level TEXT NOT NULL DEFAULT 'shallow',
            parameter_scores TEXT NOT NULL DEFAULT '{}',
            feedback TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS tech_int_resp_sess_idx ON technical_interview_responses(session_id);

        CREATE TABLE IF NOT EXISTS machine_test_assignments (
            assignment_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            task_type TEXT NOT NULL CHECK (task_type IN ('coding', 'debugging', 'file_based', 'mini_system_design')),
            task_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            time_limit_minutes INTEGER NOT NULL DEFAULT 60,
            status TEXT NOT NULL CHECK (status IN ('ASSIGNED', 'IN_PROGRESS', 'SUBMITTED', 'EVALUATED', 'EXPIRED')),
            assigned_at TEXT NOT NULL,
            completed_at TEXT
        );
        CREATE INDEX IF NOT EXISTS machine_test_cand_idx ON machine_test_assignments(candidate_id);

        CREATE TABLE IF NOT EXISTS machine_test_submissions (
            submission_id TEXT PRIMARY KEY,
            assignment_id TEXT NOT NULL REFERENCES machine_test_assignments(assignment_id) ON DELETE CASCADE,
            code_content TEXT NOT NULL,
            language TEXT NOT NULL DEFAULT 'python',
            time_spent_minutes REAL NOT NULL DEFAULT 0.0,
            total_score REAL NOT NULL DEFAULT 0.0,
            rubric_scores TEXT NOT NULL DEFAULT '{}',
            execution_details TEXT NOT NULL DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'EVALUATED',
            submitted_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS machine_test_sub_assign_idx ON machine_test_submissions(assignment_id);

        CREATE TABLE IF NOT EXISTS candidate_integrity_records (
            record_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            session_id TEXT NOT NULL,
            round_type TEXT NOT NULL,
            has_consent INTEGER NOT NULL DEFAULT 1,
            total_risk_points INTEGER NOT NULL DEFAULT 0,
            risk_level TEXT NOT NULL CHECK (risk_level IN ('LOW', 'MODERATE', 'HIGH')),
            requires_human_review INTEGER NOT NULL DEFAULT 0,
            events_json TEXT NOT NULL DEFAULT '[]',
            review_flags TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS cand_integrity_cand_idx ON candidate_integrity_records(candidate_id);

        CREATE TABLE IF NOT EXISTS candidate_behavioral_records (
            record_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            session_id TEXT NOT NULL,
            round_type TEXT NOT NULL,
            has_consent INTEGER NOT NULL DEFAULT 1,
            consistency_index REAL NOT NULL DEFAULT 100.0,
            requires_human_review INTEGER NOT NULL DEFAULT 0,
            observations_json TEXT NOT NULL DEFAULT '[]',
            disclaimer TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS cand_behavioral_cand_idx ON candidate_behavioral_records(candidate_id);

        CREATE TABLE IF NOT EXISTS cross_round_evaluations (
            evaluation_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            target_role TEXT NOT NULL,
            hiring_fit_percentage REAL NOT NULL,
            round_scores_json TEXT NOT NULL,
            effective_weights_json TEXT NOT NULL,
            completed_rounds INTEGER NOT NULL,
            missing_rounds_json TEXT NOT NULL,
            anomalies_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS cross_round_cand_idx ON cross_round_evaluations(candidate_id);

        CREATE TABLE IF NOT EXISTS final_recommendations (
            recommendation_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            target_role TEXT NOT NULL,
            decision TEXT NOT NULL CHECK (decision IN ('SELECTED', 'HOLD_REVIEW', 'REJECTED')),
            score REAL NOT NULL,
            confidence REAL NOT NULL,
            completed_rounds INTEGER NOT NULL,
            expected_rounds INTEGER NOT NULL,
            reasons_json TEXT NOT NULL,
            risk_factors_json TEXT NOT NULL,
            recruiter_decision TEXT NOT NULL DEFAULT 'PENDING_REVIEW' CHECK (recruiter_decision IN ('PENDING_REVIEW', 'APPROVED', 'OVERRIDDEN', 'REJECTED')),
            recruiter_notes TEXT,
            recruiter_decided_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS final_rec_cand_idx ON final_recommendations(candidate_id);
        CREATE TABLE IF NOT EXISTS hiring_intelligence_reports (
            report_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
            version INTEGER NOT NULL DEFAULT 1,
            report_json TEXT NOT NULL,
            markdown_content TEXT NOT NULL,
            html_content TEXT NOT NULL,
            created_by_recruiter_id TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS hiring_reports_cand_ver_idx ON hiring_intelligence_reports(candidate_id, version);
        CREATE TABLE IF NOT EXISTS audit_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            details_json TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            event_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS audit_events_type_idx ON audit_events(event_type);
        CREATE INDEX IF NOT EXISTS audit_events_subject_idx ON audit_events(subject_id);
        CREATE TABLE IF NOT EXISTS candidate_coaching_records (
            coaching_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
            target_role TEXT NOT NULL,
            identified_skill_gaps_json TEXT NOT NULL,
            recommended_preparation_json TEXT NOT NULL,
            practice_questions_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS coaching_records_cand_idx ON candidate_coaching_records(candidate_id);
        """
    )
    opening_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(openings)")
    }
    if "minimum_education" not in opening_columns:
        connection.execute("ALTER TABLE openings ADD COLUMN minimum_education TEXT")
    if "minimum_years_experience" not in opening_columns:
        connection.execute(
            "ALTER TABLE openings ADD COLUMN minimum_years_experience REAL"
        )
    candidate_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(candidates)")
    }
    if "resume_data" not in candidate_columns:
        connection.execute(
            "ALTER TABLE candidates ADD COLUMN resume_data TEXT NOT NULL DEFAULT '{}'"
        )
    for column, definition in (
        ("location", "TEXT"),
        ("relocation_willingness", "INTEGER"),
        ("work_mode_preference", "TEXT"),
        ("availability_date", "TEXT"),
    ):
        if column not in candidate_columns:
            connection.execute(
                f"ALTER TABLE candidates ADD COLUMN {column} {definition}"
            )
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    """Create the local database schema if it does not exist."""
    with _connection():
        pass


def check_database() -> None:
    """Raise a SQLite error if the configured database cannot be queried."""
    with _connection() as connection:
        connection.execute("SELECT 1").fetchone()


def fail_interrupted_processing_jobs() -> int:
    """Make uploads left in flight by a prior server process visible as failures."""
    with _connection() as connection:
        cursor = connection.execute(
            """
            UPDATE processing_jobs
            SET status = 'FAILED',
                error = 'Resume processing was interrupted by a server restart. Upload it again.'
            WHERE status IN ('QUEUED', 'PROCESSING')
            """
        )
        return cursor.rowcount


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def current_timestamp() -> str:
    return _now()


def _generate_id(prefix: str = "id") -> str:
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_recruiter_session(token: str, username: str, lifetime_seconds: int) -> float:
    now = time.time()
    expires_at = now + lifetime_seconds
    with _connection() as connection:
        connection.execute(
            "DELETE FROM recruiter_sessions WHERE expires_at <= ?", (now,)
        )
        connection.execute(
            """
            INSERT INTO recruiter_sessions (
                token_hash, username, expires_at, created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (_token_hash(token), username, expires_at, now),
        )
    return expires_at


def get_recruiter_session(token: str) -> str | None:
    now = time.time()
    with _connection() as connection:
        row = connection.execute(
            """
            SELECT username FROM recruiter_sessions
            WHERE token_hash = ? AND expires_at > ?
            """,
            (_token_hash(token), now),
        ).fetchone()
        return row["username"] if row is not None else None


def get_recruiter_session_expiry(token: str) -> float | None:
    now = time.time()
    with _connection() as connection:
        row = connection.execute(
            """
            SELECT expires_at FROM recruiter_sessions
            WHERE token_hash = ? AND expires_at > ?
            """,
            (_token_hash(token), now),
        ).fetchone()
        return row["expires_at"] if row is not None else None


def get_recruiter_account(username: str) -> dict[str, str] | None:
    with _connection() as connection:
        row = connection.execute(
            """
            SELECT username, password_salt, password_hash
            FROM recruiter_accounts WHERE username = ?
            """,
            (username,),
        ).fetchone()
        return dict(row) if row is not None else None


def has_recruiter_accounts() -> bool:
    with _connection() as connection:
        return (
            connection.execute(
                "SELECT 1 FROM recruiter_accounts LIMIT 1"
            ).fetchone()
            is not None
        )


def create_first_recruiter_account(
    username: str, password_salt: str, password_hash: str
) -> None:
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        if connection.execute(
            "SELECT 1 FROM recruiter_accounts LIMIT 1"
        ).fetchone():
            raise ValueError("A recruiter account has already been initialized.")
        connection.execute(
            """
            INSERT INTO recruiter_accounts (
                username, password_salt, password_hash, created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (username, password_salt, password_hash, _now()),
        )


def reset_recruiter_account(
    username: str, password_salt: str, password_hash: str
) -> None:
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        accounts = connection.execute(
            "SELECT username FROM recruiter_accounts"
        ).fetchall()
        if not accounts:
            raise ValueError(
                "No recruiter account exists. Create the first account instead."
            )
        if len(accounts) != 1:
            raise ValueError(
                "Expected exactly one recruiter account; credentials were not changed."
            )
        connection.execute(
            """
            UPDATE recruiter_accounts
            SET username = ?, password_salt = ?, password_hash = ?
            WHERE username = ?
            """,
            (username, password_salt, password_hash, accounts[0]["username"]),
        )
        connection.execute("DELETE FROM recruiter_sessions")
        connection.execute("DELETE FROM recruiter_login_attempts")


def revoke_recruiter_session(token: str) -> None:
    with _connection() as connection:
        connection.execute(
            "DELETE FROM recruiter_sessions WHERE token_hash = ?",
            (_token_hash(token),),
        )


def recruiter_login_key(client_host: str, username: str) -> str:
    value = f"{client_host}\0{username.casefold()}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def recruiter_login_blocked(key_hash: str) -> bool:
    with _connection() as connection:
        row = connection.execute(
            "SELECT blocked_until FROM recruiter_login_attempts WHERE key_hash = ?",
            (key_hash,),
        ).fetchone()
        return row is not None and row["blocked_until"] > time.time()


def record_recruiter_login_failure(key_hash: str) -> bool:
    now = time.time()
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            """
            SELECT attempts, window_started, blocked_until
            FROM recruiter_login_attempts WHERE key_hash = ?
            """,
            (key_hash,),
        ).fetchone()
        if row is not None and row["blocked_until"] > now:
            return True
        attempts = 1
        window_started = now
        if row is not None and now - row["window_started"] < 900:
            attempts = row["attempts"] + 1
            window_started = row["window_started"]
        blocked_until = now + 900 if attempts >= 5 else 0
        connection.execute(
            """
            INSERT INTO recruiter_login_attempts (
                key_hash, attempts, window_started, blocked_until
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT(key_hash) DO UPDATE SET
                attempts = excluded.attempts,
                window_started = excluded.window_started,
                blocked_until = excluded.blocked_until
            """,
            (key_hash, attempts, window_started, blocked_until),
        )
        return blocked_until > now


def clear_recruiter_login_attempts(key_hash: str) -> None:
    with _connection() as connection:
        connection.execute(
            "DELETE FROM recruiter_login_attempts WHERE key_hash = ?", (key_hash,)
        )


def _redact_candidate_processing_jobs(
    connection: sqlite3.Connection, candidate_ids: list[str]
) -> None:
    if not candidate_ids:
        return
    placeholders = ", ".join("?" for _ in candidate_ids)
    connection.execute(
        f"""
        UPDATE processing_jobs
        SET candidate_id = NULL, result = NULL
        WHERE candidate_id IN ({placeholders})
        """,
        candidate_ids,
    )


def _opening(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    record = dict(row)
    record["required_skills"] = json.loads(record["required_skills"])
    record["preferred_skills"] = json.loads(record["preferred_skills"])
    return record


def _candidate(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    record = dict(row)
    record["skills"] = json.loads(record["skills"])
    record["resume_data"] = json.loads(record["resume_data"])
    record["score_evidence"] = (
        json.loads(record["score_evidence"])
        if record["score_evidence"] is not None
        else None
    )
    if "relocation_willingness" in record:
        record["relocation_willingness"] = (
            bool(record["relocation_willingness"])
            if record["relocation_willingness"] is not None
            else None
        )
    return record


def create_opening(data: dict[str, Any]) -> dict[str, Any]:
    opening_id = data.get("opening_id") or _generate_id("op")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO openings (
                opening_id, title, description, required_skills,
                preferred_skills, minimum_education,
                minimum_years_experience, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?)
            """,
            (
                opening_id,
                data["title"],
                data.get("description", ""),
                json.dumps(data.get("required_skills", [])),
                json.dumps(data.get("preferred_skills", [])),
                data.get("minimum_education"),
                data.get("minimum_years_experience"),
                now,
                now,
            ),
        )
        return _opening(
            connection.execute(
                "SELECT * FROM openings WHERE opening_id = ?", (opening_id,)
            ).fetchone()
        ) or {}


def save_opening(
    title: str,
    description: str = "",
    requirements: list[str] | None = None,
    preferred_skills: list[str] | None = None,
    minimum_education: str | None = None,
    minimum_years_experience: float | None = None,
    opening_id: str | None = None,
    status: str = "OPEN",
    **kwargs: Any,
) -> dict[str, Any]:
    return create_opening({
        "opening_id": opening_id or _generate_id("op"),
        "title": title,
        "description": description,
        "required_skills": requirements or [],
        "preferred_skills": preferred_skills or [],
        "minimum_education": minimum_education,
        "minimum_years_experience": minimum_years_experience,
        "status": status,
        **kwargs,
    })


def list_openings(status: str | None = None) -> list[dict[str, Any]]:
    with _connection() as connection:
        if status:
            rows = connection.execute(
                "SELECT * FROM openings WHERE status = ? ORDER BY created_at",
                (status,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM openings ORDER BY created_at"
            ).fetchall()
        return [_opening(row) or {} for row in rows]


def get_opening(opening_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        return _opening(
            connection.execute(
                "SELECT * FROM openings WHERE opening_id = ?", (opening_id,)
            ).fetchone()
        )


def update_opening(opening_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    allowed_fields = {
        "title",
        "description",
        "required_skills",
        "preferred_skills",
        "minimum_education",
        "minimum_years_experience",
        "status",
    }
    updates = {key: value for key, value in data.items() if key in allowed_fields}
    if not updates:
        return get_opening(opening_id)
    updates["updated_at"] = _now()
    with _connection() as connection:
        current = connection.execute(
            """
            SELECT title, description, required_skills, preferred_skills,
                   minimum_education, minimum_years_experience
            FROM openings WHERE opening_id = ?
            """,
            (opening_id,),
        ).fetchone()
        if current is None:
            return None
        required_skills_changed = (
            "required_skills" in updates
            and json.loads(current["required_skills"])
            != updates["required_skills"]
        )
        scoring_inputs_changed = required_skills_changed or any(
            key in updates
            and (
                json.loads(current[key])
                if key == "preferred_skills"
                else current[key]
            )
            != updates[key]
            for key in (
                "title",
                "description",
                "preferred_skills",
                "minimum_education",
                "minimum_years_experience",
            )
        )
        for key in ("required_skills", "preferred_skills"):
            if key in updates:
                updates[key] = json.dumps(updates[key])
        assignments = ", ".join(f"{key} = ?" for key in updates)
        connection.execute(
            f"UPDATE openings SET {assignments} WHERE opening_id = ?",
            (*updates.values(), opening_id),
        )
        if scoring_inputs_changed:
            connection.execute(
                """
                UPDATE candidates
                SET score = NULL, score_evidence = NULL, updated_at = ?
                WHERE opening_id = ?
                """,
                (_now(), opening_id),
            )
        return _opening(
            connection.execute(
                "SELECT * FROM openings WHERE opening_id = ?", (opening_id,)
            ).fetchone()
        )


def delete_opening(opening_id: str) -> bool:
    with _connection() as connection:
        candidate_ids = [
            row["candidate_id"]
            for row in connection.execute(
                "SELECT candidate_id FROM candidates WHERE opening_id = ?",
                (opening_id,),
            ).fetchall()
        ]
        _redact_candidate_processing_jobs(connection, candidate_ids)
        cursor = connection.execute(
            "DELETE FROM openings WHERE opening_id = ?", (opening_id,)
        )
        return cursor.rowcount > 0


def create_candidate(data: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
    payload = dict(data) if data is not None else kwargs
    candidate_id = payload.get("candidate_id") or _generate_id("cand")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO candidates (
                candidate_id, name, email, opening_id, skills, resume_text,
                resume_data, location, relocation_willingness,
                work_mode_preference, availability_date, application_status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, '{}', ?, ?, ?, ?, 'APPLIED', ?, ?)
            """,
            (
                candidate_id,
                payload["name"],
                payload.get("email"),
                payload["opening_id"],
                json.dumps(payload.get("skills", [])),
                payload.get("resume_text", ""),
                payload.get("location"),
                (
                    int(payload["relocation_willingness"])
                    if payload.get("relocation_willingness") is not None
                    else None
                ),
                payload.get("work_mode_preference"),
                payload.get("availability_date"),
                now,
                now,
            ),
        )
        return _candidate(
            connection.execute(
                "SELECT * FROM candidates WHERE candidate_id = ?",
                (candidate_id,),
            ).fetchone()
        ) or {}


def list_candidates(
    opening_id: str | None = None,
    application_status: str | None = None,
) -> list[dict[str, Any]]:
    conditions = []
    parameters: list[str] = []
    if opening_id:
        conditions.append("opening_id = ?")
        parameters.append(opening_id)
    if application_status:
        conditions.append("application_status = ?")
        parameters.append(application_status)
    where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    with _connection() as connection:
        rows = connection.execute(
            f"SELECT * FROM candidates{where_clause} ORDER BY created_at",
            parameters,
        ).fetchall()
        return [_candidate(row) or {} for row in rows]


def get_candidate(candidate_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        return _candidate(
            connection.execute(
                "SELECT * FROM candidates WHERE candidate_id = ?",
                (candidate_id,),
            ).fetchone()
        )


def update_candidate(
    candidate_id: str, data: dict[str, Any]
) -> dict[str, Any] | None:
    allowed_fields = {
        "name",
        "email",
        "skills",
        "application_status",
        "location",
        "relocation_willingness",
        "work_mode_preference",
        "availability_date",
    }
    updates = {key: value for key, value in data.items() if key in allowed_fields}
    if not updates:
        return get_candidate(candidate_id)
    updates["updated_at"] = _now()
    with _connection() as connection:
        if "skills" in updates:
            current = connection.execute(
                "SELECT skills FROM candidates WHERE candidate_id = ?",
                (candidate_id,),
            ).fetchone()
            if current is None:
                return None
            skills_changed = json.loads(current["skills"]) != updates["skills"]
            updates["skills"] = json.dumps(updates["skills"])
            if skills_changed:
                updates["score"] = None
                updates["score_evidence"] = None
        if "name" in updates:
            current_name = connection.execute(
                "SELECT name FROM candidates WHERE candidate_id = ?",
                (candidate_id,),
            ).fetchone()
            if current_name is None:
                return None
            if current_name["name"] != updates["name"]:
                updates["score"] = None
                updates["score_evidence"] = None
        if "relocation_willingness" in updates and updates["relocation_willingness"] is not None:
            updates["relocation_willingness"] = int(updates["relocation_willingness"])
        assignments = ", ".join(f"{key} = ?" for key in updates)
        connection.execute(
            f"UPDATE candidates SET {assignments} WHERE candidate_id = ?",
            (*updates.values(), candidate_id),
        )
        return _candidate(
            connection.execute(
                "SELECT * FROM candidates WHERE candidate_id = ?",
                (candidate_id,),
            ).fetchone()
        )


def save_candidate_resume(
    candidate_id: str,
    filename: str,
    parsed_text: str,
    resume_data: dict[str, Any],
) -> bool:
    with _connection() as connection:
        cursor = connection.execute(
            """
            UPDATE candidates
            SET resume_filename = ?, resume_text = ?, resume_data = ?,
                score = NULL, score_evidence = NULL, updated_at = ?
            WHERE candidate_id = ?
            """,
            (
                filename,
                parsed_text,
                json.dumps(resume_data),
                _now(),
                candidate_id,
            ),
        )
        return cursor.rowcount > 0


def save_candidate_score(
    candidate_id: str, score: float, evidence: dict[str, Any]
) -> bool:
    with _connection() as connection:
        cursor = connection.execute(
            """
            UPDATE candidates
            SET score = ?, score_evidence = ?, updated_at = ?
            WHERE candidate_id = ?
            """,
            (score, json.dumps(evidence), _now(), candidate_id),
        )
        return cursor.rowcount > 0


def delete_candidate(candidate_id: str) -> bool:
    with _connection() as connection:
        _redact_candidate_processing_jobs(connection, [candidate_id])
        cursor = connection.execute(
            "DELETE FROM candidates WHERE candidate_id = ?", (candidate_id,)
        )
        return cursor.rowcount > 0


def save_screening_report(report: dict[str, Any]) -> None:
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO screening_reports (
                report_id, candidate_id, opening_id, report_json, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                report["report_id"],
                report["candidate_id"],
                report["opening_id"],
                json.dumps(report),
                report["created_at"],
            ),
        )


def list_screening_reports(candidate_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT report_json FROM screening_reports
            WHERE candidate_id = ?
            ORDER BY created_at DESC
            """,
            (candidate_id,),
        ).fetchall()
        return [json.loads(row["report_json"]) for row in rows]


def create_processing_job(
    job_id: str, filename: str, candidate_id: str | None
) -> None:
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO processing_jobs (
                job_id, filename, candidate_id, status, created_at
            ) VALUES (?, ?, ?, 'QUEUED', ?)
            """,
            (job_id, filename, candidate_id, _now()),
        )


def update_processing_job(
    job_id: str,
    status: str,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> bool:
    with _connection() as connection:
        if result is not None and result.get("candidate_id") is not None:
            candidate_exists = connection.execute(
                "SELECT 1 FROM candidates WHERE candidate_id = ?",
                (result["candidate_id"],),
            ).fetchone()
            if candidate_exists is None:
                status = "FAILED"
                result = None
                error = "The candidate record was removed before resume processing completed."
        cursor = connection.execute(
            """
            UPDATE processing_jobs
            SET status = ?, result = ?, error = ?
            WHERE job_id = ?
            """,
            (
                status,
                json.dumps(result) if result is not None else None,
                error,
                job_id,
            ),
        )
        return cursor.rowcount > 0


def get_processing_job(job_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM processing_jobs WHERE job_id = ?", (job_id,)
        ).fetchone()
        if row is None:
            return None
        record = dict(row)
        record["result"] = (
            json.loads(record["result"]) if record["result"] is not None else None
        )
        return record


def save_eligibility_configuration(
    opening_id: str, configuration: dict[str, Any]
) -> dict[str, Any] | None:
    now = _now()
    with _connection() as connection:
        current = connection.execute(
            "SELECT version, created_at FROM eligibility_configurations WHERE opening_id = ?",
            (opening_id,),
        ).fetchone()
        version = current["version"] + 1 if current else 1
        created_at = current["created_at"] if current else now
        connection.execute(
            """
            INSERT INTO eligibility_configurations (
                opening_id, version, configuration_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(opening_id) DO UPDATE SET
                version = excluded.version,
                configuration_json = excluded.configuration_json,
                updated_at = excluded.updated_at
            """,
            (opening_id, version, json.dumps(configuration), created_at, now),
        )
        return {
            "opening_id": opening_id,
            "version": version,
            "configuration": configuration,
            "created_at": created_at,
            "updated_at": now,
        }


def get_eligibility_configuration(opening_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM eligibility_configurations WHERE opening_id = ?",
            (opening_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "opening_id": row["opening_id"],
            "version": row["version"],
            "configuration": json.loads(row["configuration_json"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


def save_eligibility_evaluation(
    evaluation: dict[str, Any], input_fingerprint: str
) -> None:
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO eligibility_evaluations (
                evaluation_id, candidate_id, opening_id, configuration_version,
                input_fingerprint, result_json, evaluated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation["evaluation_id"],
                evaluation["candidate_id"],
                evaluation["opening_id"],
                evaluation["configuration_version"],
                input_fingerprint,
                json.dumps(evaluation),
                evaluation["evaluated_at"],
            ),
        )


def get_latest_eligibility_evaluation(
    candidate_id: str, opening_id: str
) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            """
            SELECT result_json, input_fingerprint
            FROM eligibility_evaluations
            WHERE candidate_id = ? AND opening_id = ?
            ORDER BY evaluated_at DESC LIMIT 1
            """,
            (candidate_id, opening_id),
        ).fetchone()
        if row is None:
            return None
        result = json.loads(row["result_json"])
        result["_input_fingerprint"] = row["input_fingerprint"]
        return result


def save_candidate_eligibility_evaluation(
    candidate_id: str,
    opening_id: str,
    eligibility_status: str = "ELIGIBLE",
    failed_thresholds: list[str] | None = None,
    missing_information: list[str] | None = None,
    details: dict[str, Any] | None = None,
    evaluation_id: str | None = None,
) -> dict[str, Any]:
    evaluation_id = evaluation_id or _generate_id("eval")
    now = _now()
    eval_dict = {
        "evaluation_id": evaluation_id,
        "candidate_id": candidate_id,
        "opening_id": opening_id,
        "eligibility_status": eligibility_status,
        "is_eligible": eligibility_status == "ELIGIBLE",
        "failed_thresholds": failed_thresholds or [],
        "missing_information": missing_information or [],
        "details": details or {},
        "configuration_version": "v1",
        "evaluated_at": now,
    }
    fingerprint = hashlib.sha256(f"{candidate_id}:{opening_id}:{now}".encode()).hexdigest()
    save_eligibility_evaluation(eval_dict, fingerprint)
    return eval_dict


def get_candidate_eligibility_evaluation(
    candidate_id: str, opening_id: str | None = None
) -> dict[str, Any] | None:
    with _connection() as connection:
        if opening_id:
            row = connection.execute(
                """
                SELECT result_json, input_fingerprint
                FROM eligibility_evaluations
                WHERE candidate_id = ? AND opening_id = ?
                ORDER BY evaluated_at DESC LIMIT 1
                """,
                (candidate_id, opening_id),
            ).fetchone()
        else:
            row = connection.execute(
                """
                SELECT result_json, input_fingerprint
                FROM eligibility_evaluations
                WHERE candidate_id = ?
                ORDER BY evaluated_at DESC LIMIT 1
                """,
                (candidate_id,),
            ).fetchone()
        if row is None:
            return None
        result = json.loads(row["result_json"])
        result["_input_fingerprint"] = row["input_fingerprint"]
        return result


def create_screening_session(session: dict[str, Any]) -> dict[str, Any]:
    now = _now()
    started_at = session.get("started_at") or now
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO screening_sessions (
                session_id, candidate_id, opening_id, status, language,
                started_at, completed_at, source, version, created_at, updated_at
            ) VALUES (?, ?, ?, 'CREATED', ?, ?, NULL, ?, 1, ?, ?)
            """,
            (
                session["session_id"],
                session["candidate_id"],
                session["opening_id"],
                session["language"],
                started_at,
                session["source"],
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM screening_sessions WHERE session_id = ?",
            (session["session_id"],),
        ).fetchone()
        return dict(row) if row is not None else {}


def get_screening_session(session_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM screening_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return dict(row) if row is not None else None


def list_screening_sessions(candidate_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM screening_sessions
            WHERE candidate_id = ? ORDER BY created_at DESC
            """,
            (candidate_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def update_screening_session_status(session_id: str, status: str) -> dict[str, Any] | None:
    now = _now()
    completed_at = now if status in {"COMPLETED", "CANCELLED"} else None
    with _connection() as connection:
        connection.execute(
            """
            UPDATE screening_sessions
            SET status = ?, completed_at = ?, version = version + 1, updated_at = ?
            WHERE session_id = ?
            """,
            (status, completed_at, now, session_id),
        )
        row = connection.execute(
            "SELECT * FROM screening_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return dict(row) if row is not None else None


def save_screening_session_full(
    candidate_id: str,
    opening_id: str,
    overall_score: float = 85.0,
    status: str = "COMPLETED",
    summary_notes: str = "",
    session_id: str | None = None,
) -> dict[str, Any]:
    session_id = session_id or _generate_id("scr_sess")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO screening_sessions (
                session_id, candidate_id, opening_id, status,
                language, started_at, completed_at, source, version,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'en', ?, ?, 'api', 1, ?, ?)
            """,
            (session_id, candidate_id, opening_id, status, now, now, now, now),
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO screening_aggregate_scores (
                aggregate_id, session_id, candidate_id, overall_score,
                score_status, questions_evaluated, questions_answered, questions_missing,
                human_review_required, scoring_version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'FINAL', 5, 5, 0, 0, 'v1', ?, ?)
            """,
            (_generate_id("agg"), session_id, candidate_id, overall_score, now, now),
        )
    return {
        "session_id": session_id,
        "candidate_id": candidate_id,
        "opening_id": opening_id,
        "status": status,
        "overall_score": overall_score,
        "summary_notes": summary_notes,
    }


list_screening_sessions_for_candidate = list_screening_sessions


def save_transcript_segments(
    session_id: str, segments: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    now = _now()
    with _connection() as connection:
        for segment in segments:
            raw_text = segment["text"]
            normalized = " ".join(raw_text.split())
            connection.execute(
                """
                INSERT INTO transcript_segments (
                    segment_id, session_id, question_id, speaker, raw_text,
                    normalized_text, start_time, end_time, confidence, language,
                    source, processing_version, sequence_number, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'transcript-v1', ?, ?, ?)
                """,
                (
                    segment["segment_id"],
                    session_id,
                    segment.get("question_id"),
                    segment["speaker"],
                    raw_text,
                    normalized,
                    segment.get("start_time"),
                    segment.get("end_time"),
                    segment.get("confidence"),
                    segment.get("language"),
                    segment["source"],
                    segment["sequence_number"],
                    now,
                    now,
                ),
            )
        rows = connection.execute(
            """
            SELECT * FROM transcript_segments
            WHERE session_id = ? ORDER BY sequence_number
            """,
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def list_transcript_segments(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM transcript_segments
            WHERE session_id = ? ORDER BY sequence_number
            """,
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def save_screening_interaction(
    session_id: str, interaction: dict[str, Any]
) -> dict[str, Any]:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO screening_interactions (
                interaction_id, session_id, question_id, candidate_answer,
                answer_type, validation_status, display_order, follow_up_to,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                interaction["interaction_id"],
                session_id,
                interaction["question_id"],
                interaction.get("candidate_answer"),
                interaction.get("answer_type"),
                interaction["validation_status"],
                interaction["display_order"],
                interaction.get("follow_up_to"),
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM screening_interactions WHERE interaction_id = ?",
            (interaction["interaction_id"],),
        ).fetchone()
        return dict(row) if row is not None else {}


def list_screening_interactions(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM screening_interactions
            WHERE session_id = ? ORDER BY display_order
            """,
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def save_screening_audio(
    session_id: str, audio: dict[str, Any]
) -> dict[str, Any]:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO screening_audio (
                audio_id, session_id, question_id, file_path, file_size_bytes,
                duration_seconds, mime_type, source, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?, ?)
            """,
            (
                audio["audio_id"],
                session_id,
                audio.get("question_id"),
                audio["file_path"],
                audio["file_size_bytes"],
                audio.get("duration_seconds"),
                audio["mime_type"],
                audio["source"],
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM screening_audio WHERE audio_id = ?", (audio["audio_id"],)
        ).fetchone()
        return dict(row) if row is not None else {}


def update_screening_audio_status(
    audio_id: str, status: str
) -> dict[str, Any] | None:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            UPDATE screening_audio
            SET status = ?, updated_at = ?
            WHERE audio_id = ?
            """,
            (status, now, audio_id),
        )
        row = connection.execute(
            "SELECT * FROM screening_audio WHERE audio_id = ?", (audio_id,)
        ).fetchone()
        return dict(row) if row is not None else None


def get_screening_audio(audio_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM screening_audio WHERE audio_id = ?", (audio_id,)
        ).fetchone()
        return dict(row) if row is not None else None


def save_screening_transcript(
    session_id: str, transcript: dict[str, Any]
) -> dict[str, Any]:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO screening_transcripts (
                transcript_id, session_id, audio_id, question_id, raw_text,
                cleaned_text, language, language_probability, partial_answer,
                processing_version, segment_count, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transcript["transcript_id"],
                session_id,
                transcript.get("audio_id"),
                transcript.get("question_id"),
                transcript["raw_text"],
                transcript["cleaned_text"],
                transcript.get("language"),
                transcript.get("language_probability"),
                1 if transcript.get("partial_answer") else 0,
                transcript["processing_version"],
                transcript.get("segment_count", 0),
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM screening_transcripts WHERE transcript_id = ?",
            (transcript["transcript_id"],),
        ).fetchone()
        return dict(row) if row is not None else {}


def get_screening_transcript(transcript_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM screening_transcripts WHERE transcript_id = ?",
            (transcript_id,),
        ).fetchone()
        return dict(row) if row is not None else None


def list_screening_transcripts(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM screening_transcripts
            WHERE session_id = ? ORDER BY created_at
            """,
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def save_screening_answer(
    session_id: str, answer: dict[str, Any]
) -> dict[str, Any]:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO screening_answers (
                answer_id, session_id, transcript_id, question_id, question_text,
                expected_intent, detected_intent, answer_status, raw_answer,
                cleaned_answer, extracted_information, intent_confidence,
                needs_clarification, is_off_topic, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                answer["answer_id"],
                session_id,
                answer.get("transcript_id"),
                answer["question_id"],
                answer["question_text"],
                answer["expected_intent"],
                answer.get("detected_intent"),
                answer["answer_status"],
                answer["raw_answer"],
                answer["cleaned_answer"],
                json.dumps(answer.get("extracted_information", {})),
                answer.get("intent_confidence"),
                1 if answer.get("needs_clarification") else 0,
                1 if answer.get("is_off_topic") else 0,
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM screening_answers WHERE answer_id = ?",
            (answer["answer_id"],),
        ).fetchone()
        if row is None:
            return {}
        rec = dict(row)
        if isinstance(rec.get("extracted_information"), str):
            try:
                rec["extracted_information"] = json.loads(rec["extracted_information"])
            except Exception:
                rec["extracted_information"] = {}
        return rec


def get_screening_answer(answer_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM screening_answers WHERE answer_id = ?", (answer_id,)
        ).fetchone()
        if row is None:
            return None
        rec = dict(row)
        if isinstance(rec.get("extracted_information"), str):
            try:
                rec["extracted_information"] = json.loads(rec["extracted_information"])
            except Exception:
                rec["extracted_information"] = {}
        return rec


def list_screening_answers(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM screening_answers
            WHERE session_id = ? ORDER BY created_at
            """,
            (session_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            if isinstance(rec.get("extracted_information"), str):
                try:
                    rec["extracted_information"] = json.loads(rec["extracted_information"])
                except Exception:
                    rec["extracted_information"] = {}
            results.append(rec)
        return results


def save_screening_question_score(
    session_id: str, score: dict[str, Any]
) -> dict[str, Any]:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO screening_question_scores (
                score_id, session_id, answer_id, question_id, clarity_score,
                relevance_score, completeness_score, consistency_score,
                weighted_score, normalized_score, explanation,
                human_review_required, scoring_version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                score["score_id"],
                session_id,
                score["answer_id"],
                score["question_id"],
                score["clarity_score"],
                score["relevance_score"],
                score["completeness_score"],
                score["consistency_score"],
                score["weighted_score"],
                score["normalized_score"],
                score["explanation"],
                1 if score.get("human_review_required") else 0,
                score["scoring_version"],
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM screening_question_scores WHERE score_id = ?",
            (score["score_id"],),
        ).fetchone()
        return dict(row) if row is not None else {}


def get_screening_question_score(score_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM screening_question_scores WHERE score_id = ?",
            (score_id,),
        ).fetchone()
        return dict(row) if row is not None else None


def list_screening_question_scores(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM screening_question_scores
            WHERE session_id = ? ORDER BY created_at
            """,
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def save_screening_aggregate_score(
    aggregate: dict[str, Any]
) -> dict[str, Any]:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO screening_aggregate_scores (
                aggregate_id, session_id, candidate_id, overall_score,
                score_status, questions_evaluated, questions_answered,
                questions_missing, human_review_required, scoring_version,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                aggregate["aggregate_id"],
                aggregate["session_id"],
                aggregate["candidate_id"],
                aggregate["overall_score"],
                aggregate["score_status"],
                aggregate["questions_evaluated"],
                aggregate["questions_answered"],
                aggregate["questions_missing"],
                1 if aggregate.get("human_review_required") else 0,
                aggregate["scoring_version"],
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM screening_aggregate_scores WHERE aggregate_id = ?",
            (aggregate["aggregate_id"],),
        ).fetchone()
        return dict(row) if row is not None else {}


def get_screening_aggregate_score(session_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            """
            SELECT * FROM screening_aggregate_scores
            WHERE session_id = ? ORDER BY created_at DESC LIMIT 1
            """,
            (session_id,),
        ).fetchone()
        return dict(row) if row is not None else None


def save_behavioral_analysis(
    session_id: str, analysis: dict[str, Any]
) -> dict[str, Any]:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO behavioral_analysis (
                analysis_id, session_id, answer_id, sentiment, sentiment_score,
                confidence_score, hesitation_count, uncertainty_count,
                contradiction_detected, contradiction_details,
                response_length_category, words_per_minute, pace_category,
                processing_version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis["analysis_id"],
                session_id,
                analysis.get("answer_id"),
                analysis.get("sentiment"),
                analysis.get("sentiment_score"),
                analysis.get("confidence_score"),
                analysis.get("hesitation_count", 0),
                analysis.get("uncertainty_count", 0),
                1 if analysis.get("contradiction_detected") else 0,
                analysis.get("contradiction_details"),
                analysis.get("response_length_category"),
                analysis.get("words_per_minute"),
                analysis.get("pace_category"),
                analysis["processing_version"],
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM behavioral_analysis WHERE analysis_id = ?",
            (analysis["analysis_id"],),
        ).fetchone()
        return dict(row) if row is not None else {}


def get_behavioral_analysis(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM behavioral_analysis
            WHERE session_id = ? ORDER BY created_at
            """,
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def save_screening_report_full(
    session_id: str, report: dict[str, Any]
) -> dict[str, Any]:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO screening_reports_full (
                report_id, session_id, candidate_id, opening_id, report_json,
                html_report, pdf_report, version, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'COMPLETED', ?, ?)
            """,
            (
                report["report_id"],
                session_id,
                report["candidate_id"],
                report["opening_id"],
                json.dumps(report.get("report_json", report)),
                report.get("html_report"),
                report.get("pdf_report"),
                now,
                now,
            ),
        )
        row = connection.execute(
            "SELECT * FROM screening_reports_full WHERE report_id = ?",
            (report["report_id"],),
        ).fetchone()
        if row is None:
            return {}
        record = dict(row)
        if isinstance(record.get("report_json"), str):
            try:
                record["report_json"] = json.loads(record["report_json"])
            except Exception:
                pass
        return record


def get_screening_report_full(report_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM screening_reports_full WHERE report_id = ?",
            (report_id,),
        ).fetchone()
        if row is None:
            return None
        record = dict(row)
        record["report_json"] = json.loads(record["report_json"])
        return record


def list_screening_reports_full(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM screening_reports_full
            WHERE session_id = ? ORDER BY created_at DESC
            """,
            (session_id,),
        ).fetchall()
        results = []
        for row in rows:
            record = dict(row)
            record["report_json"] = json.loads(record["report_json"])
            results.append(record)
        return results


# ---------------------------------------------------------------------------
# Days 33–40: AI HR Interview Database Functions
# ---------------------------------------------------------------------------


def create_hr_interview(
    session_data: dict[str, Any] | None = None,
    candidate_id: str | None = None,
    opening_id: str | None = None,
    candidate_experience_level: str = "mid",
    overall_score: float | None = None,
    status: str = "COMPLETED",
    **kwargs: Any,
) -> dict[str, Any]:
    if isinstance(session_data, dict):
        payload = dict(session_data)
    else:
        payload = {
            "candidate_id": candidate_id,
            "opening_id": opening_id,
            "experience_level": candidate_experience_level,
            "status": status,
            **kwargs,
        }
    sess = create_hr_interview_session(payload)
    if overall_score is not None:
        save_hr_interview_score({
            "interview_id": sess["interview_id"],
            "candidate_id": sess["candidate_id"],
            "relevance_score": 85.0,
            "communication_score": 85.0,
            "confidence_score": 85.0,
            "consistency_score": 85.0,
            "overall_hr_score": float(overall_score),
            "score_status": "FINAL",
            "breakdown": {},
            "human_review_required": 0,
        })
    return sess


def create_hr_interview_session(session_data: dict[str, Any]) -> dict[str, Any]:
    now = _now()
    interview_id = session_data.get("interview_id") or _generate_id("hr_int")

    exp_level = str(session_data.get("experience_level", "FRESHER")).upper()
    if exp_level not in ("FRESHER", "EXPERIENCED"):
        exp_level = "EXPERIENCED" if any(k in exp_level for k in ("EXP", "MID", "SENIOR", "LEAD")) else "FRESHER"

    role_type = str(session_data.get("role_type", "NON_TECHNICAL")).upper()
    if role_type not in ("TECHNICAL", "NON_TECHNICAL"):
        role_type = "TECHNICAL" if "TECH" in role_type else "NON_TECHNICAL"

    status = str(session_data.get("status", "CREATED")).upper()
    if status not in ("CREATED", "IN_PROGRESS", "PAUSED", "COMPLETED", "CANCELLED", "FAILED"):
        status = "CREATED"

    current_phase = str(session_data.get("current_phase", "CREATED")).upper()
    if current_phase not in ("CREATED", "INTRODUCTION", "CORE_HR_QUESTIONS", "ROLE_BASED_EVALUATION", "CLOSING", "COMPLETED"):
        current_phase = "COMPLETED" if status == "COMPLETED" else "CREATED"

    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO hr_interview_sessions (
                interview_id, candidate_id, opening_id, status,
                current_phase, current_question_id, experience_level,
                role_type, recruiter_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                interview_id,
                session_data["candidate_id"],
                session_data["opening_id"],
                status,
                current_phase,
                session_data.get("current_question_id"),
                exp_level,
                role_type,
                session_data.get("recruiter_id"),
                now,
                now,
            ),
        )
    return get_hr_interview_session(interview_id)  # type: ignore[return-value]


def get_hr_interview_session(interview_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM hr_interview_sessions WHERE interview_id = ?",
            (interview_id,),
        ).fetchone()
        return dict(row) if row else None


def list_hr_interview_sessions(
    candidate_id: str | None = None, status: str | None = None
) -> list[dict[str, Any]]:
    with _connection() as connection:
        query = "SELECT * FROM hr_interview_sessions WHERE 1=1"
        params: list[Any] = []
        if candidate_id:
            query += " AND candidate_id = ?"
            params.append(candidate_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        rows = connection.execute(query, params).fetchall()
        return [dict(r) for r in rows]


list_hr_interviews = list_hr_interview_sessions


def update_hr_interview_session_status(
    interview_id: str,
    status: str | None = None,
    current_phase: str | None = None,
    current_question_id: str | None = None,
) -> dict[str, Any] | None:
    now = _now()
    fields = ["updated_at = ?"]
    params: list[Any] = [now]
    if status is not None:
        fields.append("status = ?")
        params.append(status)
    if current_phase is not None:
        fields.append("current_phase = ?")
        params.append(current_phase)
    if current_question_id is not None:
        fields.append("current_question_id = ?")
        params.append(current_question_id)
    params.append(interview_id)

    with _connection() as connection:
        connection.execute(
            f"UPDATE hr_interview_sessions SET {', '.join(fields)} WHERE interview_id = ?",
            params,
        )
    return get_hr_interview_session(interview_id)


def save_hr_interview_question(
    interview_id: str, question: dict[str, Any]
) -> dict[str, Any]:
    question_id = question.get("question_id") or _generate_id("hr_q")
    now = _now()
    eval_params = question.get("evaluation_parameters")
    if isinstance(eval_params, (dict, list)):
        eval_params_str = json.dumps(eval_params)
    else:
        eval_params_str = eval_params or "{}"

    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO hr_interview_questions (
                question_id, interview_id, category, question_text,
                role_type, experience_level, difficulty, expected_answer_criteria,
                evaluation_parameters, follow_up_eligibility, question_order,
                active_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question_id,
                interview_id,
                question.get("category", "General"),
                question.get("question_text", ""),
                question.get("role_type", "NON_TECHNICAL"),
                question.get("experience_level", "FRESHER"),
                question.get("difficulty", "simple"),
                question.get("expected_answer_criteria"),
                eval_params_str,
                1 if question.get("follow_up_eligibility", True) else 0,
                question.get("question_order", 0),
                1 if question.get("active_status", True) else 0,
                now,
            ),
        )
    return {
        "question_id": question_id,
        "interview_id": interview_id,
        "category": question.get("category", "General"),
        "question_text": question.get("question_text", ""),
        "role_type": question.get("role_type", "NON_TECHNICAL"),
        "experience_level": question.get("experience_level", "FRESHER"),
        "difficulty": question.get("difficulty", "simple"),
        "expected_answer_criteria": question.get("expected_answer_criteria"),
        "evaluation_parameters": eval_params if isinstance(eval_params, (dict, list)) else {},
        "follow_up_eligibility": question.get("follow_up_eligibility", True),
        "question_order": question.get("question_order", 0),
        "active_status": question.get("active_status", True),
        "created_at": now,
    }


def list_hr_interview_questions(interview_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM hr_interview_questions WHERE interview_id = ? ORDER BY question_order ASC",
            (interview_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["follow_up_eligibility"] = bool(rec["follow_up_eligibility"])
            rec["active_status"] = bool(rec["active_status"])
            try:
                rec["evaluation_parameters"] = json.loads(rec.get("evaluation_parameters") or "{}")
            except Exception:
                rec["evaluation_parameters"] = {}
            results.append(rec)
        return results


def save_hr_interview_response(
    interview_id: str, response_data: dict[str, Any]
) -> dict[str, Any]:
    response_id = response_data.get("response_id") or _generate_id("hr_resp")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO hr_interview_responses (
                response_id, interview_id, question_id, raw_response,
                cleaned_response, quality, follow_up_eligible, follow_up_count,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                response_id,
                interview_id,
                response_data["question_id"],
                response_data.get("raw_response", ""),
                response_data.get("cleaned_response", ""),
                response_data.get("quality", "complete"),
                1 if response_data.get("follow_up_eligible", True) else 0,
                response_data.get("follow_up_count", 0),
                now,
                now,
            ),
        )
    return {
        "response_id": response_id,
        "interview_id": interview_id,
        "question_id": response_data["question_id"],
        "raw_response": response_data.get("raw_response", ""),
        "cleaned_response": response_data.get("cleaned_response", ""),
        "quality": response_data.get("quality", "complete"),
        "follow_up_eligible": response_data.get("follow_up_eligible", True),
        "follow_up_count": response_data.get("follow_up_count", 0),
        "created_at": now,
        "updated_at": now,
    }


def list_hr_interview_responses(interview_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM hr_interview_responses WHERE interview_id = ? ORDER BY created_at ASC",
            (interview_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["follow_up_eligible"] = bool(rec["follow_up_eligible"])
            results.append(rec)
        return results


def save_hr_interview_followup(
    interview_id: str, followup_data: dict[str, Any]
) -> dict[str, Any]:
    followup_id = followup_data.get("followup_id") or _generate_id("hr_fup")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO hr_interview_followups (
                followup_id, interview_id, parent_question_id,
                followup_type, followup_question, candidate_response,
                difficulty_level, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                followup_id,
                interview_id,
                followup_data["parent_question_id"],
                followup_data.get("followup_type", "clarification"),
                followup_data.get("followup_question", ""),
                followup_data.get("candidate_response"),
                followup_data.get("difficulty_level", "simple"),
                now,
                now,
            ),
        )
    return {
        "followup_id": followup_id,
        "interview_id": interview_id,
        "parent_question_id": followup_data["parent_question_id"],
        "followup_type": followup_data.get("followup_type", "clarification"),
        "followup_question": followup_data.get("followup_question", ""),
        "candidate_response": followup_data.get("candidate_response"),
        "difficulty_level": followup_data.get("difficulty_level", "simple"),
        "created_at": now,
        "updated_at": now,
    }


def list_hr_interview_followups(interview_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM hr_interview_followups WHERE interview_id = ? ORDER BY created_at ASC",
            (interview_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def save_hr_communication_evaluation(
    interview_id: str, eval_data: dict[str, Any]
) -> dict[str, Any]:
    evaluation_id = eval_data.get("evaluation_id") or _generate_id("hr_comm")
    now = _now()
    fillers = eval_data.get("fillers_detected", [])
    evidence = eval_data.get("evidence", [])
    fillers_str = json.dumps(fillers) if isinstance(fillers, list) else str(fillers)
    evidence_str = json.dumps(evidence) if isinstance(evidence, (list, dict)) else str(evidence)

    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO hr_communication_evaluations (
                evaluation_id, interview_id, response_id, fluency_score,
                grammar_score, vocabulary_score, clarity_score, structure_score,
                filler_control_score, total_communication_score, fillers_detected,
                evidence, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation_id,
                interview_id,
                eval_data.get("response_id"),
                eval_data.get("fluency_score", 0.0),
                eval_data.get("grammar_score", 0.0),
                eval_data.get("vocabulary_score", 0.0),
                eval_data.get("clarity_score", 0.0),
                eval_data.get("structure_score", 0.0),
                eval_data.get("filler_control_score", 0.0),
                eval_data.get("total_communication_score", 0.0),
                fillers_str,
                evidence_str,
                now,
            ),
        )
    return {
        "evaluation_id": evaluation_id,
        "interview_id": interview_id,
        "response_id": eval_data.get("response_id"),
        "fluency_score": eval_data.get("fluency_score", 0.0),
        "grammar_score": eval_data.get("grammar_score", 0.0),
        "vocabulary_score": eval_data.get("vocabulary_score", 0.0),
        "clarity_score": eval_data.get("clarity_score", 0.0),
        "structure_score": eval_data.get("structure_score", 0.0),
        "filler_control_score": eval_data.get("filler_control_score", 0.0),
        "total_communication_score": eval_data.get("total_communication_score", 0.0),
        "fillers_detected": fillers if isinstance(fillers, list) else [],
        "evidence": evidence if isinstance(evidence, (list, dict)) else [],
        "created_at": now,
    }


def get_hr_communication_evaluations(interview_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM hr_communication_evaluations WHERE interview_id = ? ORDER BY created_at ASC",
            (interview_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            try:
                rec["fillers_detected"] = json.loads(rec.get("fillers_detected") or "[]")
            except Exception:
                rec["fillers_detected"] = []
            try:
                rec["evidence"] = json.loads(rec.get("evidence") or "[]")
            except Exception:
                rec["evidence"] = []
            results.append(rec)
        return results


def get_hr_communication_evaluation(
    interview_id: str, response_id: str | None = None
) -> dict[str, Any] | None:
    evals = get_hr_communication_evaluations(interview_id)
    if not evals:
        return None
    if response_id:
        for e in evals:
            if e.get("response_id") == response_id:
                return e
        return None
    return evals[-1]


def save_hr_behavioral_signals(
    interview_id: str, signals_data: dict[str, Any]
) -> dict[str, Any]:
    signal_id = signals_data.get("signal_id") or _generate_id("hr_sig")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO hr_behavioral_signals (
                signal_id, interview_id, response_id, hesitation_count,
                pause_count, uncertainty_count, repeated_word_count,
                sentiment, sentiment_score, stress_score, confidence_score,
                contradiction_detected, contradiction_reason, disclaimer, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                signal_id,
                interview_id,
                signals_data.get("response_id"),
                signals_data.get("hesitation_count", 0),
                signals_data.get("pause_count", 0),
                signals_data.get("uncertainty_count", 0),
                signals_data.get("repeated_word_count", 0),
                signals_data.get("sentiment", "NEUTRAL"),
                signals_data.get("sentiment_score", 0.0),
                signals_data.get("stress_score", 0.0),
                signals_data.get("confidence_score", 0.0),
                1 if signals_data.get("contradiction_detected", False) else 0,
                signals_data.get("contradiction_reason"),
                signals_data.get("disclaimer", "Behavioral signals are assistive and non-binding."),
                now,
            ),
        )
    return {
        "signal_id": signal_id,
        "interview_id": interview_id,
        "response_id": signals_data.get("response_id"),
        "hesitation_count": signals_data.get("hesitation_count", 0),
        "pause_count": signals_data.get("pause_count", 0),
        "uncertainty_count": signals_data.get("uncertainty_count", 0),
        "repeated_word_count": signals_data.get("repeated_word_count", 0),
        "sentiment": signals_data.get("sentiment", "NEUTRAL"),
        "sentiment_score": signals_data.get("sentiment_score", 0.0),
        "stress_score": signals_data.get("stress_score", 0.0),
        "confidence_score": signals_data.get("confidence_score", 0.0),
        "contradiction_detected": signals_data.get("contradiction_detected", False),
        "contradiction_reason": signals_data.get("contradiction_reason"),
        "contradictions_detected": signals_data.get(
            "contradictions_detected",
            [signals_data["contradiction_reason"]] if signals_data.get("contradiction_reason") else [],
        ),
        "disclaimer": signals_data.get("disclaimer", "Behavioral signals are assistive and non-binding."),
        "ethical_disclaimer": signals_data.get("ethical_disclaimer", signals_data.get("disclaimer", "Behavioral signals are assistive and non-binding.")),
        "created_at": now,
    }


def get_hr_behavioral_signals(interview_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM hr_behavioral_signals WHERE interview_id = ? ORDER BY created_at ASC",
            (interview_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["contradiction_detected"] = bool(rec["contradiction_detected"])
            results.append(rec)
        return results


def save_hr_aptitude_evaluation(
    interview_id: str, eval_data: dict[str, Any]
) -> dict[str, Any]:
    aptitude_id = eval_data.get("aptitude_id") or _generate_id("hr_apt")
    now = _now()
    details = eval_data.get("evaluation_details", {})
    details_str = json.dumps(details) if isinstance(details, dict) else str(details)
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO hr_aptitude_evaluations (
                aptitude_id, interview_id, question_id, category,
                candidate_answer, logic_score, clarity_score,
                problem_solving_score, decision_making_score, communication_score,
                overall_score, evaluation_details, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                aptitude_id,
                interview_id,
                eval_data.get("question_id", ""),
                eval_data.get("category", "problem_solving"),
                eval_data.get("candidate_answer", ""),
                eval_data.get("logic_score", 0.0),
                eval_data.get("clarity_score", 0.0),
                eval_data.get("problem_solving_score", 0.0),
                eval_data.get("decision_making_score", 0.0),
                eval_data.get("communication_score", 0.0),
                eval_data.get("overall_score", 0.0),
                details_str,
                now,
            ),
        )
    return {
        "aptitude_id": aptitude_id,
        "interview_id": interview_id,
        "question_id": eval_data.get("question_id", ""),
        "category": eval_data.get("category", "problem_solving"),
        "candidate_answer": eval_data.get("candidate_answer", ""),
        "logic_score": eval_data.get("logic_score", 0.0),
        "clarity_score": eval_data.get("clarity_score", 0.0),
        "problem_solving_score": eval_data.get("problem_solving_score", 0.0),
        "decision_making_score": eval_data.get("decision_making_score", 0.0),
        "communication_score": eval_data.get("communication_score", 0.0),
        "overall_score": eval_data.get("overall_score", 0.0),
        "evaluation_details": details if isinstance(details, dict) else {},
        "created_at": now,
    }


def list_hr_aptitude_evaluations(interview_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM hr_aptitude_evaluations WHERE interview_id = ? ORDER BY created_at ASC",
            (interview_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            try:
                rec["evaluation_details"] = json.loads(rec.get("evaluation_details") or "{}")
            except Exception:
                rec["evaluation_details"] = {}
            results.append(rec)
        return results


def save_hr_interview_score(score_record: dict[str, Any]) -> dict[str, Any]:
    score_id = score_record.get("score_id") or _generate_id("hr_sc")
    now = _now()
    breakdown = score_record.get("breakdown", {})
    breakdown_str = json.dumps(breakdown) if isinstance(breakdown, dict) else str(breakdown)
    with _connection() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO hr_interview_scores (
                score_id, interview_id, candidate_id, relevance_score,
                communication_score, confidence_score, consistency_score,
                overall_hr_score, score_status, breakdown, human_review_required,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                score_id,
                score_record["interview_id"],
                score_record["candidate_id"],
                score_record.get("relevance_score", 0.0),
                score_record.get("communication_score", 0.0),
                score_record.get("confidence_score", 0.0),
                score_record.get("consistency_score", 0.0),
                score_record.get("overall_hr_score", 0.0),
                score_record.get("score_status", "FINAL"),
                breakdown_str,
                1 if score_record.get("human_review_required", False) else 0,
                now,
                now,
            ),
        )
    return get_hr_interview_score(score_record["interview_id"])  # type: ignore[return-value]


def get_hr_interview_score(interview_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM hr_interview_scores WHERE interview_id = ? ORDER BY created_at DESC LIMIT 1",
            (interview_id,),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["human_review_required"] = bool(rec["human_review_required"])
        try:
            rec["breakdown"] = json.loads(rec.get("breakdown") or "{}")
        except Exception:
            rec["breakdown"] = {}
        return rec


def save_hr_interview_report(report_data: dict[str, Any]) -> dict[str, Any]:
    report_id = report_data.get("report_id") or _generate_id("hr_rep")
    now = _now()
    report_json = report_data.get("report_json", {})
    report_json_str = json.dumps(report_json) if isinstance(report_json, dict) else str(report_json)

    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO hr_interview_reports (
                report_id, interview_id, candidate_id, opening_id,
                report_json, html_report, version, recruiter_decision,
                recruiter_notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                report_data["interview_id"],
                report_data["candidate_id"],
                report_data["opening_id"],
                report_json_str,
                report_data.get("html_report"),
                report_data.get("version", 1),
                report_data.get("recruiter_decision"),
                report_data.get("recruiter_notes"),
                now,
                now,
            ),
        )
    return get_hr_interview_report_by_interview(report_data["interview_id"])  # type: ignore[return-value]


def get_hr_interview_report_by_interview(interview_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM hr_interview_reports WHERE interview_id = ? ORDER BY created_at DESC LIMIT 1",
            (interview_id,),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        try:
            rec["report_json"] = json.loads(rec.get("report_json") or "{}")
        except Exception:
            rec["report_json"] = {}
        return rec


def list_hr_interview_reports_for_candidate(candidate_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM hr_interview_reports WHERE candidate_id = ? ORDER BY created_at DESC",
            (candidate_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            try:
                rec["report_json"] = json.loads(rec.get("report_json") or "{}")
            except Exception:
                rec["report_json"] = {}
            results.append(rec)
        return results


def update_hr_interview_decision(
    interview_id: str, decision: str, notes: str | None = None
) -> dict[str, Any] | None:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            UPDATE hr_interview_reports
            SET recruiter_decision = ?, recruiter_notes = ?, updated_at = ?
            WHERE interview_id = ?
            """,
            (decision, notes, now, interview_id),
        )
        row = connection.execute(
            "SELECT * FROM hr_interview_reports WHERE interview_id = ? ORDER BY created_at DESC LIMIT 1",
            (interview_id,),
        ).fetchone()
        if row is None:
            return None
        record = dict(row)
        try:
            record["report_json"] = json.loads(record.get("report_json") or "{}")
        except Exception:
            record["report_json"] = {}
        return record


# ---------------------------------------------------------------------------
# Day 41–52: Technical Interview Database Functions
# ---------------------------------------------------------------------------


def create_technical_interview_session(
    candidate_id: str,
    opening_id: str,
    target_role: str,
    experience_level: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    session_id = session_id or _generate_id("tech_sess")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO technical_interview_sessions (
                session_id, candidate_id, opening_id, target_role,
                experience_level, status, current_stage, total_questions,
                overall_score, rubric_breakdown, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'CREATED', 'CREATED', 0, 0.0, '{}', ?, ?)
            """,
            (session_id, candidate_id, opening_id, target_role, experience_level, now, now),
        )
    return get_technical_interview_session(session_id)


def get_technical_interview_session(session_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM technical_interview_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if not row:
            return None
        record = dict(row)
        record["rubric_breakdown"] = json.loads(record.get("rubric_breakdown") or "{}")
        return record


def list_technical_interview_sessions(candidate_id: str | None = None) -> list[dict[str, Any]]:
    with _connection() as connection:
        if candidate_id:
            rows = connection.execute(
                "SELECT * FROM technical_interview_sessions WHERE candidate_id = ? ORDER BY created_at DESC",
                (candidate_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM technical_interview_sessions ORDER BY created_at DESC"
            ).fetchall()
        result = []
        for r in rows:
            rec = dict(r)
            rec["rubric_breakdown"] = json.loads(rec.get("rubric_breakdown") or "{}")
            result.append(rec)
        return result


def update_technical_interview_session(
    session_id: str,
    status: str | None = None,
    current_stage: str | None = None,
    total_questions: int | None = None,
    overall_score: float | None = None,
    rubric_breakdown: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    now = _now()
    fields = ["updated_at = ?"]
    params: list[Any] = [now]
    if status is not None:
        fields.append("status = ?")
        params.append(status)
    if current_stage is not None:
        fields.append("current_stage = ?")
        params.append(current_stage)
    if total_questions is not None:
        fields.append("total_questions = ?")
        params.append(total_questions)
    if overall_score is not None:
        fields.append("overall_score = ?")
        params.append(overall_score)
    if rubric_breakdown is not None:
        fields.append("rubric_breakdown = ?")
        params.append(json.dumps(rubric_breakdown))
    params.append(session_id)

    with _connection() as connection:
        connection.execute(
            f"UPDATE technical_interview_sessions SET {', '.join(fields)} WHERE session_id = ?",
            params,
        )
    return get_technical_interview_session(session_id)


def update_technical_interview_session_status(session_id: str, status: str) -> dict[str, Any] | None:
    return update_technical_interview_session(session_id, status=status)


def save_technical_interview_question(
    session_id: str,
    question_text: str,
    topic: str,
    question_type: str,
    difficulty: str,
    sequence_order: int = 1,
    expected_criteria: list[str] | None = None,
    question_id: str | None = None,
) -> dict[str, Any]:
    question_id = question_id or _generate_id("tech_q")
    now = _now()
    expected_criteria_json = json.dumps(expected_criteria or [])
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO technical_interview_questions (
                question_id, session_id, question_text, topic,
                question_type, difficulty, sequence_order, expected_criteria, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question_id,
                session_id,
                question_text,
                topic,
                question_type,
                difficulty,
                sequence_order,
                expected_criteria_json,
                now,
            ),
        )
    return {
        "question_id": question_id,
        "session_id": session_id,
        "question_text": question_text,
        "topic": topic,
        "question_type": question_type,
        "difficulty": difficulty,
        "sequence_order": sequence_order,
        "expected_criteria": expected_criteria or [],
        "created_at": now,
    }


def list_technical_interview_questions(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM technical_interview_questions WHERE session_id = ? ORDER BY sequence_order ASC",
            (session_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["expected_criteria"] = json.loads(rec.get("expected_criteria") or "[]")
            results.append(rec)
        return results


def save_technical_interview_response(
    session_id: str | dict[str, Any],
    question_id: str | None = None,
    raw_answer: str = "",
    score: float = 0.0,
    depth_level: str = "shallow",
    parameter_scores: dict[str, Any] | None = None,
    feedback: str = "",
    response_id: str | None = None,
) -> dict[str, Any]:
    if isinstance(session_id, dict):
        d = session_id
        session_id = d.get("session_id") or d.get("interview_id") or ""
        question_id = d.get("question_id") or ""
        raw_answer = d.get("raw_answer") or d.get("answer_text") or ""
        score = float(d.get("score") if d.get("score") is not None else (d.get("normalized_score") or d.get("weighted_score") or 0.0))
        depth_level = d.get("depth_level") or d.get("depth_classification") or "shallow"
        parameter_scores = d.get("parameter_scores") or {
            "accuracy": d.get("accuracy_score"),
            "depth": d.get("depth_score"),
            "reasoning": d.get("reasoning_score"),
            "applicability": d.get("applicability_score"),
        }
        feedback = d.get("feedback") or d.get("explanation") or ""
        response_id = d.get("response_id")

    response_id = response_id or _generate_id("tech_resp")
    now = _now()
    param_json = json.dumps(parameter_scores or {})
    with _connection() as connection:
        if question_id:
            connection.execute(
                """
                INSERT OR IGNORE INTO technical_interview_questions (
                    question_id, session_id, question_text, topic, question_type, difficulty, sequence_order, expected_criteria, created_at
                ) VALUES (?, ?, 'Technical Assessment Question', 'General', 'conceptual', 'mid', 1, '[]', ?)
                """,
                (question_id, session_id, now),
            )
        connection.execute(
            """
            INSERT INTO technical_interview_responses (
                response_id, session_id, question_id, raw_answer,
                score, depth_level, parameter_scores, feedback, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                response_id,
                session_id,
                question_id,
                raw_answer,
                score,
                depth_level,
                param_json,
                feedback,
                now,
            ),
        )
    return {
        "response_id": response_id,
        "session_id": session_id,
        "question_id": question_id,
        "raw_answer": raw_answer,
        "score": score,
        "depth_level": depth_level,
        "parameter_scores": parameter_scores or {},
        "feedback": feedback,
        "created_at": now,
    }


def list_technical_interview_responses(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM technical_interview_responses WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["parameter_scores"] = json.loads(rec.get("parameter_scores") or "{}")
            rec["normalized_score"] = rec["score"]
            rec["depth_classification"] = rec["depth_level"]
            results.append(rec)
        return results


# ---------------------------------------------------------------------------
# Day 50: Machine Test Database Functions
# ---------------------------------------------------------------------------


def create_machine_test_assignment(
    candidate_id: str,
    opening_id: str,
    task_type: str,
    task_id: str,
    title: str,
    description: str,
    time_limit_minutes: int = 60,
    assignment_id: str | None = None,
) -> dict[str, Any]:
    assignment_id = assignment_id or _generate_id("mt_assign")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO machine_test_assignments (
                assignment_id, candidate_id, opening_id, task_type,
                task_id, title, description, time_limit_minutes, status, assigned_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ASSIGNED', ?)
            """,
            (
                assignment_id,
                candidate_id,
                opening_id,
                task_type,
                task_id,
                title,
                description,
                time_limit_minutes,
                now,
            ),
        )
    return get_machine_test_assignment(assignment_id)  # type: ignore[return-value]


def get_machine_test_assignment(assignment_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM machine_test_assignments WHERE assignment_id = ?",
            (assignment_id,),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["test_id"] = rec["assignment_id"]
        return rec


def list_machine_test_assignments(candidate_id: str | None = None) -> list[dict[str, Any]]:
    with _connection() as connection:
        if candidate_id:
            rows = connection.execute(
                "SELECT * FROM machine_test_assignments WHERE candidate_id = ? ORDER BY assigned_at DESC",
                (candidate_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM machine_test_assignments ORDER BY assigned_at DESC"
            ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["test_id"] = rec["assignment_id"]
            results.append(rec)
        return results


def update_machine_test_assignment_status(
    assignment_id: str, status: str, completed_at: str | None = None
) -> dict[str, Any] | None:
    with _connection() as connection:
        connection.execute(
            """
            UPDATE machine_test_assignments
            SET status = ?, completed_at = COALESCE(?, completed_at)
            WHERE assignment_id = ?
            """,
            (status, completed_at, assignment_id),
        )
    return get_machine_test_assignment(assignment_id)


def save_machine_test_submission(
    assignment_id: str | dict[str, Any],
    code_content: str = "",
    language: str = "python",
    time_spent_minutes: float = 0.0,
    total_score: float = 0.0,
    rubric_scores: dict[str, Any] | None = None,
    execution_details: dict[str, Any] | None = None,
    submission_id: str | None = None,
) -> dict[str, Any]:
    if isinstance(assignment_id, dict):
        d = assignment_id
        assignment_id = d.get("assignment_id") or d.get("test_id") or ""
        code_content = d.get("code_content") or ""
        language = d.get("language") or "python"
        time_spent_minutes = float(d.get("time_spent_minutes") or d.get("elapsed_time_minutes") or 0.0)
        total_score = float(d.get("total_score") or 0.0)
        rubric_scores = d.get("rubric_scores") or {
            "correctness": d.get("correctness_score"),
            "efficiency": d.get("efficiency_score"),
            "code_quality": d.get("code_quality_score"),
            "problem_solving": d.get("problem_solving_score"),
            "time_management": d.get("time_management_score"),
        }
        execution_details = d.get("execution_details") or {
            "test_results": d.get("test_results"),
            "evaluation_summary": d.get("evaluation_summary"),
        }
        submission_id = d.get("submission_id")

    submission_id = submission_id or _generate_id("mt_sub")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO machine_test_submissions (
                submission_id, assignment_id, code_content, language,
                time_spent_minutes, total_score, rubric_scores, execution_details,
                status, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'EVALUATED', ?)
            """,
            (
                submission_id,
                assignment_id,
                code_content,
                language,
                time_spent_minutes,
                total_score,
                json.dumps(rubric_scores or {}),
                json.dumps(execution_details or {}),
                now,
            ),
        )
    return get_machine_test_submission(submission_id)  # type: ignore[return-value]


def get_machine_test_submission(submission_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM machine_test_submissions WHERE submission_id = ? OR assignment_id = ? ORDER BY submitted_at DESC LIMIT 1",
            (submission_id, submission_id),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["rubric_scores"] = json.loads(rec.get("rubric_scores") or "{}")
        rec["execution_details"] = json.loads(rec.get("execution_details") or "{}")
        return rec


def list_machine_test_submissions(assignment_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM machine_test_submissions WHERE assignment_id = ? ORDER BY submitted_at DESC",
            (assignment_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["rubric_scores"] = json.loads(rec.get("rubric_scores") or "{}")
            rec["execution_details"] = json.loads(rec.get("execution_details") or "{}")
            results.append(rec)
        return results


# ---------------------------------------------------------------------------
# Day 49 & Day 48: Integrity & Behavioral Records Database Functions
# ---------------------------------------------------------------------------


def save_candidate_integrity_record(
    candidate_id: str,
    session_id: str,
    round_type: str,
    has_consent: bool,
    total_risk_points: int,
    risk_level: str,
    requires_human_review: bool,
    events: list[dict[str, Any]],
    review_flags: list[dict[str, Any]],
    record_id: str | None = None,
) -> dict[str, Any]:
    record_id = record_id or _generate_id("integ_rec")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO candidate_integrity_records (
                record_id, candidate_id, session_id, round_type,
                has_consent, total_risk_points, risk_level, requires_human_review,
                events_json, review_flags, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                candidate_id,
                session_id,
                round_type,
                1 if has_consent else 0,
                total_risk_points,
                risk_level,
                1 if requires_human_review else 0,
                json.dumps(events),
                json.dumps(review_flags),
                now,
            ),
        )
    return {
        "record_id": record_id,
        "candidate_id": candidate_id,
        "session_id": session_id,
        "round_type": round_type,
        "has_consent": has_consent,
        "total_risk_points": total_risk_points,
        "risk_level": risk_level,
        "requires_human_review": requires_human_review,
        "events": events,
        "review_flags": review_flags,
        "created_at": now,
    }


def get_candidate_integrity_records(candidate_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM candidate_integrity_records WHERE candidate_id = ? ORDER BY created_at DESC",
            (candidate_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["has_consent"] = bool(rec["has_consent"])
            rec["requires_human_review"] = bool(rec["requires_human_review"])
            rec["events"] = json.loads(rec.get("events_json") or "[]")
            rec["review_flags"] = json.loads(rec.get("review_flags") or "[]")
            results.append(rec)
        return results


def save_candidate_behavioral_record(
    candidate_id: str,
    session_id: str,
    round_type: str,
    has_consent: bool,
    consistency_index: float,
    requires_human_review: bool,
    observations: list[dict[str, Any]],
    disclaimer: str,
    record_id: str | None = None,
) -> dict[str, Any]:
    record_id = record_id or _generate_id("behav_rec")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO candidate_behavioral_records (
                record_id, candidate_id, session_id, round_type,
                has_consent, consistency_index, requires_human_review,
                observations_json, disclaimer, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                candidate_id,
                session_id,
                round_type,
                1 if has_consent else 0,
                consistency_index,
                1 if requires_human_review else 0,
                json.dumps(observations),
                disclaimer,
                now,
            ),
        )
    return {
        "record_id": record_id,
        "candidate_id": candidate_id,
        "session_id": session_id,
        "round_type": round_type,
        "has_consent": has_consent,
        "consistency_index": consistency_index,
        "requires_human_review": requires_human_review,
        "observations": observations,
        "disclaimer": disclaimer,
        "created_at": now,
    }


def get_candidate_behavioral_records(candidate_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM candidate_behavioral_records WHERE candidate_id = ? ORDER BY created_at DESC",
            (candidate_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["has_consent"] = bool(rec["has_consent"])
            rec["requires_human_review"] = bool(rec["requires_human_review"])
            rec["observations"] = json.loads(rec.get("observations_json") or "[]")
            results.append(rec)
        return results


# ---------------------------------------------------------------------------
# Day 41 & 51: Cross-Round Evaluation Database Functions
# ---------------------------------------------------------------------------


def save_cross_round_evaluation(
    candidate_id: str | dict[str, Any],
    opening_id: str = "",
    target_role: str = "",
    hiring_fit_percentage: float = 0.0,
    round_scores: dict[str, Any] | None = None,
    effective_weights: dict[str, Any] | None = None,
    completed_rounds: int = 0,
    missing_rounds: list[str] | None = None,
    anomalies: list[str] | None = None,
    evaluation_id: str | None = None,
) -> dict[str, Any]:
    if isinstance(candidate_id, dict):
        d = candidate_id
        candidate_id = d.get("candidate_id", "")
        opening_id = d.get("opening_id", "")
        target_role = d.get("target_role", "")
        hiring_fit_percentage = float(d.get("hiring_fit_percentage", 0.0))
        round_scores = d.get("round_scores", {})
        effective_weights = d.get("effective_weights", {})
        completed_rounds = int(d.get("completed_rounds", 0))
        missing_rounds = d.get("missing_rounds", [])
        anomalies = d.get("anomalies", [])
        evaluation_id = d.get("evaluation_id")

    evaluation_id = evaluation_id or _generate_id("cross_eval")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO cross_round_evaluations (
                evaluation_id, candidate_id, opening_id, target_role,
                hiring_fit_percentage, round_scores_json, effective_weights_json,
                completed_rounds, missing_rounds_json, anomalies_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation_id,
                candidate_id,
                opening_id,
                target_role,
                hiring_fit_percentage,
                json.dumps(round_scores),
                json.dumps(effective_weights),
                completed_rounds,
                json.dumps(missing_rounds),
                json.dumps(anomalies),
                now,
            ),
        )
    return get_cross_round_evaluation(evaluation_id)  # type: ignore[return-value]


def get_cross_round_evaluation(evaluation_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM cross_round_evaluations WHERE evaluation_id = ?",
            (evaluation_id,),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["round_scores"] = json.loads(rec.get("round_scores_json") or "{}")
        rec["effective_weights"] = json.loads(rec.get("effective_weights_json") or "{}")
        rec["missing_rounds"] = json.loads(rec.get("missing_rounds_json") or "[]")
        rec["anomalies"] = json.loads(rec.get("anomalies_json") or "[]")
        return rec


def list_cross_round_evaluations(candidate_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM cross_round_evaluations WHERE candidate_id = ? ORDER BY created_at DESC",
            (candidate_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["round_scores"] = json.loads(rec.get("round_scores_json") or "{}")
            rec["effective_weights"] = json.loads(rec.get("effective_weights_json") or "{}")
            rec["missing_rounds"] = json.loads(rec.get("missing_rounds_json") or "[]")
            rec["anomalies"] = json.loads(rec.get("anomalies_json") or "[]")
            results.append(rec)
        return results


# ---------------------------------------------------------------------------
# Day 52: Final Recommendation Database Functions
# ---------------------------------------------------------------------------


def save_final_recommendation(
    candidate_id: str,
    opening_id: str,
    target_role: str,
    decision: str,
    score: float,
    confidence: float = 0.85,
    completed_rounds: int = 5,
    expected_rounds: int = 5,
    reasons: list[str] | None = None,
    risk_factors: dict[str, Any] | None = None,
    recruiter_decision: str = "PENDING_REVIEW",
    recruiter_notes: str | None = None,
    recommendation_id: str | None = None,
) -> dict[str, Any]:
    recommendation_id = recommendation_id or _generate_id("final_rec")
    now = _now()
    reasons_list = reasons or []
    risks_dict = risk_factors or {}
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO final_recommendations (
                recommendation_id, candidate_id, opening_id, target_role,
                decision, score, confidence, completed_rounds, expected_rounds,
                reasons_json, risk_factors_json, recruiter_decision,
                recruiter_notes, recruiter_decided_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                recommendation_id,
                candidate_id,
                opening_id,
                target_role,
                decision,
                score,
                confidence,
                completed_rounds,
                expected_rounds,
                json.dumps(reasons_list),
                json.dumps(risks_dict),
                recruiter_decision,
                recruiter_notes,
                now if recruiter_decision != "PENDING_REVIEW" else None,
                now,
                now,
            ),
        )
    return get_final_recommendation(recommendation_id)  # type: ignore[return-value]


def get_final_recommendation(recommendation_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM final_recommendations WHERE recommendation_id = ?",
            (recommendation_id,),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["reasons"] = json.loads(rec.get("reasons_json") or "[]")
        rec["risk_factors"] = json.loads(rec.get("risk_factors_json") or "{}")
        rec["confidence_interpretation"] = "Evidence completeness indicator; not a probability of job success."
        return rec


def list_final_recommendations(candidate_id: str | None = None) -> list[dict[str, Any]]:
    with _connection() as connection:
        if candidate_id:
            rows = connection.execute(
                "SELECT * FROM final_recommendations WHERE candidate_id = ? ORDER BY created_at DESC",
                (candidate_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM final_recommendations ORDER BY created_at DESC"
            ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["reasons"] = json.loads(rec.get("reasons_json") or "[]")
            rec["risk_factors"] = json.loads(rec.get("risk_factors_json") or "{}")
            rec["confidence_interpretation"] = "Evidence completeness indicator; not a probability of job success."
            results.append(rec)
        return results


def update_final_recommendation_decision(
    recommendation_id: str,
    recruiter_decision: str,
    recruiter_notes: str | None = None,
) -> dict[str, Any] | None:
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            UPDATE final_recommendations
            SET recruiter_decision = ?, recruiter_notes = ?, recruiter_decided_at = ?, updated_at = ?
            WHERE recommendation_id = ?
            """,
            (recruiter_decision, recruiter_notes, now, now, recommendation_id),
        )
    return get_final_recommendation(recommendation_id)


def save_hiring_intelligence_report(
    candidate_id: str,
    opening_id: str,
    report_json: dict[str, Any],
    markdown_content: str,
    html_content: str,
    created_by_recruiter_id: str | None = None,
    version: int | None = None,
    report_id: str | None = None,
) -> dict[str, Any]:
    report_id = report_id or _generate_id("report")
    now = _now()
    with _connection() as connection:
        if version is None:
            prev = connection.execute(
                "SELECT MAX(version) as max_v FROM hiring_intelligence_reports WHERE candidate_id = ?",
                (candidate_id,),
            ).fetchone()
            current_max = prev["max_v"] if prev and prev["max_v"] is not None else 0
            version = current_max + 1

        connection.execute(
            """
            INSERT INTO hiring_intelligence_reports (
                report_id, candidate_id, opening_id, version,
                report_json, markdown_content, html_content,
                created_by_recruiter_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                candidate_id,
                opening_id,
                version,
                json.dumps(report_json),
                markdown_content,
                html_content,
                created_by_recruiter_id,
                now,
            ),
        )
    return get_hiring_intelligence_report(report_id)  # type: ignore[return-value]


def get_hiring_intelligence_report(report_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM hiring_intelligence_reports WHERE report_id = ?",
            (report_id,),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["report_json"] = json.loads(rec.get("report_json") or "{}")
        return rec


def get_latest_hiring_intelligence_report(candidate_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM hiring_intelligence_reports WHERE candidate_id = ? ORDER BY version DESC LIMIT 1",
            (candidate_id,),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["report_json"] = json.loads(rec.get("report_json") or "{}")
        return rec


def list_hiring_intelligence_reports(candidate_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM hiring_intelligence_reports WHERE candidate_id = ? ORDER BY version DESC",
            (candidate_id,),
        ).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["report_json"] = json.loads(rec.get("report_json") or "{}")
            results.append(rec)
        return results


def append_audit_event(
    event_type: str,
    actor_id: str,
    subject_id: str,
    details: dict[str, Any],
    event_id: str | None = None,
) -> dict[str, Any]:
    event_id = event_id or _generate_id("audit")
    now = _now()
    with _connection() as connection:
        last = connection.execute(
            "SELECT event_hash FROM audit_events ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        previous_hash = last["event_hash"] if last and last["event_hash"] else "GENESIS"

        canonical_payload = {
            "timestamp": now,
            "event_type": event_type,
            "actor_id": actor_id,
            "subject_id": subject_id,
            "details": details,
            "previous_hash": previous_hash,
        }
        event_hash = hashlib.sha256(
            json.dumps(canonical_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        connection.execute(
            """
            INSERT INTO audit_events (
                event_id, event_type, actor_id, subject_id,
                details_json, previous_hash, event_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                event_type,
                actor_id,
                subject_id,
                json.dumps(details),
                previous_hash,
                event_hash,
                now,
            ),
        )
    return {
        "event_id": event_id,
        "event_type": event_type,
        "actor_id": actor_id,
        "subject_id": subject_id,
        "details": details,
        "previous_hash": previous_hash,
        "event_hash": event_hash,
        "created_at": now,
    }


def list_audit_events(
    limit: int = 100,
    event_type: str | None = None,
    subject_id: str | None = None,
) -> list[dict[str, Any]]:
    with _connection() as connection:
        query = "SELECT * FROM audit_events WHERE 1=1"
        params: list[Any] = []
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if subject_id:
            query += " AND subject_id = ?"
            params.append(subject_id)
        query += " ORDER BY rowid DESC LIMIT ?"
        params.append(limit)

        rows = connection.execute(query, tuple(params)).fetchall()
        results = []
        for r in rows:
            rec = dict(r)
            rec["details"] = json.loads(rec.get("details_json") or "{}")
            results.append(rec)
        return results


def verify_audit_log_integrity() -> dict[str, Any]:
    with _connection() as connection:
        rows = connection.execute("SELECT * FROM audit_events ORDER BY rowid ASC").fetchall()
        if not rows:
            return {"verified": True, "event_count": 0, "status": "EMPTY"}

        prev_hash = "GENESIS"
        for idx, r in enumerate(rows):
            if r["previous_hash"] != prev_hash:
                return {
                    "verified": False,
                    "tampered_at_index": idx,
                    "event_id": r["event_id"],
                    "expected_previous_hash": prev_hash,
                    "actual_previous_hash": r["previous_hash"],
                }
            canonical_payload = {
                "timestamp": r["created_at"],
                "event_type": r["event_type"],
                "actor_id": r["actor_id"],
                "subject_id": r["subject_id"],
                "details": json.loads(r["details_json"]),
                "previous_hash": prev_hash,
            }
            computed_hash = hashlib.sha256(
                json.dumps(canonical_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            if computed_hash != r["event_hash"]:
                return {
                    "verified": False,
                    "tampered_at_index": idx,
                    "event_id": r["event_id"],
                    "expected_hash": computed_hash,
                    "stored_hash": r["event_hash"],
                }
            prev_hash = r["event_hash"]

        return {"verified": True, "event_count": len(rows), "status": "VALID"}


def save_coaching_record(
    candidate_id: str,
    target_role: str,
    identified_skill_gaps: list[str],
    recommended_preparation: list[str],
    practice_questions: list[str],
    coaching_id: str | None = None,
) -> dict[str, Any]:
    coaching_id = coaching_id or _generate_id("coach")
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO candidate_coaching_records (
                coaching_id, candidate_id, target_role,
                identified_skill_gaps_json, recommended_preparation_json,
                practice_questions_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                coaching_id,
                candidate_id,
                target_role,
                json.dumps(identified_skill_gaps),
                json.dumps(recommended_preparation),
                json.dumps(practice_questions),
                now,
            ),
        )
    return get_coaching_record(coaching_id)  # type: ignore[return-value]


def get_coaching_record(coaching_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM candidate_coaching_records WHERE coaching_id = ?",
            (coaching_id,),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["identified_skill_gaps"] = json.loads(rec.get("identified_skill_gaps_json") or "[]")
        rec["recommended_preparation"] = json.loads(rec.get("recommended_preparation_json") or "[]")
        rec["practice_questions"] = json.loads(rec.get("practice_questions_json") or "[]")
        return rec


def get_latest_coaching_record(candidate_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM candidate_coaching_records WHERE candidate_id = ? ORDER BY created_at DESC LIMIT 1",
            (candidate_id,),
        ).fetchone()
        if not row:
            return None
        rec = dict(row)
        rec["identified_skill_gaps"] = json.loads(rec.get("identified_skill_gaps_json") or "[]")
        rec["recommended_preparation"] = json.loads(rec.get("recommended_preparation_json") or "[]")
        rec["practice_questions"] = json.loads(rec.get("practice_questions_json") or "[]")
        return rec
