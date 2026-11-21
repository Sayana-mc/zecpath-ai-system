# ZecPath API Documentation Summary

FastAPI exposes **125 `/api/v1/*` routes** (live OpenAPI spec at `http://127.0.0.1:8000/docs`):

- **Auth & Health:** `POST/GET/DELETE /api/v1/auth/session`, `GET /api/v1/health`
- **Openings & Candidates:** `POST/GET/PATCH/DELETE /api/v1/openings*`, `/api/v1/candidates*`
- **Resume & ATS:** `POST /api/v1/resumes/upload` (`202`), `GET /api/v1/jobs/{job_id}`, `POST /api/v1/ats/score`, `POST /api/v1/ats/shortlist`
- **Eligibility & Screening:** `PUT/GET /api/v1/openings/{id}/eligibility-config`, `POST /api/v1/candidates/{id}/eligibility/evaluate`, `/api/v1/screening/*`
- **Interviews & Machine Test:** `/api/v1/hr-interviews*`, `/api/v1/technical-interviews*`, `/api/v1/machine-tests/assignments*`
- **Cross-Round, Decision & Reports:** `POST /api/v1/candidates/{id}/cross-round-evaluation`, `POST /api/v1/candidates/{id}/final-recommendation`, `POST /api/v1/final-recommendations/{id}/decision`, `POST/GET /api/v1/candidates/{id}/hiring-intelligence-report*` (`/html`, `/markdown`, `/pdf`)
- **Governance, Optimization & Monitoring:** `/api/v1/audit/events`, `/api/v1/audit/verify`, `/api/v1/governance/*`, `/api/v1/optimization/*`, `/api/v1/monitoring/*`
