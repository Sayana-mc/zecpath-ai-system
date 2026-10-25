# API and Integration Contracts

**Status:** Planning guide. Exact production routes and schemas must be verified in current routers/controllers, validation schemas, auth middleware, and tests. Example paths/payloads below are not confirmed live endpoints.

## Logical interface inventory
| Interface | Purpose |
|---|---|
| Resume submission | Validate document/reference and enqueue processing |
| Processing status | Retrieve job progress/result status |
| Screening | Run or retrieve validated screening result |
| Interview analysis | Process interview-related input where implemented |
| Decision/review | Record authorized review outcome and audit event |
| Health/readiness | Report safe operational health |

## Example request (illustrative)
```json
{"candidate_ref":"candidate-ref-123","document_ref":"document-ref-456","correlation_id":"trace-example"}
```
## Example response (illustrative)
```json
{"job_id":"job-example","status":"QUEUED","correlation_id":"trace-example"}
```
## Example error (illustrative)
```json
{"error":{"code":"VALIDATION_ERROR","message":"The request did not pass validation","correlation_id":"trace-example"}}
```

## Contract principles
- HTTPS, authentication, authorization, input validation.
- Stable error codes and safe public error messages.
- Correlation/request IDs propagated across services.
- Pagination for collection routes.
- Idempotency keys for retryable create/submit operations where needed.
- Never expose stack traces, secrets, prompts, or unnecessary candidate data.

## Verification checklist
For each live endpoint, document method, path, required fields, response schema, status codes, permissions, rate limits, retry semantics, and tests. Verify malformed input, auth failures, duplicate requests, provider timeout, invalid model output, and audit-event creation.
