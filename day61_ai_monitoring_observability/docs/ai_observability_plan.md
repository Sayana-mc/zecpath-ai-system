# AI Observability Plan — Day 61

## Objective and scope
Track, debug, and monitor API requests, model execution, candidate processing, interview analysis, errors, and consequential decisions. This package is a synthetic local prototype, not live production monitoring.

## Signals
- **Logs:** API request, model run, error, and decision audit events.
- **Metrics:** response-time percentiles, API/model failure rates, throughput, queue depth/age, reviewed-set accuracy, interview-analysis completion, human-review coverage, audit completeness.
- **Traces:** propagate one correlation ID through API, queue, parser, model, validation, storage, and decision service.

## Accuracy definition
Accuracy must compare predictions to reviewed ground-truth labels over a defined evaluation window. HTTP success, task completion, and model confidence are not accuracy.

## Alerting
The demo implements API failure-rate and p95-latency rules. Initial thresholds: latency warning 1s/critical 3s; failure-rate warning 5%/critical 10% after at least 10 requests. Tune against baseline. Production should also alert on queue backlog, repeated model timeouts, missing telemetry, low reviewed-set accuracy, and incomplete audit records.

## Privacy and security
Redact PII/secrets; never log raw resumes, interview transcripts, full prompts, tokens, or passwords. Use role-based access, encryption, access audit, defined retention, and tamper-evident decision records. Thirty-day retention in the sample config is illustrative only.

## Rollout
1. Approve event schema and owners.
2. Add correlation IDs and structured logging.
3. Export metrics to a monitoring backend.
4. Build dashboards and notification routing.
5. Validate using synthetic/staging traffic.
6. Review alert noise, privacy, retention, and audit completeness.
7. Publish incident runbooks and roll out gradually.
