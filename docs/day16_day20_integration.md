# Day 16 API and Day 20 scoring integration

## What is actually integrated

The runnable recruiter application is `src.main:app`, with its routes in
`src/api.py`, SQLite persistence in `src/database.py`, and same-origin UI in
`static/index.html`. Its authenticated API now provides job/candidate CRUD,
resume upload and text extraction, structured resume extraction, scoring,
shortlist suggestions, and screening reports.

The standalone Day 16 module
(`day16_ats_api_design_integration/src/api.py`) is a separate demo. Its resume
upload route records the upload's filename and size; it does not persist
applications or extract resume text. Its `/api/v1/scoring` route receives
caller-supplied candidate/job data. It is not mounted in the recruiter app and
must not be mistaken for the root application's API.

No executable Day 20 scoring engine was found. The Day 20 folder contains a
production-readiness checklist, not a scorer. The root integration therefore
uses the existing Day 13 scorer rather than inventing or claiming a Day 20
implementation:

1. Day 9 extracts rule-based resume skills.
2. Day 10 extracts work-history records and detectable duration.
3. Day 11 extracts education records.
4. Day 12 creates local `all-MiniLM-L6-v2` embeddings and cosine similarity
   for resumes with readable text.
5. Day 13 combines normalized component scores using its existing role
   weights.

Uploads continue to be extracted by the root service, and the original file is
removed after processing. Parsed text and structured extraction are stored
with the application; existing databases receive additive columns at startup.
The resume/job association is checked before scoring. A job edit or a change
to candidate scoring evidence invalidates the saved score and breakdown.

## Score contract and limitations

`POST /api/v1/candidates/score` returns the saved score, job/candidate IDs and
names, matching/missing skills, education and experience evidence, component
scores and reasons, the role weights, weighted contributions, classification,
candidate rank, and `human_review_required: true`. The same evidence is
persisted with the candidate and is available after page refresh.

The active Day 13 scorer loads weights from
`day13_ats_scoring/src/weight_manager.py`. The adjacent JSON weight files are
not loaded by that implementation and conflict for some roles. The integration
preserves the active scorer's values instead of silently selecting or
rewriting a different configuration. Unknown role titles use Day 13's default
weights. The selected values are returned in each score's evidence.

Unavailable experience, education, or semantic evidence remains marked
unavailable in the component evidence. Day 13's current normalization treats
unavailable components as zero contribution; this is not evidence that a
candidate lacks the qualification. The Day 12 model is loaded with
`local_files_only=True`; a missing dependency/model produces HTTP 503 rather
than a fabricated semantic score. Candidate rankings are review suggestions,
not hiring decisions. The model and score are not validated employment
assessments.

## Root API verification matrix

| Workflow | Root endpoint(s) | Verification |
|---|---|---|
| Static dashboard and database health | `GET /`, `GET /api/v1/health` | Root API tests verify the page, health response, and configured recruiter auth state. |
| Recruiter session and protected routes | `/api/v1/auth/session`; protected `/api/v1/*` routes | Root API tests verify login, cookie-backed session, unauthenticated denial, logout, and session revocation on password reset. |
| Job create/list/edit/delete | `/api/v1/openings` and `/api/v1/openings/{opening_id}` | Root API tests exercise CRUD, candidate associations, score invalidation, and schema migration of newly added requirements. |
| Candidate create/list/edit/delete | `/api/v1/candidates` and `/api/v1/candidates/{candidate_id}` | Root API tests exercise CRUD, validation, duplicate handling, persistence, and job association checks. |
| Resume upload/extraction | `POST /api/v1/resumes/upload`, `GET /api/v1/jobs/{job_id}`, `POST /api/v1/resumes/parse` | Root API tests cover TXT, DOCX, and PDF extraction, structured extraction persistence, upload failure, and candidate deletion during processing. |
| Weighted score | `POST /api/v1/candidates/score` | Root API tests exercise the HTTP contract with deterministic embedding fixtures; a separate runtime check loaded the cached Day 12 model and calculated all four Day 13 components on synthetic input. |
| Ranking/shortlist | `POST /api/v1/openings/{opening_id}/shortlist` | Root API tests verify persisted-score ranking and that shortlist generation does not change application status. |
| HR screening notes | `POST/GET /api/v1/candidates/{candidate_id}/screening-reports` | Root API tests exercise report persistence and retrieval. |

The imported Postman collection exercises the same root API (not the
standalone Day 16 demo). It uses the configured local server on port 8000 and
keeps credential values blank in the exported environment. Select a synthetic
resume file in Postman for the upload request. Do not export or share an
environment after entering a real password.

## Validation evidence

- `.\.venv\Scripts\python.exe -m pytest tests\test_api.py -q`: **31 passed**.
- `.\.venv\Scripts\python.exe -m pytest -q`: **483 passed** in the latest full
  suite after adding the semantic-job-input test and MIME consistency check.
- An isolated FastAPI `TestClient` workflow used a temporary SQLite database,
  a generated synthetic recruiter credential, and a synthetic TXT resume. It
  passed login and HTTP-only cookie checks, resume extraction, persisted
  candidate retrieval (refresh-equivalent), real local Day 12 model scoring,
  score persistence, logout, and protected-route denial. The observed
  synthetic score was 61.89; no applicant data or credentials were used.
- The locally cached Day 12 model produced 384-dimensional embeddings and a
  numeric cosine similarity. The no-cache path was also checked to fail
  explicitly, and API tests verify that model unavailability returns HTTP 503
  without persisting a score.
- Dashboard inline JavaScript parsed successfully with Node, and both Postman
  exports parsed as JSON. The Postman collection itself was not executed in
  Postman.

## Running the local model check

After installing the root requirements, cache the model while online:

```powershell
.\.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

Inference in the application is local-only. Check the root README for account
setup, the exact port-8000 startup command, synthetic demo steps, and test
commands.
