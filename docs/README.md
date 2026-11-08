# Zecpath documentation index

This folder is the entry point for current, evidence-based project
documentation. Historical stage-specific reports remain in their original
folders so their inputs, code, tests, and outputs stay together. The presence
of a stage report does not mean that stage is integrated into the root
recruiter application.

## Current application documentation

- [Project README](../README.md) — setup, account initialization, environment
  variables, API reference, tests, limitations, and local demo workflow.
- [Verified root architecture](architecture/ATS_Architecture.md) — actual app
  entrypoint and data flow.
- [System architecture](system_architecture.md) — current root-app components,
  trust boundaries, and integrated versus prototype stages.
- [Database schema](database_schema.md) — SQLite tables, relationships, and
  persistence behavior.
- [API documentation](api_documentation.md) — root route contracts and auth
  requirements.
- [Setup and run guide](setup_and_run.md) — Windows commands, first account,
  reset, URL, Postman, and tests.
- [ATS scoring methodology](ats_scoring_methodology.md) — active Day 9–13
  inputs, weights, formula, and cautions.
- [Day 13 scoring methodology](day13_ats_scoring_methodology.md) — root
  component evidence, missing-data behavior, and unvalidated-score limits.
- [Resume processing](resume_processing.md) — upload validation, extraction,
  retention, and failure behavior.
- [Known limitations](known_limitations.md) — integration boundary and
  operational gaps.
- [Testing report](testing_report.md) — measured tests and synthetic browser
  verification.
- [Day 1–15 task-level audit](day01_day15_implementation_audit.md),
  [implementation report](day01_day15_implementation_report.md),
  [test report](day01_day15_test_report.md), and
  [known limitations](day01_day15_known_limitations.md) — first-fifteen-day
  status with evidence and blockers.
- [Progress checkpoint](day01_day15_implementation_progress.md) — remaining
  work for the Day 1–15 scope.
- [Day 1–68 audit](day01_day68_audit.md) and
  [integration report](day01_day68_integration_report.md) — inventory,
  evidence, verification gates, and explicit limits.
- [Developer guide](developer_guide/Developer_Guide.md) — Windows setup,
  testing, and troubleshooting.
- [Daily report catalog](daily_reports.md) — historical module themes and
  selected evidence.
- [AI roadmap](ai_roadmap.md) — implemented deterministic capabilities versus
  proposed AI work.
- [Day 16/20 integration and verification](day16_day20_integration.md) —
  distinguishes the standalone Day 16 demo from the root API and documents the
  Day 9-13 scoring integration and evidence.
- [Days 16–23 audit](day16_day23_implementation_audit.md),
  [implementation report](day16_day23_implementation_report.md),
  [test report](day16_day23_test_report.md),
  [known limitations](day16_day23_known_limitations.md), and
  [progress checkpoint](day16_day23_implementation_progress.md) — current
  phase status and evidence.
- [Day 16 root API integration](day16_root_api_integration.md),
  [Day 17 ATS evaluation](day17_ats_evaluation.md),
  [Day 18 performance validation](day18_performance_validation.md),
  [Day 19 root technical documentation](day19_root_technical_documentation.md),
  [Day 20 scoring review](day20_scoring_review.md),
  [Day 21 eligibility](day21_eligibility_decision_support.md),
  [Day 22 screening questions](day22_screening_question_bank.md), and
  [Day 23 transcript architecture](day23_transcript_data_architecture.md).
- [Postman collection](../postman/ZecPath%20Recruiter%20API.postman_collection.json)
  and [local environment](../postman/ZecPath%20Local.postman_environment.json)
  — synthetic recruiter API workflow; no credentials are included.
- [Internship portfolio](internship_portfolio.md) — evidence-based portfolio
  summary.

## Day 68 release-readiness submission

- [Repository audit](../day68_release_readiness/day68_audit_report.md)
- [Bug-fix report](../day68_release_readiness/day68_bug_fix_report.md)
- [Integration report](../day68_release_readiness/day68_integration_report.md)
- [Test report](../day68_release_readiness/day68_test_report.md)
- [Security report](../day68_release_readiness/day68_security_report.md)
- [Performance report](../day68_release_readiness/day68_performance_report.md)
- [Final validation](../day68_release_readiness/day68_final_validation.md)
- [Release notes](../day68_release_readiness/day68_release_notes.md)
- [Final ATS report](reports/Final_ATS_Report.md)

## Existing technical and governance documents

- [Day 15 fairness notes](bias_reduction.md) — stage-level fairness methods.
  The root now applies limited personal-data masking in semantic matching;
  this does not constitute a fairness evaluation. See
  [Day 15 integration status](day15_fairness_normalization_and_bias_reduction.md).
- [Day 24 speech-to-text notes](day24_documentation.md) — Faster-Whisper
  prototype and limitations; not connected to root API workflows.
- [Day 19 ATS developer guide](../day19_ats_documentation/docs/ATS_Technical_Documentation.md)
- [Day 20 production-readiness checklist](../day20_ats_final_review/docs/Production_Readiness_Checklist.md)
- [Day 43 ethics/compliance documentation](../day43_ethics_compliance_review/docs/ai_ethics_documentation.md)
- [Day 55 security governance framework](../day55_security_ai_governance/docs/security_framework.md)
- [Day 60 synthetic benchmark report](../day60_performance_scalability/output/benchmark_report.md)
- [Day 61 observability prototype](../day61_ai_monitoring_observability/README.md)
- [Day 62 technical handbook](../day62_documentation_master_file/README.md) — includes explicit caveats that its planned architecture/API items need source verification.
- [Day 64 internal review](../day64_internal_review/README.md)
- [Day 65 final enhancements](../day65_final_enhancements_feature_polish/README.md)

## Documentation accuracy

The root app is a small local FastAPI service and dashboard. Many numbered
folders are independent exercises, simulations, or plans. Consult the current
root API, schemas, tests, and [Day 1–68 integration report](day01_day68_integration_report.md)
before describing a historical module as a live feature. No document here
certifies production readiness.