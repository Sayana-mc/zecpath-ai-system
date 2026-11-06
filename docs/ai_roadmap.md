# AI roadmap

This roadmap is a proposal, not a feature-completion claim. Development must
remain evidence-based and human-supervised because hiring decisions can have
significant consequences.

## Implemented in the root application today

- Resume text extraction from TXT, DOCX, and text-based PDF.
- Exact case-insensitive required-skill overlap using candidate-reported skills
  and exact mentions in extracted text.
- Evidence snippets and missing/matched skill lists.
- Deterministic Day 25 keyword/regex interpretation of recruiter-entered
  screening answers.
- Human-reviewed shortlist suggestions based on persisted deterministic
  scores; shortlist generation does not change candidate status.
- No external AI/LLM provider is configured or called by the root API.

These are deterministic rules, not semantic AI, validated employment
assessments, or evidence that a system is bias-free.

## Planned improvements

| Priority | Proposal | Preconditions and acceptance evidence |
|---|---|---|
| P0 | Establish a versioned candidate/job/answer/evidence contract and provenance for each extracted or candidate-reported fact. | Schema compatibility tests; every output maps to source text or an explicit candidate answer; missing data remains missing. |
| P0 | Add safe correction/verification workflow for parser output before it is used for score evidence. | Browser/API tests show manual edits persist and trigger score invalidation. |
| P0 | Replace keyword-only matching only if a real, approved provider/model is selected. | Provider-specific secret handling, structured schema output, timeouts, retries, cost limits, provider-offline behavior, model/version logging, and deterministic test fixtures; no simulated AI success. |
| P0 | Validate any scoring/ranking method against a job-related, independently reviewed dataset and approved metrics. | Pre-registered evaluation protocol, documented cohort coverage/limitations, error analysis, calibration, reviewer agreement, and independent governance sign-off. |
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
