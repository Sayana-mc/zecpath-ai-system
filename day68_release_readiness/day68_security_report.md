# Day 68 Security Report

## Implemented and tested

- The first recruiter can be initialized with `python -m src.create_recruiter`.
  The command does not embed credentials, prompts for a 16+ character
  password without echo, and stores a random-salt PBKDF2-HMAC-SHA256 hash
  (600,000 iterations), not the supplied password.
- Session tokens are random, stored in SQLite only as SHA-256 token hashes,
  expire after eight hours, and are revoked on logout.
- Browser cookies are HttpOnly and SameSite=Strict; Secure is enabled when the
  request scheme is HTTPS.
- Cookie-authenticated write requests require a same-origin `Origin` header.
- Login attempts are counted in SQLite by a hash of client address and
  case-folded username; five failures trigger a 15-minute cooldown.
- Basic authentication remains supported for direct clients. Constant-time
  comparison is used for environment-credential compatibility mode.
- Health responses do not disclose secrets. Database errors are returned as
  generic unavailable messages.
- Resume uploads are limited to 5 MiB, use generated storage names, restrict
  suffixes to PDF/DOCX/TXT, and parse using format-aware libraries.
- SQL values are parameterized; field identifiers in update statements come
  from fixed allowlists.

## Risks and required follow-up

| Severity | Finding / risk | Current mitigation or gap |
|---|---|---|
| High for network use | Applicant records and extracted resume/screening text are stored unencrypted in SQLite. | Local synthetic-data use only; add encryption/key management before real data. |
| High for network use | Legacy environment credentials are not persisted as password hashes; Basic authentication is only safe over TLS. | Prefer database PBKDF2 account setup and localhost binding; do not expose this service without TLS and a reviewed proxy configuration. |
| High for production | One shared recruiter account, no tenant isolation, RBAC, identity provider, account reset/rotation, or audit trail. | Not suitable for multi-user or production hiring. |
| High for production | No formal consent, candidate data retention, deletion schedule, verified backup/restore, or privacy notice workflow. | Deletion endpoints remove records but do not implement a policy. |
| Medium | Candidate list endpoints return all matching candidates and full resume text; there is no pagination or field-level access control. | Restrict to local/synthetic data; add pagination and data-minimizing response schemas. |
| Medium | MIME type is not validated independently of extension/parser. DOCX is ZIP-based; compressed-file resource behavior has not been stress tested. | 5 MiB cap and format parsers are present; validate content signatures and resource limits before broader exposure. |
| Medium | SQLite login throttling keys off the direct client address; proxy deployments may make many clients share an address or may misconfigure forwarded addresses. | Localhost only; proxy deployment requires trusted-proxy design and separate review. |
| Medium | No automated dependency vulnerability scan was executed. | Run a vetted scanner against a locked dependency set before release. |
| Low/Medium | Sessions persist across restart and are not invalidated by environment-password rotation until expiry unless revoked or the account username is removed. | Eight-hour expiry/logout; implement a credential-version/session-revocation policy for production. |

## Scope limitation

This is a release-readiness review of the local root app, not an independent
penetration test or a complete vulnerability audit of all historical day
modules. No claim is made that the system is bias-free or safe for real
employment decisions. No third-party AI provider is configured.
