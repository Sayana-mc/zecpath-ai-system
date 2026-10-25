# Logging Structure — Day 61

All events should use UTC timestamps, unique event IDs, event type, service name, and correlation ID.

## API logs
Fields: timestamp, event_id, event_type, service, correlation_id, method, endpoint, status_code, duration_ms, success.

## Model output/operation logs
Fields: model_name, model_version, task, duration_ms, success, opaque input reference. Do not log raw prompts, model outputs containing candidate data, or resume text. If business requirements require output traceability, store a minimized/redacted result reference in access-controlled storage.

## Error logs
Fields: component, error_type, short safe message, correlation_id. Redact stack traces if they could expose secrets or PII.

## Decision audit
Fields: timestamp, event_id, candidate_ref, decision status, reason, actor, model version, human_reviewed, correlation ID. Allowed demo statuses: SHORTLIST, REVIEW_REQUIRED, NOT_SHORTLISTED, PENDING. The prototype rejects unsupported statuses and does not implement an automatic-rejection path.

## Storage
Operational logs: JSON Lines in the demo; production should use centralized protected log storage. Metrics belong in a time-series store. Decision audit should be append-only/tamper-evident with restricted access and retention policy.
