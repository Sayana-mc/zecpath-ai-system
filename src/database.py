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
            resume_filename TEXT,
            application_status TEXT NOT NULL CHECK (
                application_status IN (
                    'APPLIED', 'IN_REVIEW', 'SHORTLISTED', 'INTERVIEW',
                    'OFFER', 'HIRED', 'REJECTED', 'WITHDRAWN'
                )
            ),
            score REAL,
            score_evidence TEXT,
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
        CREATE TABLE IF NOT EXISTS recruiter_login_attempts (
            key_hash TEXT PRIMARY KEY,
            attempts INTEGER NOT NULL,
            window_started REAL NOT NULL,
            blocked_until REAL NOT NULL DEFAULT 0
        );
        """
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
    record["score_evidence"] = (
        json.loads(record["score_evidence"])
        if record["score_evidence"] is not None
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
                preferred_skills, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'OPEN', ?, ?)
            """,
            (
                opening_id,
                data["title"],
                data.get("description", ""),
                json.dumps(data["required_skills"]),
                json.dumps(data.get("preferred_skills", [])),
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
        "status",
    }
    updates = {key: value for key, value in data.items() if key in allowed_fields}
    if not updates:
        return get_opening(opening_id)
    updates["updated_at"] = _now()
    with _connection() as connection:
        current = connection.execute(
            "SELECT required_skills FROM openings WHERE opening_id = ?",
            (opening_id,),
        ).fetchone()
        if current is None:
            return None
        required_skills_changed = (
            "required_skills" in updates
            and json.loads(current["required_skills"])
            != updates["required_skills"]
        )
        for key in ("required_skills", "preferred_skills"):
            if key in updates:
                updates[key] = json.dumps(updates[key])
        assignments = ", ".join(f"{key} = ?" for key in updates)
        connection.execute(
            f"UPDATE openings SET {assignments} WHERE opening_id = ?",
            (*updates.values(), opening_id),
        )
        if required_skills_changed:
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
                application_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'APPLIED', ?, ?)
            """,
            (
                candidate_id,
                data["name"],
                data.get("email"),
                data["opening_id"],
                json.dumps(data.get("skills", [])),
                data.get("resume_text", ""),
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
    allowed_fields = {"name", "email", "skills", "application_status"}
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
    candidate_id: str, filename: str, parsed_text: str
) -> bool:
    with _connection() as connection:
        cursor = connection.execute(
            """
            UPDATE candidates
            SET resume_filename = ?, resume_text = ?, score = NULL,
                score_evidence = NULL, updated_at = ?
            WHERE candidate_id = ?
            """,
            (filename, parsed_text, _now(), candidate_id),
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
