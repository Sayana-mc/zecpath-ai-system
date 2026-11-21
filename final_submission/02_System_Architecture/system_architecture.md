# System architecture

## Root runtime

```text
Browser (static/index.html, same-origin)
  ├─ POST/GET/DELETE /api/v1/auth/session
  ├─ /api/v1/openings (job CRUD)
  ├─ /api/v1/candidates (application CRUD/status)
  ├─ POST /api/v1/resumes/upload
  │    └─ size/type checks → processing_jobs → FastAPI background task
  │         └─ TXT/DOCX/PDF text extraction → Day 9-11 structured data
  ├─ POST /api/v1/candidates/score
  │    └─ Day 9-11 evidence + cached local Day 12 embeddings
  │         └─ active Day 13 weighted score → score_evidence in SQLite
  ├─ POST /api/v1/openings/{id}/shortlist
  │    └─ persisted per-opening scores; human review only
  └─ /api/v1/candidates/{id}/screening-reports
       └─ Day 25 keyword/regex notes → JSON report in SQLite
```

## Modules and boundaries

- Entry point: `src.main:app`; same process serves dashboard, API and OpenAPI.
- Router/business boundary: `src.api`; request/response validation in
  `src.schemas`; file parsing in `src.services`; structured parsers in
  `src.resume_analysis`; score orchestration in `src.integrated_scoring`.
- Persistence: `src.database`, SQLite. `ZECPATH_DB_PATH` overrides
  `data/zecpath.sqlite3`.
- Authentication: `src.auth` plus recruiter CLI scripts. Account hashes and
  sessions reside in the selected database.
- Day 16 and Day 20 are not root dependencies. Day 16's standalone API keeps
  demo behavior; Day 20 is a checklist. Day 9–13 are the only explicitly
  integrated numbered ATS stages in the score path, with Day 25 used for root
  screening annotations.

## Runtime limitations

Resume processing is an in-process background task and is marked failed on
restart if left queued/processing. It is not a durable queue. Embedding model
loading is cached within a process and configured local-only. Candidate lists
are unpaginated and include resume text. The database and applicant content
are not encrypted. This architecture is appropriate only for a local
synthetic-data demonstration, not production hiring.

See [database schema](database_schema.md),
[API inventory](api_documentation.md),
[Day 1–68 audit](day01_day68_audit.md), and
[integration evidence](day01_day68_integration_report.md).
