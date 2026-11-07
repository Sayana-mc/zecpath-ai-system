# Day 1–68 integration and verification report

**Date:** 2026-11-07  
**Primary application:** `src.main:app`  
**Scope:** Root recruiter app and Day 1–68 feature wiring. This report does not
certify production readiness or imply that a folder's presence proves a
feature.

## Architecture decision

The root FastAPI application is the only supported recruiter runtime. It serves
the HTML dashboard and exposes one versioned API under `/api/v1`; the same
SQLite database backs the recruiter session, openings, candidate applications,
resume processing records, scores and screening notes. Historical `day*`
packages are stage exercises or documentation unless an explicit import from
the root source proves otherwise.

The root scorer uses Day 9–11 rule-based extraction, Day 12 local embedding
similarity, and the active Day 13 weighted score implementation. It does not
use a Day 20 score engine: none was found. The Day 16 standalone API is not
mounted and is not the root API.

## Active root API inventory

All endpoints below are generated in Swagger at `/docs`; `/redoc` and
`/openapi.json` are also available. Every endpoint except health, session
status and login requires recruiter authentication. Cookie-authenticated
mutations require same-origin `Origin`.

| Method | Path | Purpose | Access / key response |
|---|---|---|---|
| GET | `/` | Serve dashboard | Public HTML |
| GET | `/api/v1/health` | Health and DB probe | Public; never returns credentials |
| POST | `/api/v1/auth/session` | Recruiter login | Public; returns session status and sets HTTP-only cookie |
| GET | `/api/v1/auth/session` | Session status | Public; reports authenticated boolean |
| DELETE | `/api/v1/auth/session` | Revoke/logout | Authenticated; 204 |
| POST | `/api/v1/openings` | Create opening | 201; generated UUID |
| GET | `/api/v1/openings` | List/filter openings | Authenticated |
| GET | `/api/v1/openings/{opening_id}` | Get opening | Authenticated |
| PATCH | `/api/v1/openings/{opening_id}` | Edit requirements/details/status | Authenticated; invalidates score evidence when score inputs change |
| DELETE | `/api/v1/openings/{opening_id}` | Delete opening and cascaded applications | Authenticated; 204 |
| POST | `/api/v1/candidates` | Register candidate | 201; generated UUID; job must exist and be open |
| GET | `/api/v1/candidates` | List/filter applications | Authenticated; unpaginated |
| GET | `/api/v1/candidates/{candidate_id}` | Get candidate | Authenticated |
| PATCH | `/api/v1/candidates/{candidate_id}` | Edit profile/status | Authenticated |
| DELETE | `/api/v1/candidates/{candidate_id}` | Delete application and linked reports | Authenticated; 204 |
| POST | `/api/v1/resumes/upload` | Validate/queue resume | Authenticated; 202 |
| GET | `/api/v1/jobs/{job_id}` | Processing state/result | Authenticated |
| POST | `/api/v1/resumes/parse` | Retrieve parsed text and structured data | Authenticated |
| POST | `/api/v1/candidates/score` | Persist weighted job-specific score | Authenticated; component evidence and rank |
| POST | `/api/v1/openings/{opening_id}/shortlist` | Rank persisted scores for one opening | Authenticated; review-only suggestions |
| POST | `/api/v1/candidates/shortlist` | Legacy caller-supplied score simulation | Authenticated; explicitly `simulation_only` |
| POST | `/api/v1/candidates/{candidate_id}/screening-reports` | Build Day 25 rule-based report | Authenticated; 201 |
| GET | `/api/v1/candidates/{candidate_id}/screening-reports` | Retrieve saved reports | Authenticated |

There is no standalone root ranking endpoint, eligibility endpoint, voice
interview endpoint, Day 26 screening-score endpoint, or Day 28 comprehensive
report endpoint. Job-specific ranking is returned by scoring and shortlist
responses.

## Root data model

| Table | Use | Integrity notes |
|---|---|---|
| `openings` | Job data, skill lists, optional education/experience requirements, state and timestamps | UUID primary key; status check |
| `candidates` | Candidate application, resume text/data, status, saved score/evidence | Job FK with cascade; unique `(opening_id, email)`; status check |
| `processing_jobs` | Resume job status, result/error and source filename | Job UUID; candidate ID is nullable and not an enforced FK |
| `screening_reports` | JSON report linked to candidate and opening | Both FKs cascade |
| `recruiter_accounts` | Single recruiter name, random salt and PBKDF2 hash | Username primary key |
| `recruiter_sessions` | SHA-256 token hash, username and expiry | No FK to account; validation checks current account |
| `recruiter_login_attempts` | Hashed throttle key and failure window | Throttled by client host/username key |

New `minimum_education`, `minimum_years_experience` and `resume_data` fields
are added with additive SQLite `ALTER TABLE` checks. No existing records are
deleted. This is a lightweight startup migration, not a versioned migration
framework.

## Verified root flows

An isolated browser run used a generated local database, an ephemeral
synthetic recruiter, one synthetic opening and one synthetic TXT resume:

1. Login succeeded and the HTTP-only session restored after page reload.
2. The dashboard created the job and candidate, uploaded and extracted the
   resume, then saved a Day 9–13 score (77.6% in this synthetic run).
3. The dashboard displayed component evidence, ranked the saved candidate,
   generated a Day 25 screening report, and changed status to `IN_REVIEW`.
4. After reload, the row showed the saved score/status and the report could be
   retrieved.
5. Logout returned the UI to sign-in; a subsequent protected API request
   returned HTTP 401.
6. No browser JavaScript page errors were observed during the first scoring
   flow. The browser's expected protected-route probe logged a 401 after
   logout.

The isolated SQLite database contained one opening, one candidate, one report
and a non-null score at verification. It was temporary and was removed after
the run. This does not verify the currently shared port-8000 service: the
shared page reported connection-refused events. No user database was read or
changed.

## Final verification gates

| Gate | Status | Evidence / remaining limitation |
|---|---|---|
| G1 Day 1–68 inventory | PARTIAL | Folder-by-folder inventory and module/test counts are documented in the audit. An exhaustive file-by-file review of every historical source file was not completed; historical status remains prototype unless directly integrated. |
| G2 Root app starts | PASS | Isolated Uvicorn instance on port 8766 returned healthy; browser loaded root dashboard. Port 8000 was not claimed live. |
| G3 First recruiter account | PASS | Synthetic account creation against isolated SQLite; PBKDF2 account tests passed. |
| G4 Login/logout | PASS | Browser login, session restore, sign-out and protected route HTTP 401; API session tests. |
| G5 Job CRUD | PASS | Root API tests; browser created job with requirements. |
| G6 Candidate CRUD | PASS | Root API tests; browser registered and updated synthetic candidate status. |
| G7 Resume upload | PASS | TXT browser flow; root API tests cover TXT/DOCX/PDF, size, empty, unsupported and MIME mismatch. |
| G8 Resume parsing | PASS | Structured extraction and processing-state API tests; browser showed extracted data. Scanned-image OCR is absent. |
| G9 Structured persistence | PASS | Browser refresh and isolated database verified persisted resume data and score. |
| G10 Semantic model | PASS (local) | Cached 384-dimensional model loaded and produced cosine similarity; tested against synthetic resume. Offline cache still required. |
| G11 Weighted ATS score | PASS (root scope) | Day 13 component scorer and configured weights; targeted API suite passes. Not validated for hiring decisions. |
| G12 Score explanation | PASS (root scope) | API returns component inputs/reasons, weights and contributions; UI displays evidence. |
| G13 Candidate ranking | PASS (job-scoped) | Root rank/shortlist use saved scores and one opening; no separate rank endpoint/history table. |
| G14 Shortlisting | PASS | Browser returned ranked review suggestion without changing status; API tests cover saved shortlist. |
| G15 HR screening | PARTIAL | Day 25 intent annotations/report persistence work; no Day 22 question bank or Day 26 evaluation integration. |
| G16 Reports | PARTIAL | Day 25 report created/retrieved in UI; Day 28 comprehensive reports are not root-integrated. |
| G17 Swagger | PASS (schema) | FastAPI OpenAPI schema enumerates root route operations; interactive Swagger is served by FastAPI. No separate manual Swagger interaction was claimed. |
| G18 Postman | PARTIAL | Collection/environment JSON validate and contain blank credentials; not executed in Postman/Newman. |
| G19 Frontend/backend | PASS (synthetic root path) | Actual browser login → job → candidate → resume → score → shortlist → screening → status → refresh → logout workflow. |
| G20 Database integrity | PASS (tested scope) | SQLite constraints, additive migration, persistence and cascade behaviors have root tests; not a production concurrency/restore certification. |
| G21 Security | PARTIAL | Password/session/CSRF-style origin checks, auth denial, upload limits/type consistency and safe errors tested. No external security review, TLS deployment, encryption, RBAC or tenant isolation. |
| G22 Regression suite | PASS | Full pytest suite: 483 passed, 0 failed (after the current integration changes). |
| G23 End-to-end | PASS (one synthetic browser scenario) | Full workflow above; not a multi-job, many-candidate/browser compatibility matrix. |
| G24 Documentation | PASS (local demo scope) | README, API, setup, schema, score, resume, limitation, audit and integration docs updated; limitations stated. |

## Remaining blockers to a complete integrated platform

The application remains a local single-recruiter demo. Eligibility, transcript
and audio, interview, behavior indicators, Day 26 screening scores, Day 28 full
reports, cross-round scoring, fairness, and governance prototypes are not
connected to the root data/API/UI. The root does not parse contact details,
certifications, projects, or achievements into structured data. It has no OCR,
durable task queue/retries, pagination, versioned migrations, applicant-data
encryption, retention workflow, production monitoring, or tested backup
restore. Neither the Day 13 model/weights nor the root score is a validated
employment assessment.
