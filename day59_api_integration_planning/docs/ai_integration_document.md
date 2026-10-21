# Day 59 — AI Integration Document

## Objective
Define proposed integration contracts for Resume Parsing, ATS Scoring, Screening AI, Interview AI, and Decision AI, including backend/database flow, sync/async behavior, error handling, retries, authentication, and security.

## API inventory
1. Resume Parsing API: `POST /v1/resume-jobs`; async; returns HTTP 202 and a job ID.
2. ATS Scoring API: `POST /v1/ats/score`; sync; returns a validated score and matched/missing skills.
3. Screening AI API: `POST /v1/screening/evaluate`; sync; returns evidence and a review flag.
4. Interview AI API: `POST /v1/interviews/score`; sync for real-time scoring; strict example timeout of 8 seconds.
5. Decision AI API: `POST /v1/decisions/recommend`; sync; returns a recommendation for human review, not an automatic rejection.

These are proposed endpoints, not claims that live endpoints already exist.

## Backend → AI → database flow
1. Authenticate the caller and validate request fields.
2. Create request metadata and a correlation ID.
3. For resumes, create a job row and queue work; return 202 with job ID.
4. A worker retrieves the authorized document, parses it, validates extraction output, then stores the structured profile and job status.
5. ATS and Screening services receive validated profile data and role rubric.
6. Interview AI receives transcript text and rubric version; backend enforces timeout.
7. Decision AI combines stage statuses and evidence, then returns a review recommendation.
8. Validate all AI outputs before database writes.
9. Write audit events with service, request ID, timestamps, version, status, and outcome.

## Async vs sync
Resume parsing is asynchronous because file parsing and possible OCR can take variable time. Client polls `GET /v1/resume-jobs/{job_id}` or receives a notification. Use bounded retries, idempotency keys, and a dead-letter/manual-review path.

Real-time interview scoring is synchronous with a strict timeout (example 8 seconds). On timeout, return a controlled error and continue with manual review; never fabricate a score. Non-interactive post-interview batch scoring may be asynchronous.

## Error contract
```json
{
  "error": {
    "code": "UPSTREAM_TIMEOUT",
    "message": "The scoring service did not respond in time.",
    "request_id": "req-1004",
    "retryable": true
  }
}
```
HTTP guidance: 400 malformed/invalid input; 401 unauthenticated; 403 unauthorized; 404 unknown resource; 409 idempotency/state conflict; 413 oversized payload; 422 business validation error; 429 rate limited; 500 unexpected server error; 502/503 upstream unavailable; 504 timeout. Never expose stack traces, secrets, or private resume content in client errors.

## Retry mechanism
Retry transient network errors, 429, and selected 5xx only. Use exponential backoff with jitter, max 3 attempts as an example, and honor `Retry-After`. Do not retry 400/401/403 or schema errors without fixing the request. Use idempotency keys and deduplication. After exhausted retries, mark the job failed with a safe error code and route it to manual review/dead-letter handling.

## Authentication and security
Use HTTPS/TLS; OAuth2 client credentials or short-lived signed service tokens for service-to-service calls; secret manager/environment configuration; least privilege; token rotation; request-size and file-type limits; private storage; short-lived signed URLs; encryption at rest; rate limiting; PII redaction in logs; protected audit logs; retention/deletion policies.

## Logical database entities
`candidates`, `resume_jobs`, `resume_profiles`, `assessment_results`, `decision_recommendations`, `audit_events`. These are proposed logical entities, not a physical database migration.

## Observability
Track request volume, latency, status/error rates, timeouts, retries, queue depth, oldest queued job, failed jobs, schema mismatches, and model/rubric versions. Use correlation IDs across backend, worker, AI API, and database.

## Safeguards
Human review is mandatory. Automatic rejection remains disabled. Scores must include evidence and rubric/model version. Missing data is not automatically a zero score or a rejection.
