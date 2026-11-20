# ZecPath AI Governance, Privacy & Access Control Policy

## 1. Human-in-the-Loop Mandate
- All AI scoring, cross-round aggregation, behavioral/integrity indicators, and recommendations are **decision-support signals only**.
- No candidate is automatically hired without human recruiter review; human overrides and approvals are logged with actor identity, timestamp, and rationale.
- Behavioral and integrity indicators are non-punitive and route flagged cases to human review rather than automatic rejection.

## 2. Role-Based Access Control (RBAC)
| Role | Key Permissions | Restrictions |
| :--- | :--- | :--- |
| `recruiter` | View candidates, score, conduct interviews, view reports, approve/reject recommendations, manage consent | Cannot override AI decisions, configure role weights, run optimization, anonymize PII, or view/verify audit logs |
| `senior_recruiter` | All `recruiter` permissions + export PDF reports, override recommendations, delete candidates, view optimization | Cannot purge retention or manage users/audit integrity |
| `admin` | Full system administration, weight/threshold config, retention purge/anonymization, audit log viewing & verification | Scoped to actor's tenant (`tenant_id`) |
| `auditor` | Cross-tenant read-only access to candidates, reports, optimization, and audit log verification | Cannot modify scores, decisions, or candidate records |

## 3. Tenant Isolation & Consent Ledger
- Every opening, candidate, evaluation, recommendation, and report carries a `tenant_id`. Cross-tenant access returns `HTTP 403`.
- Candidate consents are versioned (`consent-v2`) and tracked per purpose (`ai_assessment`, `integrity_monitoring`, `audio_recording`) with grant/revoke audit events.

## 4. Data Retention & Tamper-Evident Audit Trail
- Retention policies are configurable per category and support controlled PII anonymization (`POST /api/v1/governance/candidates/{id}/anonymize`), redacting name, email, and resume text.
- Audit events are SHA-256 hash-chained (`previous_hash` -> `event_hash`); any direct SQLite modification breaks verification (`GET /api/v1/audit/verify` returns `verified: false`).
