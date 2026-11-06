# Day 68 Bug-Fix Report

## Confirmed defects corrected

| Defect | Root cause | Changes | Regression evidence |
|---|---|---|---|
| Dashboard authentication was lost on page reload; credentials existed only in JavaScript memory. | Dashboard attached HTTP Basic credentials to each fetch and held them only until reload. No server session or revoke operation existed. | Added SQLite-backed opaque sessions with hashed token storage, eight-hour expiry, HTTP-only/SameSite=Strict cookies, login/logout endpoints, automatic dashboard session restoration, and retained Basic auth for API compatibility. | `test_recruiter_session_survives_restart_and_logout_revokes_it`; browser workflow restored the authenticated workspace and saved records after page reload and backend restart. |
| Recruiter passwords had no persisted account initialization/password-hash flow. | Only environment variables could configure the single recruiter; no first-account setup command existed. | Added `python -m src.create_recruiter`, which prompts without echo, requires 16+ characters, stores a random-salt PBKDF2-HMAC-SHA256 hash, and refuses to replace an existing first account. | `test_recruiter_password_is_persisted_as_a_salted_hash` verifies correct/incorrect passwords and database-backed session login. |
| Authentication had no brute-force control. | Invalid credentials were checked on every request without throttling. | Added persistent SQLite login-attempt tracking, keyed by username and client address; five failures cause a 15-minute cooldown and a `Retry-After` header. | `test_recruiter_login_is_rate_limited`. |
| Cookie-authenticated writes lacked a CSRF origin check. | Basic auth did not rely on ambient browser credentials, so no session-specific origin policy existed. | Session-authenticated POST/PATCH/DELETE requests now require an exact same-origin `Origin` header; session cookies are SameSite=Strict. | Session regression test verifies a write without Origin is denied and same-origin write succeeds. |
| Initial dashboard session restoration generated an expected 401 for a signed-out user. | The UI probed a protected endpoint to discover whether a session existed. | `/api/v1/auth/session` now reports `authenticated: false` without an error when there is no valid cookie; the dashboard only opens the workspace for a valid session. | `test_root_and_health` verifies the unauthenticated probe returns 200/false; browser reload is signed out without an authentication failure. |

## Implementation-time regression corrected

The first logout implementation returned an empty response with an unset
status code. The route now explicitly returns HTTP 204; the logout regression
test passes and verifies the session is revoked. This temporary implementation
failure is not present in the final tree.

## Remaining issues (not represented as fixed)

- Account reset/rotation and multi-recruiter account management are absent.
- Environment-based compatibility authentication is not password-hash backed.
- No production identity provider, role model, TLS deployment, encryption at
  rest, consent, or retention policy is configured.
- The root screening feature remains a rule-based answer note, not the
  complete question/transcript/scoring/report flow.
- No root workflow invokes the standalone Day 21 eligibility, Day 24 audio,
  Day 26 scoring, Day 28 reporting, or Day 15 fairness engines.
- Candidate listing pagination, OCR, durable worker queue, and resume
  duplicate detection remain unimplemented.

No existing test was deleted or weakened for this work.
