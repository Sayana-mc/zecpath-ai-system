# Conceptual Data Models

These are conceptual entities, not claims about exact production schema. Confirm actual types, migrations, Pydantic models, TypeScript types, and database definitions.

## Candidate
`candidate_ref`, `created_at`, `workflow_status`, and policy-required consent/processing record where applicable.

## ResumeDocument
`document_ref`, `candidate_ref`, `file_type`, secure `storage_ref`, `extraction_status`, `created_at`.

## ParsedResume
`document_ref`, `parser_version`, structured `extracted_fields`, `evidence_refs`, `validation_status`.

## ScreeningResult
`candidate_ref`, `score`, `criteria_version`, `model_name/version`, `recommendation`, `evidence_refs`, `human_review_status`, `created_at`.

## InterviewAnalysis
`analysis_ref`, `candidate_ref`, `model_version`, `analysis_status`, secure `result_ref`, `created_at`.

## ProcessingJob
`job_id`, `job_type`, `status`, `attempt_count`, `correlation_id`, `started_at`, `completed_at`.

## DecisionAuditEvent
`event_id`, `candidate_ref`, `decision`, `reason`, `actor`, `model_version`, `human_reviewed`, `timestamp`, `correlation_id`.

## Telemetry
API: method, endpoint, status, duration, correlation ID. Model: task, model/version, duration, success. Error: component, error type, redacted message.

## Data rules
Use opaque references in logs; validate input; version schemas; record model provenance; define retention/deletion; avoid unnecessary duplication of sensitive data.
