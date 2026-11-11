# Zecpath AI Hiring System

Zecpath is a collection of ATS experiments and hiring-pipeline prototypes, plus
a small local recruiter API. The root API is the runnable application surface;
the numbered `day*` folders are learning, evaluation, and simulation modules
and are not all wired into that API.

## What the local API supports

- Create, list, edit, close, and delete job openings.
- Register, list, edit, track, and delete candidate applications.
- Protect API operations with a single SQLite-backed recruiter account. The
  dashboard receives an HTTP-only session cookie that survives page reloads
  and expires after 8 hours; direct API clients may continue to use HTTP Basic
  authentication.
- Upload TXT, DOCX, and text-based PDF resumes (up to 5 MiB) and extract text.
- Review the saved extracted resume text and the exact snippets used by matching.
- Persist application, processing, score, and review data in SQLite.
- Extract sections, skills, education, certifications, and dated work history
  with the existing Day 8-11 parsers; persist the structured profile with the
  candidate record.
- Calculate a transparent weighted score using Day 8-11 extracted evidence,
  Day 12 local sentence embeddings when a resume is present, and the active Day
  13 scoring formula. The response includes component evidence, weights,
  contributions, missing-input reasons, classification, and rank.
- Clear saved scores and evidence when score inputs change, including candidate
  name/skills/resume and job title, description, requirements, or preferred
  skills; affected applications must be rescored before shortlist suggestions.
- Rank previously scored applications for a job as a recruiter review aid.
- Parse explicitly labeled job-description requirement sections for recruiter
  confirmation; parsing does not update an opening automatically.
- Configure and retrieve per-opening eligibility rules and candidate
  evaluations. Missing information is surfaced for human review; evaluation
  never changes application status.
- Retrieve the available screening question bank and persist manual/imported
  screening sessions, transcript segments, and question interactions.
- Run complete Day 24–32 voice and text screening workflows:
  - Upload audio (WAV, MP3, M4A, OGG, FLAC) with size/MIME validation.
  - Transcribe and clean transcripts (filler removal, deduplication, punctuation).
  - Understand candidate answers with 9 intent classifications and structured entity extraction.
  - Multi-parameter answer scoring (clarity, relevance, completeness, consistency).
  - Behavioral signal analysis (hesitation markers, pacing, sentiment, contradiction detection).
  - Conversational FSM state machine with silence and confusion handling.
  - End-to-end recruiter screening report generation with JSON and HTML artifacts.
- Run complete Day 33–40 structured HR Interview workflows:
  - Role-specific question generation differentiating fresher vs. experienced candidates.
  - Dynamic follow-up question engine adapting to candidate answers.
  - Communication skills evaluation with filler word detection and pacing analysis.
  - Reasoning and situational judgment aptitude assessments.
  - 11-section comprehensive recruiter HR interview summary reports.
- Run complete Day 41–52 Advanced Multi-Round AI Evaluation & Final Decisioning workflows:
  - Unified 5-round cross-round scoring engine (ATS, HR Screening, HR Interview, Technical Interview, Machine Test) with role-based weights and `exclude_and_renormalize` policy for missing rounds.
  - Stability and anomaly detection flagging cross-round score divergences.
  - Ethics, demographic signal scrubber (`[REDACTED_DEMOGRAPHIC]`), consent verification, and 180-day retention management.
  - Technical Interview system with role-skill mapping, experience-level question banks, 5-dimension rubric, and depth classification (`shallow`, `moderate`, `deep`).
  - Consented behavioral observation consistency indexing with non-binding assistive disclaimer.
  - Consented environment and browser integrity monitoring with non-punitive review alerts and zero automatic rejection safeguard.
  - Machine test assignment across 4 task archetypes and 5-dimension rubric evaluation.
  - Explainable final recommendation AI (`SELECTED`, `HOLD_REVIEW`, `REJECTED`) with evidence completeness confidence and auditable rationale.
  - Recruiter human review decision workflow (`APPROVED`, `OVERRIDDEN`, `REJECTED`).
- Run complete Day 53–60 Intelligence, Governance, Simulation & Scalability workflows:
  - Comprehensive Hiring Intelligence Report Generator compiling 15 evaluation dimensions, with Markdown and responsive standalone HTML export.
  - Report versioning and historical tracking (`1.0`, `1.1`, etc.).
  - Optimization metrics engine computing threshold confusion matrices (TP, FP, TN, FN), precision, recall, and F1 scores.
  - Cross-round contradiction detection with severity ratings and ambiguous answer intent clarification.
  - Cryptographic audit logging with SHA-256 hash chaining, tamper detection, and RBAC permission checks.
  - 15-stage end-to-end recruitment lifecycle simulation pipeline with AI vs. human benchmark comparison.
  - Growth-oriented candidate AI coaching with preparation guidance and strict anti-emotion/anti-rejection guardrails.
  - High-throughput batch resume processing with bounded async chunking, in-memory LRU/TTL caching, and concurrent latency benchmarking.
- Run complete Day 61–70 Observability, Final Validation, Presentation & Handover:
  - Real-Time AI Monitoring & Observability engine with privacy-safe JSONL telemetry, rolling metrics buffers, P95 latency tracking, and dashboard KPI cards.
  - 30-section Technical Master Handbook (`docs/ZecPath_AI_Technical_Handbook.md`) and Developer Onboarding Guide (`docs/DEVELOPER_ONBOARDING.md`).
  - Realistic Demo Dataset with 4 job requisitions, 8 candidate archetypes, resumes, and automated SQLite seeding (`python -m src.init_demo_data`).
  - Complete 21-slide executive presentation deck, live demo script, and expected results matrix in `presentation/`.
  - 15-point pre-demo verification checklist, stakeholder Q&A guide, and emergency recovery playbooks.
  - Full-system bug fixing, pure ASGI observability middleware, and 100% regression test pass.
  - Long-term 2027+ AI Roadmap, final internship report, and handover checklist in `submission/`.
- Save rule-based screening-answer notes and review flags.
- Use interactive API documentation at `/docs`.

The scoring method is an experimental heuristic, not a validated employment
model or a recommendation to reject a candidate. Day 12 inference runs locally
from the `all-MiniLM-L6-v2` model cache; no resume text or scoring request is
sent to an external AI service. Contact details and common labeled personal
attributes are excluded from semantic matching input, but this is not complete
de-identification or a fairness guarantee. Missing evidence is reported and
contributes zero under the existing Day 13 normalization. Every score and
shortlist requires human review.
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
- `sentence-transformers` for local Day 12 embedding inference; the model must
  already be cached before scoring candidates with resumes.
- A same-origin HTML/CSS/JavaScript dashboard in `static/index.html`.
- Pytest and HTTPX for root and repository testing.
- `jsonschema` for validating the documented Day 4 JSON Schema contracts.

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
There is no shipped/default recruiter username or password.

To replace a forgotten username or password, stop the server and run:

```powershell
.\.venv\Scripts\python.exe -m src.reset_recruiter
```

The reset prompts for a new username and password without echoing the
password, stores a new salted hash, and revokes existing sessions. Passwords
cannot be recovered or displayed. If `ZECPATH_DB_PATH` is set, set it to the
same database path before account creation, reset, and server startup.

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

### Use the recruiter dashboard

1. Open `http://127.0.0.1:8000/` and sign in with the username and password
   chosen during first-account setup. The dashboard and API share this
   same-origin FastAPI server and its `ZECPATH_DB_PATH` database.
2. Use **Create a job opening** to add a title and required skills. The
   **Manage opening** form lets you update or close the selected opening.
3. Use **Register candidate** to enter a candidate and either reported skills
   or a resume file. TXT, DOCX, and text-based PDF resumes are extracted and
   saved with the candidate record, including structured skills, education,
   and detectable work history. Job openings can optionally include minimum
   education and years of experience.
4. In **Applications**, choose **Score** to combine Day 8-11 parsed evidence,
   local Day 12 resume/job similarity when available, and Day 13's weighted
   formula. Expand **Review score evidence**, **Review component scores**, and
   **Review extracted resume details** to inspect inputs, missing components,
   weights, and contributions. Use **Rank scored candidates** for review-only
   shortlist suggestions.
5. Expand **Screening report** on a candidate row, submit a question and
   answer, then review the saved rule-based report. Screening notes and scores
   are not automated hiring decisions; retain human review.
6. Use **Refresh data** or reload the browser to retrieve persisted openings,
   candidates, scores, and screening reports. **Sign out** revokes the session;
   protected API data is unavailable until you sign in again.

The standalone Day 16 API remains a separate demo, not the root app's runtime.
The root eligibility and transcript features are review/storage interfaces,
not automated employment decisions or voice AI. There is no independent
executable Day 20 scorer; the root uses the existing Day 9–13 weighted scorer.
See the [Days 16–23 implementation report](docs/day16_day23_implementation_report.md)
and [audit](docs/day16_day23_implementation_audit.md).

### Environment configuration

| Variable | Required | Purpose |
|---|---:|---|
| `ZECPATH_DB_PATH` | No | SQLite file path. Defaults to `data/zecpath.sqlite3`. Set it before both account initialization and server startup. |

Authentication uses only salted password hashes stored in SQLite; plaintext
environment-variable credentials are not supported. No `.env` file is loaded
by the application. Use a unique temporary database for a clean synthetic
demo.

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
| Match score | `POST /api/v1/candidates/score` | Protected; Day 8-13 evidence, local Day 12 semantics when a resume is present, and Day 13 weighted score. |
| Shortlist suggestions | `POST /api/v1/openings/{opening_id}/shortlist` | Protected; uses saved scores and does not change candidate status. |
| Screening notes | `POST/GET /api/v1/candidates/{candidate_id}/screening-reports` | Protected; rule-based notes, not an assessment score. |
| JD parsing | `POST /api/v1/openings/parse-description` | Protected; explicit headings only; recruiter confirmation required. |
| Eligibility | `/api/v1/openings/{opening_id}/eligibility-config` and `/api/v1/candidates/{candidate_id}/eligibility` | Protected; versioned rules, human review required. |
| Screening questions | `GET /api/v1/screening/questions` | Protected; returns existing questions and available translations only. |
| Transcript data | `/api/v1/screening/sessions` and nested `/segments` and `/interactions` routes | Protected; manual/import persistence; no audio or speech AI. |

Browser session-authenticated POST/PATCH/DELETE requests must have a matching
same-origin `Origin` header. Direct API clients can use HTTP Basic; use it only
over TLS outside localhost.

Use the browser URL matching the port in the Uvicorn command. The documented
command above uses port 8000; opening a page on port 8765 will not connect to
that server. If you intentionally change the port, change the Uvicorn
`--port` value and browser URL together. The page uses same-origin relative
API routes, so the UI and API always use the selected port together.

The API creates `data/zecpath.sqlite3` on first start. To use a different local
database, set the path before launching:

```powershell
$env:ZECPATH_DB_PATH = "$PWD\data\live-demo.sqlite3"
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Set `ZECPATH_DB_PATH` before running the first-recruiter initializer as well,
so the account and application use the same database. Set it before the reset
command as well. Unset the variable to return to the default path. No external
service keys are required. The application does not ship with a recruiter
username or password. Login sessions are stored as SHA-256 token hashes in the
selected SQLite database, use an HTTP-only, SameSite=Strict cookie, expire
after 8 hours, and are revoked on sign-out or credential reset. Five failed
logins for a username and client address are throttled for 15 minutes.
Session-authenticated writes require a same-origin `Origin` header. The API
also retains HTTP Basic for direct clients; Basic authentication must only be
used over TLS if reachable through a network-facing proxy.

Keep the service bound to localhost. The single shared recruiter credential is
not a substitute for an identity provider, multiple recruiter accounts, or
account lifecycle management. The SQLite database and extracted
resume/screening text remain unencrypted; do not use real applicant data or
expose this prototype to a network. Production use requires, at minimum, a
security review, TLS, encryption/key management, access controls, consent and
retention policies, audit logging, migration tooling, backups, and deployment
hardening.

## Local database backup and restore

The application currently has no automated backup or versioned migration
command. Startup applies additive schema changes for newer root API fields.
For a local demo, stop Uvicorn before copying the configured SQLite database:

```powershell
Copy-Item .\data\zecpath.sqlite3 .\data\zecpath.sqlite3.backup
```

Keep the backup outside any publicly served directory and verify it exists
before replacing a database. To restore, stop Uvicorn, preserve the current
database under a different name, then copy the verified backup to the exact
configured database path. These file-copy instructions are only appropriate
for a stopped local SQLite application; they are not a production backup or
recovery plan. Schema creation and additive column upgrades are automatic but
are not versioned migrations.

## Repeatable synthetic demo

The repository includes [data/demo_resume.txt](data/demo_resume.txt), a
fictional text resume. Use only synthetic data:

1. In `/docs`, call `POST /api/v1/openings` with a title, description, required
   skills `["Python", "SQL", "Git"]`, optional preferred skills, and optional
   `minimum_education` / `minimum_years_experience`. Save the returned
   `opening_id`.
2. Call `POST /api/v1/candidates` with a synthetic name/email, that
   `opening_id`, and an empty `skills` list. Save the returned `candidate_id`.
3. Call `POST /api/v1/resumes/upload`, set `candidate_id`, and select
   `data/demo_resume.txt`. The response contains a processing `job_id`.
4. Call `GET /api/v1/jobs/{job_id}` to verify `COMPLETED`, then
   `GET /api/v1/candidates/{candidate_id}` to inspect the saved extracted text.
5. Call `POST /api/v1/candidates/score` with the opening and candidate IDs.
   Review component scores, unavailable-input reasons, weights, contributions,
   extracted evidence, rank, and the `human_review_required` flag. Resume
   semantic scoring uses a locally cached Day 12 model. To cache it explicitly,
   run `.\.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`
   once while online, before running scoring.
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

- [Day 1–15 complete implementation report](docs/day01_day15_complete_implementation_report.md)
  provides the comprehensive verification of Days 1 through 15 across the root
  application and test suites.
- [Day 1–15 task-level audit](docs/day01_day15_implementation_audit.md),
  [implementation report](docs/day01_day15_implementation_report.md),
  [test report](docs/day01_day15_test_report.md), and
  [known limitations](docs/day01_day15_known_limitations.md). These mark the
  unavailable PRD and other blockers explicitly; they do not claim all
  requirements are complete.
- [Day 1–15 progress checkpoint](docs/day01_day15_implementation_progress.md)
  records remaining work.
- [Synthetic Day 4 resume/JD samples](datasets/test/) are isolated test data
  and are never loaded into the application database.
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
- [Day 16/20 integration and verification report](docs/day16_day20_integration.md)
- [Days 16–23 implementation audit](docs/day16_day23_implementation_audit.md)
- [Days 16–23 implementation report](docs/day16_day23_implementation_report.md)
- [Days 16–23 test report](docs/day16_day23_test_report.md)
- [Days 16–23 known limitations](docs/day16_day23_known_limitations.md)
- [Days 24–32 implementation report](docs/day24_day32_implementation_report.md)
- [Days 24–32 API documentation](docs/day24_day32_api_documentation.md)
- [Days 24–32 database changes](docs/day24_day32_database_changes.md)
- [Days 33–40 implementation report](docs/day33_day40_implementation_report.md)
- [Days 33–40 system architecture](docs/day33_day40_architecture.md)
- [Days 33–40 API documentation](docs/day33_day40_api_documentation.md)
- [Days 33–40 database changes](docs/day33_day40_database_changes.md)
- [Days 33–40 scoring methodology](docs/day33_day40_scoring_methodology.md)
- [Days 33–40 test report](docs/day33_day40_testing_report.md)
- [Days 33–40 demo guide](docs/day33_day40_demo_guide.md)
- [Days 33–40 known limitations](docs/day33_day40_known_limitations.md)
- [Days 33–40 final verification report](docs/day33_day40_final_verification_report.md)
- [Days 41–52 implementation report](docs/day41_day52_implementation_report.md)
- [Days 41–52 architecture documentation](docs/day41_day52_architecture.md)
- [Days 41–52 API documentation](docs/day41_day52_api_documentation.md)
- [Days 41–52 testing report](docs/day41_day52_testing_report.md)
- [Days 53–60 audit report](docs/day53_day60_audit_report.md)
- [Days 53–60 implementation report](docs/day53_day60_implementation_report.md)
- [Days 53–60 testing report](docs/day53_day60_testing_report.md)
- [Days 53–60 hiring intelligence report documentation](docs/day53_day60_hiring_report_documentation.md)
- [Days 53–60 security and governance](docs/day53_day60_security_governance.md)
- [Days 53–60 API integration](docs/day53_day60_api_integration.md)
- [Days 53–60 performance and scalability report](docs/day53_day60_performance_report.md)
- [Days 53–60 candidate AI coaching and future roadmap](docs/day53_day60_future_roadmap.md)
  documents the actual root endpoints, Day 8-13 scoring flow, and integration
  limits.
- [Day 61 AI Monitoring & Observability](docs/day61_ai_observability.md)
- [Day 62 ZecPath AI Technical Handbook](docs/ZecPath_AI_Technical_Handbook.md)
- [Day 62 Developer Onboarding Guide](docs/DEVELOPER_ONBOARDING.md)
- [Day 63 Demo Dataset Creation](docs/day63_demo_dataset.md)
- [Day 64 Internal Review Report](docs/day64_internal_review_report.md)
- [Day 65 Final Enhancements Report](docs/day65_final_enhancements.md)
- [Day 66 Live Demo Script](presentation/demo_script.md)
- [Day 66 Expected Demo Results Matrix](presentation/expected_demo_results.md)
- [Day 66 Executive Presentation Deck](presentation/presentation_slides.md)
- [Day 67 Pre-Flight Demo Checklist](presentation/mock_demo_checklist.md)
- [Day 67 Stakeholder Q&A Guide](presentation/stakeholder_qa.md)
- [Day 67 Demo Readiness Report](docs/day67_demo_readiness.md)
- [Day 68 Bug-Fix & Optimization Report](docs/day68_bug_fix_report.md)
- [Day 68 Final Validation Sign-Off](docs/day68_final_validation.md)
- [Day 69 Long-Term AI Roadmap (2027+)](docs/AI_ROADMAP.md)
- [Day 69 Internship Portfolio Summary](submission/portfolio_summary.md)
- [Day 70 Final Internship Report](submission/FINAL_INTERNSHIP_REPORT.md)
- [Day 70 Handover Checklist](submission/handover_checklist.md)
- [Days 61–70 Completion Report](docs/DAYS_61_70_COMPLETION_REPORT.md)
- Import the [Postman collection](postman/ZecPath%20Recruiter%20API.postman_collection.json)
  and [local environment](postman/ZecPath%20Local.postman_environment.json)
  for synthetic HTTP API checks. Set the recruiter credentials locally and do
  not export or share an environment containing real credentials.

## Troubleshooting

- **Dashboard says "API unavailable" / "Failed to fetch":** From the repository
  root, start the FastAPI command above and leave that terminal running. Open
  the dashboard from the same origin at `http://127.0.0.1:8000/` (do not open
  `static/index.html` as a local file or use a different host/port). Confirm
  the dashboard sign-in succeeds. The frontend calls relative `/api/v1`
  routes, so no separate API URL or CORS configuration is needed.
- **Dashboard sign-in fails:** Create the first account with
  `.\.venv\Scripts\python.exe -m src.create_recruiter`. If you have forgotten
  the username or password, stop Uvicorn and run
  `.\.venv\Scripts\python.exe -m src.reset_recruiter` to replace both. Confirm
  that the browser URL uses the same port as the active Uvicorn command and
  that both commands use the same `ZECPATH_DB_PATH`, if configured. Five failed
  sign-ins for a username/client address trigger a 15-minute cooldown.
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
