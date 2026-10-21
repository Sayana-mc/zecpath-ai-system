# Day 58 — AI Roadmap and Innovation Proposal

## Vision
Evolve Zecpath from a pipeline simulation into a transparent, candidate-supportive and operationally reliable AI-assisted hiring platform. Prioritize explainability, consent, accessibility, privacy, and human accountability.

## Proposed features

### 1. AI video analysis — optional, consent-based
Potential scope: interviewer-facing playback, timestamped notes, transcript alignment, and review of observable interview events. Recording is off by default, access is restricted, and candidates can request deletion. Do not infer suitability from facial movements or other biometric/emotional proxies. The initial MVP should focus on transcript and timestamp tools rather than automated judgments.

### 2. Emotion detection — excluded from hiring decisions
Facial expressions and voice are unreliable grounds for inferring a candidate's inner emotional state, honesty, personality, or job capability. Do not produce or store an emotion score for ranking, selection, or rejection. Use structured, job-related rubrics instead.

### 3. Real-time feedback
Start in practice mode. Give feedback on answer relevance, use of examples, structure, and technical correctness against a transparent rubric. Candidates can opt out. During live assessed interviews, do not provide hidden or unequal assistance; define and disclose permitted tools consistently.

### 4. AI coaching system
Provide practice questions, learning plans, sample exercises, and explanations linked to job requirements. The candidate can review and correct their skill profile. Coaching usage must not affect hiring scores.

### 5. Candidate improvement suggestions
Map explicitly missing skills to actionable practice steps. The prototype demonstrates a rule-based approach using supplied skills. Production suggestions should include evidence, confidence or uncertainty, and an option for the candidate to correct inaccurate inputs.

### 6. Interview analytics dashboard
Show aggregate stage completion, question/rubric coverage, review turnaround, missing evidence, and reviewer disagreement. Use access controls and privacy safeguards for small groups. Avoid emotion, personality, or other unsupported proxy metrics.

## Roadmap

| Phase | Timeline | Focus | Exit criteria |
|---|---|---|---|
| P1 | 0–2 months | Reliable foundations, validation, versioned outputs, audit events, consent controls | Tests pass; schemas and safeguards documented |
| P2 | 2–4 months | Candidate coaching MVP and practice feedback | Suggestions map to role skills; candidate can correct inputs |
| P3 | 4–6 months | Interview analytics dashboard | Metrics documented; access control tested |
| P4 | 6–9 months | Optional consent-based video workflow pilot | Consent, withdrawal, access, correction and deletion tested |
| P5 | 9–12 months | Scale, API versioning, queues, observability, load/recovery tests | Load targets, monitoring, rollback, privacy and security reviews pass |

Timelines are planning estimates, not commitments. They depend on staffing, data availability, legal/privacy review, and integration complexity.

## Scaling architecture
1. Start with a modular monolith and explicit module contracts.
2. Add versioned APIs and schema validation before external integrations.
3. Move long-running transcription or document processing to a queue only when workload measurements justify it.
4. Add monitoring for latency, errors, queue depth, cost, and data quality.
5. Evaluate models and prompts against a versioned test set before release.
6. Use access controls, encryption, retention schedules, deletion workflows, and audit logs.
7. Deploy gradually with rollback and incident-response procedures.

## Success metrics
- Coaching suggestions linked to target-role skills.
- Candidate correction and opt-out flows work.
- API error rate and latency measured against agreed service objectives.
- Reproducible model/prompt evaluation before releases.
- Dashboard metrics traceable to documented definitions.
- Consent, retention, and deletion tests pass.
- Human review remains required; automatic rejection stays disabled.

## Risks and mitigations
- **Bias or proxy discrimination:** use job-related rubrics, audit outcomes, and avoid emotion/personality inference.
- **Privacy risks:** minimize collection, require explicit consent for recordings, restrict access, and provide deletion controls.
- **Incorrect coaching:** show evidence and allow corrections; do not make unsupported ability claims.
- **Automation bias:** make recommendations advisory and retain human decision responsibility.
- **Scaling failures:** introduce queues, monitoring, load tests, and rollback only after measuring bottlenecks.

## Conclusion
Prioritize transparent coaching and structured analytics. Treat video processing as optional and consent-based. Exclude emotion and personality inference from hiring decisions. Production implementation requires technical, privacy, security, accessibility, and stakeholder review.
