# Day 68 Final Validation

**Validation target:** local FastAPI + real SQLite database + integrated browser  
**Data:** fictional candidate only  
**Endpoint:** `http://127.0.0.1:8765/`

## Browser-to-database journey

| Step | Result |
|---|---|
| Opened the recruiter workspace and checked `/api/v1/health`. | Pass; API and configured authentication were reported. |
| Signed in with the temporary synthetic demo account. | Pass; the dashboard received a session cookie. |
| Created an opening with required Python/SQL/Git skills and preferred Tableau. | Pass; opening persisted and was displayed. |
| Registered fictional candidate `Fictional Applicant One`. | Pass; application persisted for the selected opening. |
| Uploaded repository fiction file `data/demo_resume.txt`. | Pass; processing completed and extracted text was shown on the candidate record. |
| Scored candidate against saved opening. | Pass; 100% exact required-skill overlap with matched evidence. This is a deterministic lexical score, not AI. |
| Generated shortlist suggestions. | Pass; candidate appeared as a review suggestion; no status was changed by shortlist generation. |
| Generated screening note from recruiter-entered question/answer. | Pass; note was labeled rule-based and human review was required. |
| Changed candidate status. | Pass; the UI saved a recruiter-selected status (`WITHDRAWN`) and it remained after reload. |
| Reloaded the browser. | Pass; the eight-hour session was restored and saved opening/candidate/score/status data reloaded. |
| Restarted the backend and reloaded the page. | Pass; the same session and saved data survived the backend restart. |
| Signed out. | Pass; dashboard returned to sign-in. The public session probe returned `authenticated: false`. |
| Tested a protected API request without authentication. | Pass; `GET /api/v1/openings` returned HTTP 401. |
| Tested unavailable API behavior. | During the intentional restart the browser observed connection-refused events; after the API returned, health and data recovered. |

The browser exercised the actual static page, FastAPI routes, background resume
processing, and SQLite persistence. The temporary server and database used for
this validation were isolated from the repository database and were stopped/
removed after validation.

## Acceptance gates

| Gate | Result | Reason |
|---|---|---|
| A — Application | **Pass for local demo** | Startup, health, browser connectivity, session auth, and restart recovery verified. Not a production deployment test. |
| B — Recruiter workflows | **Partial** | Create job, candidate, upload, score, shortlist, screening note, status, reload, and auth denial verified. Full browser CRUD/delete/filter matrix was not executed. |
| C — AI and screening | **Blocked** | No external AI; matching is exact overlap; root transcript, Day 26 scoring, Day 28 report, and voice workflow are not integrated. |
| D — Data and security | **Blocked for real data** | SQLite persists; password/session safeguards were tested. Encryption, tenant isolation, formal retention, versioned migrations, and backup recovery are absent. |
| E — Quality | **Partial** | Full pytest suite passed and a real browser flow passed. No dependency vulnerability scan, broad browser matrix, or production performance test. |
| F — Release | **Blocked for staging/production** | Local setup is documented; no staging/production deployment or production database tested. |

## Release-readiness decision

- **Local demo with synthetic data:** Ready.
- **Staging:** Not ready until TLS/proxy/auth configuration, data isolation,
  migration/backup plans, and broader test/security checks are completed.
- **Production hiring:** Not ready. Do not use real applicant data or make
  consequential decisions from the scores or screening notes.
