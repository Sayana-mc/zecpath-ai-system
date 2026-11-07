# Known limitations and unverified areas

## Integration boundary

The only supported app runtime is `src.main:app`. The root integrates Days
9–13 for resume-derived ATS scoring and Day 25 for rule-based screening
annotations. Other stage folders are independent unless specifically called
from the root code. The Day 16 standalone API is a demo; Day 20 contains a
checklist, not a scorer.

Eligibility (Day 21), question dataset (Day 22), transcript/audio (Days 23–24),
screening scoring (Day 26), sentiment/confidence (Day 27), comprehensive
screening reports (Day 28), interview/cross-round modules (Days 29–54), Day
55 governance, Days 56–65 simulations/plans, and Day 68 reports are not
connected as a unified recruiter workflow. Days 1, 2, 66, and 67 are absent.

## Applicant data and scoring

- Resume extraction is rule-based and currently structures skills, some
  education, and date-derived experience only. It does not structure
  certifications, candidate contact fields, projects, achievements, or
  recruiter-confirmed corrections.
- Original upload binaries are deleted after processing; only filename and
  extracted text/structured data remain. There is no OCR or reprocessing
  source file.
- Day 12 uses a general-purpose local model; model availability/cache is
  required. Day 13 missing component inputs contribute zero to the final score
  despite being marked unavailable in evidence.
- The model and weights have not been independently validated for job
  relevance, reliability, subgroup impacts or legal compliance. Scores and
  shortlists are not hiring decisions.
- Day 13 active Python weights and adjacent JSON config files disagree for some
  titles. The integrated app follows the active Python `weight_manager.py`;
  no config unification has been performed.

## Operations, security and scale

- One recruiter account, no RBAC/tenant separation, no MFA or identity
  provider.
- SQLite applicant content is not encrypted at rest; no retention/consent
  deletion workflow or production backup/restore procedure exists.
- Processing runs in-process, without a durable queue, retries or deduplication.
- Lists are unpaginated and include resume text; no candidate-volume/load
  validation was performed.
- Authentication protections do not replace TLS; HTTP Basic must not be used
  over a network without TLS. The root prototype is intended for localhost
  synthetic data only.
- No external security assessment, dependency vulnerability scan, or
  production threat-model review was completed.

## Verification scope

The root API suite and repository suite passed at their recorded run times;
one real local-model browser workflow used synthetic data. The Postman
collection is syntax-validated but not run in Newman/Postman. The shared
port-8000 browser page was not live at the time checked; an isolated port 8766
instance was used instead. No claim is made that every historical stage was
line-by-line audited or that every stage test is meaningful for integration.
