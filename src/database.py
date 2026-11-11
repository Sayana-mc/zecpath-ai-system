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
    opening_id = data["opening_id"]
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
                json.dumps(data["required_skills"]),
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


def create_candidate(data: dict[str, Any]) -> dict[str, Any]:
    candidate_id = data["candidate_id"]
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
                data["name"],
                data.get("email"),
                data["opening_id"],
                json.dumps(data.get("skills", [])),
                data.get("resume_text", ""),
                data.get("location"),
                (
                    int(data["relocation_willingness"])
                    if data.get("relocation_willingness") is not None
                    else None
                ),
                data.get("work_mode_preference"),
                data.get("availability_date"),
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
        return dict(row) if row is not None else {}


def get_screening_answer(answer_id: str) -> dict[str, Any] | None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM screening_answers WHERE answer_id = ?", (answer_id,)
        ).fetchone()
        return dict(row) if row is not None else None


def list_screening_answers(session_id: str) -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM screening_answers
            WHERE session_id = ? ORDER BY created_at
            """,
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]


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
                json.dumps(report),
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
        return dict(row) if row is not None else {}


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
