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
- [Developer guide](developer_guide/Developer_Guide.md) — Windows setup,
  testing, and troubleshooting.
- [Daily report catalog](daily_reports.md) — historical module themes and
  selected evidence.
- [AI roadmap](ai_roadmap.md) — implemented deterministic capabilities versus
  proposed AI work.
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

- [Day 15 fairness notes](bias_reduction.md) — stage-level fairness methods;
  not connected to root match scores.
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
root API, schemas, tests, and [integration report](../day68_release_readiness/day68_integration_report.md)
before describing a historical module as a live feature. No document here
certifies production readiness.