# Zecpath AI Hiring System

Zecpath is a collection of ATS experiments and hiring-pipeline prototypes, plus
a small local recruiter API. The root API is the runnable application surface;
the numbered `day*` folders are learning, evaluation, and simulation modules
and are not all wired into that API.

## What the local API supports

- Create, list, edit, close, and delete job openings.
- Register, list, edit, track, and delete candidate applications.
- Protect API operations with a single environment-configured recruiter
  username and password. The dashboard receives an HTTP-only session cookie
  that survives page reloads and expires after 8 hours; direct API clients may
  continue to use HTTP Basic authentication.
- Upload TXT, DOCX, and text-based PDF resumes (up to 5 MiB) and extract text.
- Review the saved extracted resume text and the exact snippets used by matching.
- Persist application, processing, score, and review data in SQLite.
- Calculate a transparent exact required-skill overlap score from explicitly
  supplied candidate skills and/or exact skill mentions in extracted resume
  text. The response includes the matching evidence.
- Clear saved scores and evidence when a candidate's skills/resume or a job's
  required skills change; affected applications must be rescored before they
  appear in shortlist suggestions.
- Rank previously scored applications for a job as a recruiter review aid.
- Save rule-based screening-answer notes and review flags. The Day 25 keyword
  classifier and regex extractors do not score or rank candidates.
- Use interactive API documentation at `/docs`.

The matching method is a simple lexical heuristic, not semantic AI, a validated
employment model, or a recommendation to reject a candidate. Every score and
shortlist requires human review. No external AI or ATS service is called.
Screening notes use separate keyword/regex rules; their heuristic output is not
validated and is not included in match scores. Scanned-image OCR, multiple
recruiter roles, identity-provider integration, notifications, and production
deployment are not implemented in the root API.

## Technology

- Python 3.12 (the repository suite was run with Python 3.12.4).
- FastAPI and Pydantic for HTTP APIs and request/response validation.
- Uvicorn for the ASGI server.
- SQLite for local application, score, screening-note, session, and processing
  job persistence.
- `python-docx` and `pypdf` for DOCX/PDF text extraction; TXT is decoded as
  UTF-8.
- `python-multipart` for file-upload form parsing.
- A same-origin HTML/CSS/JavaScript dashboard in `static/index.html`.
- Pytest and HTTPX for root and repository testing.

The root application has no configured LLM provider. The separate numbered
day folders include prototypes (for example Day 24 Faster-Whisper) that are
not dependencies or live integrations of the root API.

## Set up and run (Windows PowerShell)

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.create_recruiter
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

The initializer prompts for a username and password without echoing the
password, requires at least 16 characters, and stores a salted PBKDF2-HMAC
hash. It only creates the first account and will not overwrite an existing
account. The database is created at its configured path before the prompt.

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) for the recruiter
workspace and sign in with those credentials. `/docs` documents the protected
API. The health endpoint is `http://127.0.0.1:8000/api/v1/health`; it is public
and reports API/database availability and whether recruiter authentication is
configured, without exposing credentials. Recruiter data endpoints accept the
dashboard session cookie or HTTP Basic authentication. The dashboard checks
health on load and periodically, restores an unexpired session after reload,
and reloads saved data after a backend connection is restored. The small
browser UI and backend share one FastAPI process; there is no separate frontend
build or start command.

### Environment configuration

| Variable | Required | Purpose |
|---|---:|---|
| `ZECPATH_DB_PATH` | No | SQLite file path. Defaults to `data/zecpath.sqlite3`. Set it before both account initialization and server startup. |
| `ZECPATH_AUTH_USERNAME` | No | Legacy local-only authentication username. Prefer the database account initialized by `src.create_recruiter`. |
| `ZECPATH_AUTH_PASSWORD` | No | Legacy local-only password (minimum 16 characters); it is read from the process environment and is not stored as a password hash. Do not use this mode for network exposure. |

No `.env` file is loaded by the application. In PowerShell, environment
variables apply to child processes started in that same terminal. Use a
unique temporary database for a clean synthetic demo.

### API quick reference

`/docs` is the interactive Swagger UI; `/openapi.json` serves the OpenAPI
schema. `GET /api/v1/health` and `GET /api/v1/auth/session` are public. The
session status endpoint returns `authenticated: false` when no valid session
cookie is present.

| Operation | Endpoint | Access |
|---|---|---|
| Recruiter login | `POST /api/v1/auth/session` | Public; sets an HTTP-only session cookie on valid credentials. |
| Check session | `GET /api/v1/auth/session` | Public status probe; does not reveal the cookie. |
| Sign out | `DELETE /api/v1/auth/session` | Valid session; same-origin request required. |
| Health | `GET /api/v1/health` | Public; checks application/database availability. |
| Jobs | `/api/v1/openings` and `/api/v1/openings/{opening_id}` | Protected; GET/POST/PATCH/DELETE as documented in `/docs`. |
| Candidates | `/api/v1/candidates` and `/api/v1/candidates/{candidate_id}` | Protected; GET/POST/PATCH/DELETE. |
| Resume upload | `POST /api/v1/resumes/upload` | Protected multipart upload; TXT, DOCX, or text-based PDF up to 5 MiB. |
| Processing status | `GET /api/v1/jobs/{job_id}` | Protected. |
| Match score | `POST /api/v1/candidates/score` | Protected; deterministic exact-skill evidence. |
| Shortlist suggestions | `POST /api/v1/openings/{opening_id}/shortlist` | Protected; uses saved scores and does not change candidate status. |
| Screening notes | `POST/GET /api/v1/candidates/{candidate_id}/screening-reports` | Protected; rule-based notes, not an assessment score. |

Browser session-authenticated POST/PATCH/DELETE requests must have a matching
same-origin `Origin` header. Direct API clients can use HTTP Basic; use it only
over TLS outside localhost.

If port 8000 is already in use, choose a free local port, for example:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8765
```

Then open `http://127.0.0.1:8765/`. The page uses same-origin relative API
routes, so the UI and API always use the selected port together.

The API creates `data/zecpath.sqlite3` on first start. To use a different local
database, set the path before launching:

```powershell
$env:ZECPATH_DB_PATH = "$PWD\data\live-demo.sqlite3"
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Set `ZECPATH_DB_PATH` before running the first-recruiter initializer as well,
so the account and application use the same database. Unset the variable to
return to the default path. No external service keys are required. The
application does not ship with a recruiter username or password.
For legacy local setups, `ZECPATH_AUTH_USERNAME` and a unique
`ZECPATH_AUTH_PASSWORD` of at least 16 characters can still configure
environment-based authentication; those credentials are not persisted by the
application. Login sessions are stored as SHA-256 token hashes in the selected
SQLite database, use an HTTP-only, SameSite=Strict cookie, expire after 8
hours, and are revoked on sign-out. Five failed logins for a username and
client address are throttled for 15 minutes. Session-authenticated writes
require a same-origin `Origin` header. The API also retains HTTP Basic for
direct clients; Basic authentication must only be used over TLS if reachable
through a network-facing proxy.

Keep the service bound to localhost. The single shared recruiter credential is
not a substitute for an identity provider, multiple recruiter accounts, or
account lifecycle management. The SQLite database and extracted
resume/screening text remain unencrypted; do not use real applicant data or
expose this prototype to a network. Production use requires, at minimum, a
security review, TLS, encryption/key management, access controls, consent and
retention policies, audit logging, migration tooling, backups, and deployment
hardening.

## Local database backup and restore

The application currently has no automated backup or migration command. For a
local demo, stop Uvicorn before copying the configured SQLite database:

```powershell
Copy-Item .\data\zecpath.sqlite3 .\data\zecpath.sqlite3.backup
```

Keep the backup outside any publicly served directory and verify it exists
before replacing a database. To restore, stop Uvicorn, preserve the current
database under a different name, then copy the verified backup to the exact
configured database path. These file-copy instructions are only appropriate
for a stopped local SQLite application; they are not a production backup or
recovery plan. The database schema is created with `CREATE TABLE IF NOT EXISTS`
and does not have versioned migrations.

## Repeatable synthetic demo

The repository includes [data/demo_resume.txt](data/demo_resume.txt), a
fictional text resume. Use only synthetic data:

1. In `/docs`, call `POST /api/v1/openings` with a title, description, required
   skills `["Python", "SQL", "Git"]`, and optional preferred skills. Save the
   returned `opening_id`.
2. Call `POST /api/v1/candidates` with a synthetic name/email, that
   `opening_id`, and an empty `skills` list. Save the returned `candidate_id`.
3. Call `POST /api/v1/resumes/upload`, set `candidate_id`, and select
   `data/demo_resume.txt`. The response contains a processing `job_id`.
4. Call `GET /api/v1/jobs/{job_id}` to verify `COMPLETED`, then
   `GET /api/v1/candidates/{candidate_id}` to inspect the saved extracted text.
5. Call `POST /api/v1/candidates/score` with the opening and candidate IDs.
   Review the score evidence and `human_review_required` flag.
6. In the application row, expand **Screening report**, choose a question
   topic, enter a question and answer, and generate the rule-based report.
   Review its extracted fields and flags; it is not an assessment score.
7. Call `POST /api/v1/openings/{opening_id}/shortlist` with a
   `minimum_score`. This ranks saved scores but does not change application
   statuses or make hiring decisions.
8. After a human review, use `PATCH /api/v1/candidates/{candidate_id}` to
   update `application_status`. Refresh/reload the candidate endpoint to check
   that the change persisted.
9. Use `GET /api/v1/openings` and `GET /api/v1/candidates` to verify the saved
   records. A fresh unused `ZECPATH_DB_PATH` gives a clean demo dataset.

Deleting a candidate or opening removes linked screening reports and redacts
resume text retained by upload-processing records. Historical processing-job
metadata remains, but its parsed text is no longer available.

The older `POST /api/v1/candidates/shortlist` endpoint is retained only as a
clearly labelled, non-persistent caller-supplied score simulation; use the
opening-specific shortlist route for saved application data.

## Tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m unittest day64_internal_review.tests.test_walkthrough -v
.\.venv\Scripts\python.exe -m unittest day65_final_enhancements_feature_polish.tests.test_day65 -v
```

The first pytest command runs the root API tests; the second runs the complete
repository suite, including each numbered stage. Root `pytest.ini` uses
`--import-mode=importlib` because separate stages reuse package and test names.
Stage tests import their source through stage-qualified package names to prevent
one stage's `src` modules from shadowing another's.

The Day 64 and Day 65 tests exercise synthetic walkthrough/report modules, not
the root API database. See their individual READMEs for limitations and
evidence. The root API tests exercise its persistence and HTTP workflows.

## Documentation and submission reports

- [Documentation index](docs/README.md) maps current guides and historical
  stage reports.
- [Daily module report catalog](docs/daily_reports.md) distinguishes stage
  prototypes from root-app integrations.
- [AI roadmap](docs/ai_roadmap.md) separates verified behavior from proposals.
- [Internship portfolio](docs/internship_portfolio.md) summarizes evidenced
  project scope and outcomes.
- [Day 68 release-readiness reports](day68_release_readiness/day68_audit_report.md)
  include the audit, bug fixes, integrations, tests, security, performance,
  final validation, and release notes.
- [Final ATS report](docs/reports/Final_ATS_Report.md) summarizes current
  status and acceptance blockers.

## Troubleshooting

- **Dashboard says "API unavailable" / "Failed to fetch":** From the repository
  root, start the FastAPI command above and leave that terminal running. Open
  the dashboard from the same origin at `http://127.0.0.1:8000/` (do not open
  `static/index.html` as a local file or use a different host/port). Confirm
  the dashboard sign-in succeeds. The frontend calls relative `/api/v1`
  routes, so no separate API URL or CORS configuration is needed.
- **Dashboard sign-in fails:** Set `ZECPATH_AUTH_USERNAME` and a unique
  `ZECPATH_AUTH_PASSWORD` of at least 16 characters in the same PowerShell
  session that starts Uvicorn, or initialize the first recruiter account with
  `.\.venv\Scripts\python.exe -m src.create_recruiter`. Missing credentials or
  an uninitialized account cause protected API requests to fail with a server
  configuration error. Five failed sign-ins from the same client address for
  that username trigger a 15-minute cooldown.
- **Sign-in expires:** Dashboard sessions last 8 hours. Sign in again after
  expiry or restart using the configured recruiter credentials.
- **Port 8000 is already in use:** Stop the server you started in its own
  terminal, or select a different Uvicorn port and open that same port in the
  browser.
- **Saved records are missing:** Check whether `ZECPATH_DB_PATH` is set in the
  current PowerShell session. Without it, records use `data/zecpath.sqlite3`.
- **Resume extraction fails:** The upload accepts TXT, DOCX, and text-based
  PDFs up to 5 MiB. Scanned PDFs need OCR, which is not included.

This application remains a local prototype. It has only one shared recruiter
credential, no role-based access or identity-provider integration, and stores
extracted resume and screening text without encryption. It must not be exposed
to a network or used with real applicant information.
