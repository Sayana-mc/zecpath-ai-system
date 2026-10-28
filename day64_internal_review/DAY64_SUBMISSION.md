# Day 64 - Internal Review and System Walkthrough

## Zecpath AI Hiring System

**Prepared:** 28 October 2026  
**Review type:** Internal, repository-based technical review  
**Workflow reviewed:** ATS → Screening → HR Interview → Technical Interview → Machine Test → Aggregation → Recommendation  
**Data used:** Synthetic demonstration data only  
**Overall status:** Day 64 internal review deliverables complete

---

## 1. Executive summary

This report records an internal walkthrough of the Zecpath AI hiring-system
prototype. It reviews the available stage implementations, test results,
existing evaluation reports, and a reproducible local synthetic integration
run from resume/job matching through the final recommendation.

The local integration successfully executed the prototype's ATS, screening,
HR interview, technical interview, machine-test, aggregation, and
recommendation components. For the sample synthetic candidate, the system
returned an aggregate score of **76.31/100** and an advisory
**HOLD_REVIEW** recommendation. Human disposition remained pending and no
employment action was taken.

The walkthrough also exposed a useful accuracy investigation case: all five
required job skills were present in the synthetic resume, but the ATS score
was **44.86/100**. Experience relevance scored 0, education alignment scored
30, and the semantic-similarity field used a lexical-overlap proxy rather than
an embedding model. This demonstrates why individual score components and
their supporting evidence should be reviewed before a score is used.

The repository's Day 20 ATS report lists **94.55% accuracy, 100% precision,
57.14% recall, and three false negatives in 55 test cases**. Accuracy alone
does not establish reliable candidate discovery. The sample and labels have
not been shown to represent real applicant populations or independently
adjudicated ground truth.

**Conclusion:** The system is a runnable prototype suitable for controlled
demonstrations and further internal validation. The reviewed evidence does
not establish production readiness, real-world hiring accuracy, validated
fairness, or operational scalability. Human review remains mandatory and
automatic employment action remains disabled.

## 2. Objective and deliverables

The objective for Day 64 was to evaluate the system internally, conduct an
ATS-to-decision walkthrough, identify accuracy, user-experience, and
performance improvement areas, prioritize the findings, and prepare an action
plan.

This submission includes:

1. This consolidated review report.
2. The detailed [internal review report](docs/internal_review_report.md).
3. The [prioritized improvement list](docs/improvement_list.md).
4. The [improvement action plan](docs/action_plan.md).
5. The [internal technical feedback record](docs/reviewer_feedback_template.md).
6. The executable [synthetic walkthrough](src/walkthrough.py) and its
   [regression tests](tests/test_walkthrough.py).
7. The [machine-readable walkthrough results](output/end_to_end_walkthrough.json)
   and [walkthrough summary](output/end_to_end_walkthrough.md).

## 3. Scope and method

The review inspected existing implementations, tests, configuration, and
reports across the ATS, screening, interview, machine-test, aggregation,
recommendation, governance, and monitoring workstreams. A local integration
was added to invoke the actual prototype modules and pass their outputs
through the next stage.

The run used the Day 63 synthetic resume/job record for candidate `CAND-001`,
plus synthetic screening answers, HR ratings, technical answer ratings, and
machine-test results. It did not use real applicant information or contact
external services.

The Day 64 feedback record is an **internal technical assessment** based on
the repository walkthrough. The Day 45 manager feedback form in the
repository remains blank. No external mentor, recruiter, or hiring-manager
statement or approval is claimed.

## 4. ATS-to-decision walkthrough

| Stage | Implementation exercised | Sample result | Review notes |
|---|---|---:|---|
| ATS | Day 13 weighted ATS scorer using Day 10 experience relevance, Day 11 education parsing, resume/job skill coverage, and a documented lexical-overlap similarity proxy. | **44.86/100** | All five required skills matched; experience relevance scored 0 and education alignment 30. Investigate extraction and scoring evidence before interpreting this as suitability. |
| Screening | Day 32 question workflow and Day 26 screening scoring engine. Required answers are checked before scoring. | **91.75/100** | Rule-based heuristic score from four synthetic answers. It is not a validated measure of candidate quality. |
| HR interview | Day 33 interview phases and Day 37 HR interview scoring engine. | **85.00/100** | Four interview phases completed. Input rubric ratings were synthetic, not ratings from a real interviewer. |
| Technical interview | Day 47 rubric-based technical scoring. | **73.67/100** | Three synthetic answer records with manually supplied parameter ratings; this does not demonstrate automated technical correctness evaluation. |
| Machine test | Day 50 machine-test evaluator. | **80.25/100** | Three of four supplied execution results passed. Results and rubric values are input data; the prototype does not execute submitted code. |
| Aggregation | Day 51 role-weighted aggregation for five completed rounds. | **76.31/100; COMPLETE** | The configured data-analyst weights were applied and reported transparently. |
| Recommendation | Day 52 explainable recommendation engine. | **HOLD_REVIEW** | Advisory output. Human disposition is pending; no automatic employment action occurred. |

### Execution and safeguards

- Seven stages ran in order: ATS, screening, HR interview, technical
  interview, machine test, aggregation, and recommendation.
- The final score covered all five scored assessment rounds.
- The recommendation was `HOLD_REVIEW`.
- Human review was required; human disposition remained `PENDING`.
- Automatic employment action was `False`.
- One local synthetic run took **5.888 ms**. This is a smoke-test timing, not
  a production performance benchmark or service-level result.

## 5. Main findings

### Accuracy and scoring

1. **ATS recall needs investigation.** Day 20 reports 57.14% recall and three
   false negatives among 55 cases. The report's high accuracy should not be
   used without the confusion matrix and class balance.
2. **ATS component behavior needs inspection.** In the Day 64 synthetic case,
   all five required skills matched while the overall ATS score was 44.86.
   Experience relevance was 0 and education alignment was 30. The sample
   highlights an evidence-extraction/parser question; it does not prove the
   score is incorrect.
3. **Several scores are heuristic or supplied.** Screening uses rule-based
   heuristics. HR and technical rubric scores are manually supplied in this
   synthetic case. Machine-test execution results and rubric metrics are also
   supplied input.
4. **Synthetic evaluation is not real-world validation.** Day 56's agreement
   results use supplied synthetic labels; they are not independently verified
   ground truth.

### User experience

- The reviewed outputs are mainly scripts and JSON/Markdown reports; a
  production reviewer interface was not evaluated.
- The Day 63 dataset contains candidates with missing job or screening data.
  Their presentation and correction path in a reviewer interface have not
  been evaluated.
- The available Day 45 manager-feedback form is blank. The Day 64 internal
  feedback record documents code and workflow observations, not external
  user-research findings.

### Performance and operations

- Day 64 measured one local synthetic run at 5.888 ms. It excludes network,
  database, external model inference, and deployed services.
- No end-to-end concurrent load test, p95/p99 latency result, throughput
  target, or production service-level objective was evidenced.
- Day 61 contains observability plans and sample outputs, but the review did
  not verify telemetry wired to a deployed full workflow.

## 6. Internal reviewer feedback

The internal technical review found the stage structure and score
explanations useful for a prototype walkthrough. The synthetic pipeline is
reproducible, and the recommendation is clearly separated from a final human
employment decision.

The main concern is the ATS evidence discrepancy described above. Screening
and interview scoring also need validation with domain reviewers and
calibration data before decision-support reliance. The reviewer assessment
recommends using the system only for controlled demonstrations, keeping
synthetic results clearly labeled, and preserving mandatory human review.

This is an internal repository-based review record. It is not attributed to
an external mentor, hiring manager, recruiter, or candidate.

## 7. Prioritized improvement list

| Priority | Improvement | Reason |
|---|---|---|
| P0 | Investigate ATS false negatives and the Day 64 ATS component discrepancy; agree on evaluation metrics and release criteria before tuning. | Reduce the risk of qualified candidates being missed and avoid optimizing on accuracy alone. |
| P0 | Standardize candidate/session contracts, score scales, evidence provenance, and explicit stage states. | Make stage handoffs and incomplete evaluations unambiguous. |
| P0 | Keep recommendation, human disposition, and employment action separate; preserve human review and disable automatic rejection. | Prevent prototype scores from becoming autonomous hiring outcomes. |
| P1 | Validate screening, HR, and technical rubrics; assess reviewer agreement and question coverage. | Current results rely on heuristics and supplied ratings. |
| P1 | Improve reviewer UX to show stage status, evidence, missing information, explanation, and correction paths. | The repository review did not establish a usable end-user interface. |
| P1 | Define failure, timeout, retry, and resume behavior for integrated stages. | Missing or failed stages must not be mistaken for completed assessments. |
| P1 | Benchmark the integrated deployment under an agreed workload. | A single local run does not establish capacity or production latency. |
| P2 | Connect observability and audit events across the workflow with privacy controls. | Support traceability and incident review. |
| P2 | Link system claims to reproducible, versioned test evidence and label synthetic results. | Prevent demo metrics from being mistaken for validated production results. |

## 8. Action plan

| Phase | Work | Suggested owner role | Completion evidence |
|---|---|---|---|
| 1 | Review ATS false negatives, labels, cohort coverage, and score-component evidence. | Evaluation lead with recruiter/domain reviewers | Versioned evaluation protocol, reviewed baseline, and agreed recall/uncertainty criteria. |
| 2 | Define the shared candidate/session contract and stage-state semantics. | Technical lead / integration owner | Approved schema with score scale, evidence provenance, timestamps, and completed/pending/not-applicable/failed states. |
| 3 | Integrate the actual stage implementations and test error/retry/incomplete flows. | Integration engineer and component owners | End-to-end tests with traceable handoffs; no missing or failed stage silently becomes zero or complete. |
| 4 | Verify human-review decision safeguards at the final decision boundary. | Product and governance owners | Automated tests prove no automatic employment action and incomplete/contradictory inputs route to review. |
| 5 | Calibrate screening and interview rubrics. | HR and technical assessment leads | Versioned rubrics, dual-review agreement results, and documented disagreement resolution. |
| 6 | Evaluate reviewer experience and improve evidence visibility. | Product / UX owner | Usability session findings and dispositioned improvement items. |
| 7 | Conduct performance, reliability, and failure testing against agreed targets. | Performance / operations owner | Repeatable p50/p95/p99, throughput, resource, and error-rate report. |
| 8 | Complete audit, monitoring, privacy, and release-evidence controls. | Governance / operations owner | Traceable staging run, tested alerts/access/retention, and evidence-linked release checklist. |

These are recommended project actions identified by the review. The owners
are suggested roles, not named assignments.

## 9. Code, outputs, and run commands

### Day 64 files

- `day64_internal_review/src/walkthrough.py` - executes the local synthetic
  workflow and writes reports.
- `day64_internal_review/data/demo_case.json` - synthetic answers and supplied
  demo rubric/test inputs.
- `day64_internal_review/tests/test_walkthrough.py` - integration and
  missing-answer behavior tests.
- `day64_internal_review/output/end_to_end_walkthrough.json` - detailed stage
  output suitable for machine inspection.
- `day64_internal_review/output/end_to_end_walkthrough.md` - concise results
  summary.

### Run from the repository root in PowerShell

Run the end-to-end demonstration:

```powershell
python -m day64_internal_review.src.walkthrough
```

Run the Day 64 tests:

```powershell
python -m unittest day64_internal_review.tests.test_walkthrough -v
```

Run the connected Day 64 and stage regression suites:

```powershell
.\.venv\Scripts\python.exe -m pytest day64_internal_review\tests day26_screening_scoring_engine\tests day32_screening_system_finalization\tests day33_hr_interview_engine\tests day37_hr_interview_scoring_engine\tests day47_technical_skill_scoring\tests day50_machine_test_ai_design\tests day51_cross_round_aggregation_engine\tests day52_final_recommendation_ai\tests -q
```

**Observed validation:** 65 tests passed. One Day 51 partial-score test was
updated to assert the aggregation engine's existing two-decimal output
contract. `git diff --check` passed.

## 10. Limitations and responsible use

- All Day 64 walkthrough inputs are synthetic demonstration data.
- ATS similarity in the integration is a lexical-overlap proxy, not a
  semantic-embedding measurement.
- Screening scores are generated using demo heuristics.
- HR/technical ratings and machine-test execution results are supplied inputs.
- The machine-test prototype captures submitted code but does not execute it.
- The local integration does not connect to a production ATS, voice service,
  database, authentication system, or deployed model service.
- The local runtime is not a scalability or production-latency result.
- Scores are decision-support signals only. Human review is required; no
  automated employment action is made.

## 11. Conclusion

The Day 64 internal review package is complete: the repository was inspected,
a synthetic ATS-to-decision integration was executed, results and test
evidence were recorded, and accuracy, UX, performance, governance, and
integration improvements were prioritized.

The work confirms that the prototype modules can be connected for a local
demonstration. It also reveals concrete questions to investigate, particularly
the ATS false negatives and mismatch between skill coverage and the sample
ATS component scores. The project should represent these findings honestly:
the prototype is suitable for internal demonstration and continued
validation, but the available evidence does not establish production
readiness or real-world hiring effectiveness.
