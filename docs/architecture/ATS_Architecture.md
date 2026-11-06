# Verified root application architecture

## Scope

This document describes the runnable application in this repository. It does
not describe every numbered stage package as a deployed service.

## Runtime components

```text
Browser
  └── GET / (static/index.html; same origin)
       ├── /api/v1/auth/session (login/status/logout)
       ├── /api/v1/openings (job CRUD)
       ├── /api/v1/candidates (application CRUD)
       ├── /api/v1/resumes/upload
       │    └── FastAPI background task → parser → SQLite job/candidate data
       ├── /api/v1/candidates/score
       │    └── exact required-skill overlap → evidence + persisted score
       ├── /api/v1/openings/{id}/shortlist
       │    └── saved score review suggestions (no status change)
       └── /api/v1/candidates/{id}/screening-reports
            └── Day 25 keyword/regex rules → persisted review notes
```

## Entrypoints and configuration

- ASGI application: `src.main:app`.
- Startup: `.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000`.
- Dashboard: `static/index.html`, served by the FastAPI root route.
- API routers and request processing: `src/api.py`.
- Matching and resume parsing: `src/services.py` and `ats_engine/`.
- Database: `src/database.py`; SQLite path defaults to `data/zecpath.sqlite3`,
  overridable with `ZECPATH_DB_PATH`.
- Schemas: `src/schemas.py`; first-account setup:
  `python -m src.create_recruiter`.

FastAPI lifespan initializes the tables and marks any queued/processing resume
jobs as failed on a process restart. The schema uses `CREATE TABLE IF NOT
EXISTS`; there is no versioned migration system.

## Authentication and trust boundaries

Database-backed recruiter sessions use random opaque tokens; only SHA-256
token hashes are saved. The browser cookie is HttpOnly, SameSite=Strict, and
expires after eight hours. Session-authenticated writes require the exact
same-origin `Origin`. The API retains HTTP Basic for compatibility. Legacy
environment credentials are not stored as password hashes and should remain
local-only. Do not expose this prototype to a network or use real applicant
records.

## Explicitly separate modules

Day 21 eligibility, Day 23 transcript normalization, Day 24 Faster-Whisper,
Day 26 screening scoring, Day 28 comprehensive report generation, Day 15
fairness, and Day 64/65 synthetic walkthroughs are not invoked by the root API.
See the [integration matrix](../../day68_release_readiness/day68_integration_report.md).