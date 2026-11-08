# Day 4 — AI data entity design

## Current persisted entities

The root SQLite schema stores job openings, candidate applications, resume
text and structured resume data, processing jobs, screening reports, recruiter
accounts/sessions, and login-attempt throttles. Candidate records belong to an
opening through a foreign key. Score evidence is stored as JSON on the
candidate row. Parsed job-profile provenance, embedding cache, score history,
and explicit extraction confidence are not persisted.

The schemas under `schemas/` are documented exchange contracts for the
current root-compatible fields, not a claim that every optional property is
currently generated. The root API continues to validate its requests with
Pydantic models in `src/schemas.py`.

## Dataset

`datasets/test/resumes/` contains ten clearly labeled synthetic, text-only
resume examples spanning technical and non-technical roles, freshers and
experienced profiles, varied section names, education, work history, and
certifications. `datasets/test/job_descriptions.json` contains three
synthetic role descriptions. These are fixtures, not production candidate
records, and are not imported into the application database.

## Missing entity capabilities

Contact data is limited to candidate name/email and is application
administration data. Profile schemas do not yet normalize projects,
achievements, languages, or certification relevance into root scoring inputs.
No demographic/protected-attribute field is part of the scoring profile.
