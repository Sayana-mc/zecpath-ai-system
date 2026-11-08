# Day 7 — AI data pipeline

## Root workflow

The connected path is upload validation → processing-job row → text extraction
→ Day 8 section detection → Day 9 skills, Day 10 date-based experience, Day 11
education and certification parsing → persist resume text/profile → optional
Day 12 local embedding → Day 13 score/evidence → job-specific rank and
shortlist suggestions → recruiter review.

The profile is produced by `src/resume_analysis.py`; matching and scoring are
orchestrated by `src/integrated_scoring.py`; API routes and persistence are
`src/api.py` and `src/database.py`. Screening reports use a separate Day 25
rule-based flow.

## Lifecycle boundaries

Resume binaries are temporary and deleted after extraction. Raw extracted
text and structured data are retained with the candidate; score/evidence is
stored on that record and is cleared when score inputs change. The local
embedding is computed at scoring time and is not cached. Candidate score
history, parser/model version history, and a durable queue are absent. An
interrupted in-process job is marked failed on startup; automatic retries are
not performed.

See the [pipeline diagram](diagrams/day07_ai_data_pipeline.mmd),
[storage design](day07_ai_storage_design.md), and
[metadata standards](day07_ai_metadata_standards.md).
