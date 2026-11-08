# Day 6 — Job description parsing

## Current implementation

The root application accepts a job title, free-text description, explicit
required/preferred skill lists, and optional minimum education/experience.
Pydantic validates these fields; the dashboard requires recruiters to enter
required skills explicitly. Root create/update does not call the Day 6
prototype. `day6_jd_parser` normalizes already-structured role, skill,
experience, education, and responsibility fields; it does not reliably
extract all requirements from unstructured prose.

## Status and remaining work

The Day 6 module is **PARTIAL / NOT ROOT-INTEGRATED**. Root score invalidation
does clear scores when relevant opening fields change, so stale score evidence
is not intentionally retained. Missing work includes robust raw-description
parsing, required/preferred evidence classification, ambiguity warnings,
validated confidence, storing parser/version output, and recalculating
dependent scores from newly parsed requirements. Do not infer a job's
requirements silently or replace recruiter-entered fields with guesses.

Representative synthetic JD fixtures are in
`datasets/test/job_descriptions.json`.
