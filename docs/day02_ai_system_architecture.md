# Day 2 — AI system architecture

## Current architecture

The supported runtime is a modular monolith: one FastAPI process serves
`static/index.html`, `/api/v1`, local parsing/scoring functions, and SQLite.
`src/api.py` owns route orchestration; `src/database.py` owns SQLite
persistence; `src/resume_analysis.py` and `src/integrated_scoring.py` call
numbered modules. The numbered services are not independently deployed
microservices. Resume processing is in-process background work and has no
durable queue or retry mechanism.

See [current/proposed architecture](diagrams/day02_ai_architecture.mmd) and
[data flow](diagrams/day02_ai_data_flow.mmd).

## Logical service responsibilities

| Logical service | Input → output | Current placement/status |
|---|---|---|
| Resume processing | file reference → validated extracted text/profile/status | `src.api` plus parser modules; in-process |
| Job description processing | raw JD → normalized requirements/warnings | Day 6 prototype only; root fields are recruiter supplied |
| ATS AI | resume/job evidence → component and semantic scores | `src.integrated_scoring`; local deterministic rules plus local embedding model |
| Candidate ranking | persisted job-specific scores → ordered list | root API and SQLite reads |
| Fairness analysis | score/model evidence → safeguards and limitations | basic data masking added to matching; no demographic audit |
| Screening AI | recruiter-submitted answers → rule-based report | Day 25 rule engine, persisted in SQLite |
| Interview intelligence / behavior / decision | transcript or stage results → review output | future logical services only |

## Communication and execution

The browser uses same-origin REST requests. Recruiter endpoints require the
single configured account; cookie mutations use same-origin checks, and
HTTP Basic remains available to API clients. Resume upload returns a job ID
and status; in-process background processing records QUEUED/PROCESSING/
COMPLETED/FAILED. Restarted in-flight jobs are marked failed, not retried.
There is no webhook or external service-to-service protocol.

Short CRUD and scoring requests are synchronous. Resume upload delegates
processing to FastAPI `BackgroundTasks`, but this is not durable asynchronous
execution. Job IDs are unique, but duplicate-content idempotency is not
implemented. Model errors are returned explicitly rather than converted to
successful mock scores.

## Future scaling boundary

Keep the current modular monolith until durable queueing, independent load,
or model resource isolation is a demonstrated requirement. If extracted,
preserve authenticated service calls, versioned request/response schemas,
idempotency keys, bounded retries, model/config version metadata, resource
limits, and observable failure states. No independent deployable services
are claimed today.
