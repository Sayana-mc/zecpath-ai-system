# Testing and verification report

**Validation date:** 2026-11-07  
**Runtime:** repository `.venv` on Windows

## 2026-11-08 Day 1–15 implementation addendum

After the changes documented in
[`day01_day15_implementation_report.md`](day01_day15_implementation_report.md),
the complete repository suite passed **487 tests** in 171.38 seconds. A final
targeted run of the strengthened schema/profile checks passed **2 tests**;
those checks validate all ten synthetic resume profiles against the Day 4
resume schema. `git diff --check`, compile checks for changed Python modules,
and JSON parsing of the four schema files passed. The day-specific test report
records intermediate failure/fix evidence and remaining unrun checks such as
Mermaid rendering, OCR, browser regression, and fairness evaluation.

## Executed commands

| Command | Result |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest tests\test_api.py -q` | 32 passed after the latest root API changes |
| `.\.venv\Scripts\python.exe -m pytest -q` | **483 passed, 0 failed** in 99.80 seconds |
| Pylance diagnostics for touched Python files | No diagnostics in `src/api.py`, `src/database.py`, `src/integrated_scoring.py`, `src/resume_analysis.py`, `src/schemas.py`, `src/auth.py`, the recruiter setup/reset commands, or `day12_semantic_matching/src/embedding_engine.py`. |
| `git diff --check` | Passed after documentation and collection edits. |
| Node inline dashboard JavaScript parse | Passed before this documentation/Postman pass; no dashboard JavaScript changed in this pass. |
| Postman JSON and Origin-header check | Valid JSON; 20 requests; every POST/PATCH/DELETE request includes an `Origin` header. Not executed in Newman/Postman. |
| FastAPI OpenAPI check | Valid schema with 14 paths; opening/candidate detail, resume parse and screening-report routes present. |
| Updated documentation links | All relative links in the current technical-doc set resolve. |

## Real local-model check

The cached `all-MiniLM-L6-v2` model loaded locally, produced 384-element
embeddings and a cosine similarity. A root `TestClient` workflow used a
temporary SQLite database and synthetic recruiter/resume data and verified
login, HTTP-only cookie, extraction persistence, live Day 12 inference, score
persistence, logout, and HTTP 401 on a protected route. A separate local
synthetic score included skills, experience, education and semantic
components. No real candidate data or user database was used.

The no-cache path was observed to raise `OSError`; root API coverage confirms
an unavailable model returns 503 without saving a score.

## Actual browser workflow

An isolated Uvicorn instance on port 8766 and a temporary SQLite DB were used
because the shared browser's port-8000 page recorded connection-refused
events. The actual dashboard was used to sign in, create a job and candidate,
upload a synthetic TXT resume, extract it, score it, refresh/reload persisted
state, rank the candidate, generate and retrieve a screening report, update
status, sign out, and verify protected-route 401. The browser showed score
77.6% and shortlist rank 1 for that synthetic fixture. Database inspection
confirmed one job, candidate, report and saved score. Test server/data were
stopped/removed after verification.

## Limits

The suite includes many stage-local unit tests; those tests do not establish
root integration. Browser validation was one synthetic scenario, not a
cross-browser, multi-job stress or production deployment test. No Newman/
Postman collection run, dependency vulnerability scan, external security
review, fair-hiring validation, concurrency/load test, OCR test, or restore
drill was performed.
