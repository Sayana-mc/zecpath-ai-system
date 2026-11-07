# AI roadmap

This roadmap is a proposal, not a feature-completion claim. Development must
remain evidence-based and human-supervised because hiring decisions can have
significant consequences.

## Implemented in the root application today

- Resume text extraction from TXT, DOCX, and text-based PDF.
- Day 9-11 rule-based extraction of skills, education, and dated work history
  from TXT, DOCX, and text-based PDF resume text.
- Day 12 local `all-MiniLM-L6-v2` embeddings for resume/job cosine similarity
  when the model is cached and a readable resume is available.
- Day 13 role-weighted scores using skill, experience, education, and semantic
  components, with persisted breakdowns, weights, contributions, and
  missing-component reasons.
- Evidence snippets and missing/matched required-skill lists.
- Deterministic Day 25 keyword/regex interpretation of recruiter-entered
  screening answers.
- Human-reviewed shortlist suggestions based on persisted deterministic
  scores; shortlist generation does not change candidate status.
- No remote AI/LLM provider is configured or called by the root API; semantic
  inference stays local.

These are experimental rule/model outputs, not validated employment
assessments or evidence that a system is bias-free. Missing evidence is not
proof that a candidate lacks a qualification. The Day 13 implementation's
`weight_manager.py` is the active source of role weights; similarly named JSON
files in that stage are not read by the scorer, and contain conflicting values
for some roles.

The standalone Day 16 API remains a separate demo; the root API provides the
live CRUD, upload, parsing, scoring, shortlist, and screening routes. No
executable Day 20 ATS scorer was present to integrate, so the root app uses
the existing Day 13 weighted pipeline and does not claim a Day 20 integration.

## Planned improvements

| Priority | Proposal | Preconditions and acceptance evidence |
|---|---|---|
| P0 | Establish a versioned candidate/job/answer/evidence contract and provenance for each extracted or candidate-reported fact. | Schema compatibility tests; every output maps to source text or an explicit candidate answer; missing data remains missing. |
| P0 | Add safe correction/verification workflow for parser output before it is used for score evidence. | Browser/API tests show manual edits persist and trigger score invalidation. |
| P0 | Validate the locally loaded Day 12 model, Day 13 weights, and resulting ranking with a job-related, independently reviewed dataset. | Pre-registered evaluation protocol, documented cohort coverage/limitations, error analysis, calibration, reviewer agreement, and independent governance sign-off; current scores are experimental. |
| P0 | Add model/version provenance and an explicit, tested unavailable-model workflow for Day 12 inference. | Record the model name/version and component status without applicant text or credentials in logs; return a clear service error instead of a fabricated semantic score. |
| P1 | Integrate the Day 23 transcript schema and Day 24 real audio provider into a consent-based screening workflow, only when needed. | Explicit consent, audio retention/deletion policy, provider/model disclosure, transcript provenance, confidence metadata, accessibility fallback, and actual audio tests. |
| P1 | Integrate screening scoring/reporting from Days 26/28 only after validating question quality and weights. | Range/weight tests, missing-answer handling, evidence-linked summaries, no invented strengths, human review flags, and report/database consistency tests. |
| P1 | Add fairness monitoring with legally reviewed, privacy-preserving processes. | Independent fairness design, justified protected-group measurement where lawful, adequate sample sizes, disaggregation review, mitigation tracking, and no “bias-free” claim from proxy metrics. |
| P1 | Add durable asynchronous resume workers and request/list pagination based on measured workload. | Retry/idempotency tests, bounded resource use, concurrency/load tests, queue monitoring, and data consistency checks. |
| P2 | Add production-grade identity, tenant isolation, encryption, consent/retention, audit, backup, migration, and recovery. | Threat model, external review, tested restore, access-control tests, operational runbook, and staging evidence. |

## Guardrails for future AI work

1. Never invent candidate skills, experience, availability, salary, or answers.
2. Keep the candidate's source evidence and uncertainty visible.
3. Distinguish missing information from negative evidence.
4. Do not infer sensitive characteristics from names, images, or resumes.
5. Do not automatically reject, shortlist as a final decision, or hire.
6. Require meaningful human review and a correction/appeal path.
7. Treat model confidence and fairness indicators as limited signals, not proof.
8. Disable the AI path explicitly when credentials/provider are unavailable;
   never return a success-shaped fallback.
