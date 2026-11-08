# Day 7 — AI metadata standards

## Present metadata

Root records use `opening_id`, `candidate_id`, and processing `job_id`, plus
creation/update timestamps and explicit processing states. Score evidence
stores job/candidate IDs, component results, weights, contributions,
classification, matching evidence, and a human-review flag. Resume profile
includes an extraction-method string. Screening reports include method and
timestamp.

## Missing reproducibility metadata

No persisted resume/profile version, JD revision, parser package/version,
model artifact hash, scoring formula version, weight configuration version,
embedding model version in each score, or score history is available. The
Day 12 model name is configured in source, not copied into score metadata.
Scores are invalidated when relevant inputs change, but cannot be replayed
from an immutable historical snapshot.

Do not log passwords, tokens, full resume content, or unnecessary personal
information. Root logs contain job IDs and processing outcomes; structured
redaction, retention, correlation IDs, and log rotation require further work.
