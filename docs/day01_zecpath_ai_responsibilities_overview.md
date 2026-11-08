# Day 1 — Product and AI responsibilities

## Status and source boundary

The supplied Phase 1–100 product requirements document was not found in the
repository. Product intent below is limited to repository evidence and the
implementation prompt; missing product rules remain **BLOCKED** pending the
original PRD. The runnable product surface is the recruiter-facing FastAPI
application at `src.main:app`, not every numbered learning folder.

## Hiring lifecycle

The intended lifecycle is job definition → application/resume submission →
text extraction and structured parsing → job matching and ATS score →
recruiter review → voice screening → HR and technical interviews → machine
test → final decision → offer. Only the local recruiter, job/application,
resume processing, ATS score, persisted ranking suggestions, and limited
screening notes are currently connected. Later-stage steps are plans or
standalone prototypes and are not represented as working root-app features.
See [the lifecycle diagram](diagrams/day01_hiring_lifecycle.mmd).

## Actors and data boundary

- Recruiter: creates job requirements, manages applications, requests scores,
  reviews evidence, and makes hiring decisions.
- Candidate: submits application information and a resume; no candidate
  self-service workflow was found in the root app.
- Backend: FastAPI routes validate requests, enforce the single-recruiter
  authentication boundary, persist to SQLite, and call local parsing/scoring
  code.
- AI/analysis components: Day 9–11 rule-based extraction, Day 12 local
  sentence embeddings, and Day 13 configured weighted heuristics.
- Storage: SQLite stores job and candidate records, extracted text and data,
  scores/evidence, processing jobs, and screening reports. Resume binaries are
  removed after extraction.
- External services: no external model provider is configured in the root app.

## Business objectives and limits

The system automates repetitive extraction and comparison and exposes score
evidence for recruiter review. Its current heuristic has not been validated
for employment decisions, fairness, or legal compliance. Human review is
required; scores must not be used as automatic rejection decisions. Privacy
controls are local application controls, not a complete retention,
encryption-at-rest, or production compliance program.

Module type, dependencies, and implementation evidence are maintained in the
[AI module inventory](day01_ai_module_inventory.md).
