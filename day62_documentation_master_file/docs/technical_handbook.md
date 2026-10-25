# Zecpath AI Technical Handbook — Day 62

## 1. Purpose
This handbook is the central technical reference for the Zecpath AI Hiring System: architecture, interfaces, scoring, data, modules, setup, deployment, observability, and onboarding.

## 2. System overview
The intended workflow supports resume ingestion and parsing, candidate screening, interview analysis where implemented, validation, persistence, recruiter review, and decision audit. AI output is decision support; consequential outcomes must remain reviewable by an authorized human.

## 3. Evidence status
Day 59 covered API/integration planning and example contracts. Day 60 covered a local performance prototype with batching, bounded concurrency, caching, and synthetic benchmarks. Day 61 covered a local observability prototype with structured API/model/error logs, example alerts, dashboard summaries, and decision audit records. Earlier proof-of-concept context included Gemini, RAG/ChromaDB, PyMuPDF, python-docx, and resume screening. Verify the current branch before describing these as live integrations.

## 4. Architecture
See `system_architecture.md` and `../diagrams/workflows.md`. Logical flow: Candidate/Recruiter UI → Backend API → Queue/Workers → Resume Parsing → AI Inference → Validation → Application Database → Decision Service → Human Review. Some boxes may be logical modules rather than independently deployed services; verify in source.

## 5. APIs
See `../api/api_contracts.md`. Treat interface names and example payloads as planning examples until confirmed in routers/controllers, schemas, auth middleware, and tests.

## 6. Scoring
See `../scoring/scoring_logic.md`. Historical proof-of-concept bands were 70+ shortlist recommendation, 50–69 review, below 50 reject recommendation. These are not verified current production policy and must not drive automatic rejection without approved policy and human review.

## 7. Data models and modules
See `../data_models/data_models.md` and `../modules/module_reference.md`. They describe conceptual entities and responsibilities, not guaranteed database or code names.

## 8. Setup and deployment
See `../setup/setup_guide.md` and `../setup/deployment_guide.md`. Use the repository's actual manifests and run instructions. Secure secrets, validate migrations, use health checks, configure telemetry, and document rollback.

## 9. Observability
The Day 61 prototype demonstrates JSONL API/model/error logs, decision audit events, latency/failure metrics, and threshold alerts. It is not a live monitoring server or graphical dashboard.

## 10. Security and governance
Minimize candidate data; redact PII/secrets; use role-based access and encryption; define retention/deletion; record model/version provenance; keep audit data protected; measure model quality against reviewed labels; retain human oversight.

## 11. Testing
Use unit tests, API contract tests, integration tests, malformed input tests, timeout/retry tests, performance tests on representative anonymized inputs, privacy checks, and audit-completeness tests.

## 12. Maintenance
For each release, update architecture, API contracts, scoring policy, data schemas, deployment steps, module ownership, and version history. Mark unverified features clearly.
