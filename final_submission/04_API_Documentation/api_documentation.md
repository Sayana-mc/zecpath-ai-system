# Root API reference

The FastAPI root application is the sole supported recruiter API:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

The route declarations and Pydantic request/response schemas in `src/api.py`
and `src/schemas.py` generate these documents. Prefix: `/api/v1`.

## Authentication

`GET /api/v1/health`, `POST /api/v1/auth/session`, and
`GET /api/v1/auth/session` are public. Login sets an HTTP-only, SameSite=Strict
cookie with an eight-hour lifetime. `DELETE /api/v1/auth/session` and all ATS
routes require an authenticated recruiter. Cookie-authenticated writes require
an exact same-origin `Origin` header. HTTP Basic remains available for direct
API clients; use only locally or over TLS.

## Operations

| Method | Route | Request / response |
|---|---|---|
| GET | `/api/v1/health` | Public health/database status |
| POST / GET / DELETE | `/api/v1/auth/session` | Login body uses username/password; status uses authenticated flag; DELETE revokes cookie session |
| POST / GET | `/api/v1/openings` | Opening create/list; list accepts optional OPEN/CLOSED status |
| GET / PATCH / DELETE | `/api/v1/openings/{opening_id}` | Read/update/delete; deletes cascade applications |
| POST / GET | `/api/v1/candidates` | Candidate create/list; list can filter by opening/status |
| GET / PATCH / DELETE | `/api/v1/candidates/{candidate_id}` | Read/update/delete |
| POST | `/api/v1/resumes/upload` | Multipart `file`; optional `candidate_id`; 202 processing job |
| GET | `/api/v1/jobs/{job_id}` | Job status and retained extraction result/error |
| POST | `/api/v1/resumes/parse` | JSON `{"job_id":"..."}`; parsed text + structured extraction |
| POST | `/api/v1/candidates/score` | JSON `job_id` and `candidate_id`; job-specific persisted score/evidence |
| POST | `/api/v1/openings/{opening_id}/shortlist` | `minimum_score`; saved per-opening score suggestions |
| POST | `/api/v1/candidates/shortlist` | Legacy caller-supplied score simulation; response explicitly says simulation-only |
| POST / GET | `/api/v1/candidates/{candidate_id}/screening-reports` | Create/read Day 25 rule-based answer reports |
| POST | `/api/v1/openings/parse-description` | Conservative explicit-heading JD extraction; recruiter confirmation required |
| GET / PUT | `/api/v1/openings/{opening_id}/eligibility-config` | Read or replace versioned eligibility configuration |
| POST | `/api/v1/candidates/{candidate_id}/eligibility/evaluate` | Evaluate a candidate against their associated opening |
| GET | `/api/v1/candidates/{candidate_id}/eligibility?opening_id=...` | Retrieve current evaluation; recomputes when inputs/configuration changed |
| GET | `/api/v1/screening/questions` | Filter canonical questions by role, category, language, mandatory, and active |
| POST | `/api/v1/screening/sessions` | Create a persisted session for a candidate's associated opening |
| GET / PATCH | `/api/v1/screening/sessions/{session_id}` | Retrieve transcript bundle or update the session state |
| POST / GET | `/api/v1/screening/sessions/{session_id}/segments` | Append validated transcript segments or retrieve session interactions |
| POST / GET | `/api/v1/screening/sessions/{session_id}/interactions` | Persist/retrieve structured question interactions |

## Error behavior and contract notes

FastAPI/Pydantic returns 422 for invalid request models; common domain errors
include 400 for invalid upload metadata, 401 for unauthorized access, 403 for
cross-origin cookie-authenticated mutations, 404 for missing records, 409 for
duplicate or wrong-job association, 413 for a resume over 5 MiB, 429 for
throttled login attempts, and 503 for missing auth configuration/database or
unavailable local semantic model. See `/docs` for exact operation response
schemas.

The persisted shortlist route ranks candidates with saved scores; the legacy
`/candidates/shortlist` route remains simulation-only. Eligibility and
transcript endpoints are manual-review decision support and storage
interfaces. The API does not expose audio recording, speech recognition,
voice AI, or automated interview operations. The standalone Day 16 API is
separate, not mounted, and is not the source of recruiter records. The
question-bank API returns only available translations; it does not fabricate
pending translations.

All ATS endpoint definitions are in `src/api.py`; authentication/schema details
are in `src/auth.py` and `src/schemas.py`.
