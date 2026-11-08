# Days 16–23 known limitations and backlog

## Blocking inputs

- The product PRD and policy decisions missing from the Day 1–15 audit remain
  unavailable. This work does not infer those requirements from stage folders.
- There are no human-reviewed ATS labels. The CSV is an empty review template,
  not ground truth, so no accuracy or fairness metric is reportable.
- There is no authorized, representative subgroup evaluation dataset.
- The repository has no tenant/user model; all routes inherit the existing
  single-recruiter account boundary rather than tenant isolation.

## Functional boundaries

- JD parsing recognizes explicit headings and simple numeric experience
  patterns only. It is not a general language parser, does not infer a title,
  and requires recruiter confirmation.
- Eligibility depends partly on reported/extracted resume evidence and the
  current ATS score. Rule outcomes are not employment decisions; missing or
  uncertain values need manual review.
- Only 17 screening questions are available, for Data Analyst and Software
  Developer. The remaining 11 registered roles have no authored role-specific
  question set. Most Malayalam and Hindi translations remain pending and are
  not served as translated text.
- Transcript persistence supports manual/imported data and optional
  confidence/timing. There is no audio ingestion, speech-to-text, voice model,
  or autonomous interview agent.
- Existing upload processing is FastAPI background work with SQLite status,
  not a durable queue with retry semantics.
- Database updates are additive startup migrations, not a versioned migration
  system. Applicant and transcript text remains unencrypted at rest.
- Fairness protection remains limited to existing semantic-input masking.
  Masking is not de-identification or evidence of fairness.

## Required follow-up

1. Obtain and approve the PRD, job-related eligibility policy, and data
   governance requirements.
2. Collect double-reviewed, permissioned evaluation examples; pre-register
   metric definitions and slices before reporting performance.
3. Design identity/tenant isolation before supporting more than the existing
   single local recruiter.
4. Author and independently review additional role questions and translations
   before marking coverage complete.
5. Add a versioned migration/backup plan and retention, encryption, consent,
   access-log, and incident-response controls before any sensitive-data use.
6. Establish a controlled benchmark and browser regression environment before
   making performance or UX-coverage claims.

This prototype is not certified or recommended for production hiring use.
