# Day 68 Release Notes

## Changes in this Day 68 task

- Added first recruiter initialization through `python -m src.create_recruiter`.
  Passwords are prompted without echo and stored as salted PBKDF2-HMAC-SHA256
  hashes in the selected SQLite database.
- Added eight-hour persistent recruiter sessions, hashed opaque token storage,
  logout revocation, same-origin checks for session-authenticated writes, and
  persistent login throttling.
- Updated the dashboard to restore valid sessions after reload and to clear
  local workspace state on sign-out.
- Retained the existing HTTP Basic API compatibility mode.
- Added regression tests for session persistence, logout, brute-force
  throttling, password hashing, and unauthenticated session restoration.
- Updated root setup/security notes and created Day 68 audit, bug-fix,
  integration, test, security, performance, and validation reports.

## Setup (Windows PowerShell)

From the repository root, using an existing Python 3.12 virtual environment:

```powershell
.\.venv\Scripts\python.exe -m src.create_recruiter
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8765
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/). The initializer must
run against the same `ZECPATH_DB_PATH` that the server uses. Port 8000 was
already occupied in the validation environment; 8765 was used for the real
browser test.

To run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_api.py -q
.\.venv\Scripts\python.exe -m pytest -q
```

## Known limitations

- The only AI-like root features are deterministic keyword/regex analysis and
  exact skill overlap; no LLM provider is configured.
- Day 21 eligibility, Day 23/24 transcript/audio, Day 26 screening scoring,
  Day 28 comprehensive reporting, and Day 15 fairness are not root-app
  integrations.
- Single recruiter account only; no reset/rotation flow, RBAC, SSO, tenant
  isolation, encryption at rest, formal consent/retention controls, or
  production audit trail.
- SQLite has no versioned migrations or automated backup/recovery. Root
  candidate lists are unpaginated. Resume extraction uses in-process background
  tasks; OCR is absent.
- The full suite and local browser journey passed, but dependency security
  scanning, load testing, staging, and production deployment were not run.

## Release status

This is a local synthetic-data demo release candidate, not a staging or
production release.
