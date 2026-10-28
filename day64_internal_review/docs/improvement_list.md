# Day 64 - Prioritized Improvement List

Priorities indicate order of risk reduction, not a claim that the work is
already scheduled. Acceptance criteria are gates to agree with the relevant
stakeholders before implementation.

## Evidence gathered in the Day 64 walkthrough

- The local synthetic integration now exercises the actual prototype stages
  and produces a `HOLD_REVIEW` recommendation with human disposition pending.
  Production handoffs and safeguards are still unverified.
- In the synthetic ATS case, all five required skills matched, but the total
  ATS score was 44.86: experience relevance was 0, education alignment was 30,
  and lexical overlap was used instead of semantic embeddings. This is an
  investigation example, not proof the score is wrong; a qualified reviewer
  should inspect the source evidence and parser behavior.
- The Day 20 evaluation still has three false negatives among 55 cases. The
  repository does not include adjudication of those cases.
- The local end-to-end run took 5.888 ms once. This is smoke-test evidence,
  not a production latency or scalability benchmark.

| ID | Priority | Area | Evidence / gap | Improvement | Exit criteria |
|---|---|---|---|---|---|
| IR-01 | P0 | ATS accuracy | Day 20 reports 57.14% recall and 3 false negatives in 55 cases, despite 94.55% accuracy. | Have qualified reviewers adjudicate false negatives; audit label definitions and cohort coverage; agree on a minimum recall and uncertainty-reporting policy before tuning thresholds or weights. | A versioned, independently reviewed evaluation set and metric definitions exist; results include confusion matrix, precision/recall/F1, subgroup analysis where lawful and appropriate, and uncertainty; stakeholders approve the release threshold and residual-risk disposition. |
| IR-02 | P0 | Integration / data contracts | Day 56 supplies screening and interview scores as candidate fields; Day 63 joins only resumes, jobs, and available screening records. Day 51/52 are not demonstrated as downstream consumers in the Day 56 flow. | Define and implement a single versioned candidate/session contract with stage status, score scale, evidence/provenance, timestamps, and explicit `completed`, `pending`, `not_applicable`, and `failed` states. Wire real stage implementations through aggregation and recommendation. | An integration test takes one synthetic candidate through actual ATS, screening, HR, technical, and decision components; each handoff is schema-validated and traceable; missing/failed stages never become zero scores or successful completion. |
| IR-03 | P0 | Decision safety | Local artifacts require human review and disable automatic rejection, but the reviewed end-to-end simulation is not proof of enforcement across integrations. | Preserve safeguards at the final decision boundary; distinguish score, advisory, and human disposition in both API/data contract and UI; surface contradictory or incomplete evidence. | Tests prove a recommendation cannot finalize a hiring outcome without recorded human disposition; missing/contradictory evidence is visibly flagged; automatic rejection remains disabled. |
| IR-04 | P1 | Screening / interview validity | Day 32 uses simulated screening inputs; Day 47 uses manually supplied rubric scores and a word-count depth heuristic. | Validate question coverage and scoring rubrics with qualified HR and technical reviewers; measure inter-rater agreement; treat heuristic-derived signals as assistive and explain their evidence. | Reviewer-approved rubrics and calibration protocol are versioned; a blind dual-rating exercise reports agreement and disagreement resolution; reports distinguish human-entered ratings from system-derived values. |
| IR-05 | P1 | Reviewer UX | Outputs are distributed across scripts and JSON/Markdown artifacts; incomplete candidate records exist in Day 63; Day 45 feedback is unfilled. | Prototype a reviewer workflow that presents stage status, score explanation, source evidence, missing information, correction path, and human decision separately. Run feedback sessions with intended users. | Completed feedback forms and usability findings are recorded with disposition; representative users can locate evidence, identify missing stages, and record a human outcome in usability tasks. |
| IR-06 | P1 | Missing data / failure handling | Day 63 allows null screening/job fields. Day 56 aborts a candidate run on a stage exception rather than demonstrating resumable integrated processing. | Define retry, resume, timeout, and manual-review behavior for each stage; preserve failure reason and provenance without masking failure as a score. | Tests cover missing, invalid, timed-out, and failed stages; retry is bounded and auditable; the reviewer can distinguish pending, not applicable, and failed states. |
| IR-07 | P1 | Performance / scalability | Day 56 timing excludes network, database, inference, and external integrations; Day 20 measures only selected local components. | Benchmark the integrated deployment with realistic document sizes and concurrency; capture stage-level and end-to-end latency, throughput, error rate, and resource use. | Workload and service targets are agreed in advance; repeatable load-test results include p50/p95/p99 and failure rates; bottlenecks and capacity limits have documented owners/actions. |
| IR-08 | P2 | Monitoring / auditability | Day 61 contains observability design and sample outputs, but end-to-end production wiring was not evidenced. | Connect stage events and decision/audit records using stable candidate/session correlation IDs, privacy controls, and operational alerts. | A staging run can be traced across every stage; alert tests detect configured failures; access, retention, and redaction controls are verified against governance policy. |
| IR-09 | P2 | Documentation / release claims | Repository has independent demos and reports with different scope; synthetic metrics can be mistaken for integrated-system results. | Label evidence by data type, component, version, and limitations; maintain a release checklist that links claims to reproducible tests. | Every release metric identifies its dataset, sample size, test mode, and scope; synthetic results are visibly marked; no production-readiness claim lacks linked integration, evaluation, and operational evidence. |

## Ordering rationale

IR-01 through IR-03 address decision risk and must precede any use of
recommendations in live hiring. IR-04 through IR-07 establish validity,
reviewability, resilient operation, and credible performance evidence. IR-08
and IR-09 close operational and communication gaps before wider rollout.
