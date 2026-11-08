# Day 1–15 known limitations

## Product and requirement blockers

- The Phase 1–100 PRD is absent; Day 1 scope and policy cannot be verified.
- No approved hiring policy, legal review, consent/retention policy, or
  fairness evaluation dataset was supplied.

## Extraction and parsing

- Scanned/image-only PDFs have no OCR; complex columns/tables and repeated
  headers can degrade extraction.
- Section, skill, experience, education, and certification parsers are
  heuristic/rule-based and are not calibrated.
- Raw job-description parsing is not integrated; root requirements are
  recruiter-entered structured fields.
- Certification issuer/dates/relevance and job-relevant experience evidence
  are incomplete.

## Matching and scoring

- Day 12 local embedding model/cache is required; matching uses one overall
  similarity and is not benchmarked or threshold-calibrated.
- Day 13 score weights and formula are experimental. Missing components
  currently contribute zero. No employment outcome validation exists.
- Scoring does not retain immutable profile/JD/model/config versions or score
  history.
- Labeled personal-data removal is not complete de-identification; proxies
  and extraction differences may remain. No protected traits are inferred.
- No authorized subgroup data exists, so group fairness metrics are not
  available.

## Application and operations

- One local recruiter account; no tenant isolation, RBAC, MFA, identity
  provider, or production TLS setup.
- SQLite applicant data is not encrypted at rest; retention, consent, deletion,
  export, backup/restore, and audit requirements are incomplete.
- Resume processing is in-process; no durable queue, retry, or content-level
  idempotency. Original resume binaries are deleted.
- Candidate lists are unpaginated. No production-scale/load validation exists.
- Voice screening, interviews, machine tests, final decision and offer
  automation are later-stage prototypes/plans, not root workflow features.

Scores and ranked suggestions must remain human-reviewed decision support;
they are not an automatic employment decision.
