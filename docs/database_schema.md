# Root SQLite database schema

The root app uses SQLite at `data/zecpath.sqlite3`, unless
`ZECPATH_DB_PATH` is set before running account commands and starting the
server. Every database connection enables SQLite foreign-key enforcement.
Tables are initialized lazily by the connection helper and the app lifespan.

## Tables

| Table | Primary key | Important fields and relations |
|---|---|---|
| `openings` | `opening_id` | Title, description, JSON required/preferred skills, optional minimum education/experience, OPEN/CLOSED state, created/updated timestamps. |
| `candidates` | `candidate_id` | Candidate name/email, opening FK (`ON DELETE CASCADE`), JSON skills, resume text/filename/structured JSON, application status, score and JSON score evidence, timestamps. Unique `(opening_id,email)` prevents same-email duplicates within a job. |
| `processing_jobs` | `job_id` | Source filename, optional candidate ID, QUEUED/PROCESSING/COMPLETED/FAILED state, JSON result, safe error, timestamp. Candidate ID is not a foreign key because processing metadata and candidate deletion/redaction are managed separately. |
| `screening_reports` | `report_id` | Candidate and opening foreign keys (`ON DELETE CASCADE`), report JSON, timestamp. |
| `recruiter_accounts` | `username` | Random salt, PBKDF2 password hash, created timestamp. Intended for one local recruiter account. |
| `recruiter_sessions` | `token_hash` | Recruiter username, expiry and creation epoch. Raw cookie token is not stored. |
| `recruiter_login_attempts` | `key_hash` | Failure count, window start and throttle expiry. Key hashes combine client host and normalized username. |

Indexes support candidate filtering by job/status, screening-report retrieval
by candidate/time, and expiry lookup for recruiter sessions.

## Migration and transaction behavior

Opening education/experience requirement columns and candidate
`resume_data` are added with `PRAGMA table_info` followed by additive `ALTER
TABLE` when missing. Existing data is not dropped or rewritten. This is not a
versioned migration framework; maintain a stopped-server backup before a
schema-updating release.

The connection context commits successful operations and rolls back exceptions.
First-account creation, credential reset, and login-attempt updates use
`BEGIN IMMEDIATE` to serialize state-changing transactions. Score/evidence are
stored together on candidate rows and cleared when their input facts change.

## Data lifecycle and limitations

- Deleting an opening cascades its candidate and screening-report records.
- Deleting a candidate removes reports and redacts parsed content from linked
  processing-job results.
- Uploaded file bytes are temporary and removed after parsing; the candidate
  keeps the original filename and extracted text/data, not the original file.
- Applicant data, including resume and screening text, is not encrypted at
  rest. No retention/deletion policy or automated backup/restore exists.
- Processing-job candidate links and session usernames are not enforced by
  foreign keys; application logic validates account/session state and handles
  candidate deletion explicitly.
- Candidate lists return full resume text and are not paginated.

The integration report and audit list the DB test evidence and production
gaps.
