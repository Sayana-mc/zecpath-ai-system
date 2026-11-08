# Day 21 — eligibility decision support

The root application now persists versioned per-opening eligibility
configurations and candidate evaluations. Protected routes allow configuration
read/update, evaluation, and latest-result retrieval. Inputs include the
current score, mandatory skills, experience, location/work-mode, relocation,
and availability evidence where configured.

The evaluator distinguishes explicit failures from missing/uncertain data.
Missing information is routed to `REVIEW`; a configured explicit threshold
failure may produce `REJECTED`. Every response requires human review, and
evaluation does not mutate candidate application status. A fingerprint causes
retrieval to reevaluate when relevant candidate/opening/score/configuration
inputs change.

The root has one recruiter account and no tenant isolation. The engine is
unvalidated decision support, not an automatic rejection or hiring mechanism.
