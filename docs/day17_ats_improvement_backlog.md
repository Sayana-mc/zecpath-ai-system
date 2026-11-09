# Day 17 — ATS Improvement Backlog

## Status: PENDING EVALUATION DATA

This backlog will be populated after human-reviewed evaluation data is available. Current items are based on known architectural limitations and Day 1-15 audit findings.

## Prioritization Framework

| Priority | Criteria |
|----------|----------|
| P0 — Critical | Blocks evaluation, causes incorrect rejections, security issue |
| P1 — High | Significant accuracy impact, frequent occurrence |
| P2 — Medium | Measurable improvement, moderate effort |
| P3 — Low | Nice-to-have, minor impact, exploratory |

## Backlog Items

### P0 — Critical

| ID | Title | Description | Effort | Blocked By |
|----|-------|-------------|--------|------------|
| P0-1 | Collect labeled evaluation dataset | Minimum 100+ double-reviewed candidate/job pairs with decisions | High | Org approval, reviewer recruitment |
| P0-2 | Define "correct match" policy | Document what constitutes SHORTLISTED/REVIEW/REJECTED for each role type | Medium | Stakeholder alignment |
| P0-3 | Fix semantic model availability | Day 12 embeddings fail if sentence-transformers/model not cached | Low | Dependency setup |

### P1 — High

| ID | Title | Description | Effort | Blocked By |
|----|-------|-------------|--------|------------|
| P1-1 | Skill synonym normalization | Expand normalizer beyond current mappings (e.g., "PySpark"→"Spark", "k8s"→"Kubernetes") | Medium | Day 9 skill_normalizer |
| P1-2 | Experience overlap detection | Prevent double-counting concurrent roles | Medium | Day 10 experience parser |
| P1-3 | Section-aware extraction | Day 8 segmentation not fully scoping Day 9-11 extractors | Medium | Day 8-11 integration |
| P1-4 | Education equivalence | Map "B.Tech", "B.E.", "Bachelor of Technology" to same level | Low | Day 11 education parser |
| P1-5 | Score threshold calibration | Current thresholds arbitrary; need data-driven calibration | Medium | P0-1 evaluation data |
| P1-6 | Missing data handling | "No education found" → 0 score penalizes candidates unfairly | Low | Day 13 scoring params |

### P2 — Medium

| ID | Title | Description | Effort | Blocked By |
|----|-------|-------------|--------|------------|
| P2-1 | Resume format coverage | Improve PDF/DOCX extraction reliability (tables, columns, headers) | High | Day 5 extraction |
| P2-2 | Multi-language resume support | Non-English resume parsing | High | NLP models |
| P2-3 | Project/portfolio extraction | Extract GitHub, portfolio links as evidence | Medium | Day 9-11 extractors |
| P2-4 | Certification parsing | Structured certification extraction (AWS, Azure, PMP, etc.) | Medium | Day 11 |
| P2-5 | Soft skill detection | Identify leadership, communication from experience descriptions | High | NLP/classification |
| P2-6 | Candidate comparison view | Side-by-side skill/experience comparison for recruiters | Medium | Frontend |
| P2-7 | Score explanation UX | Human-readable breakdown for recruiters | Medium | Frontend |
| P2-8 | Batch scoring API | Score multiple candidates per job in one request | Low | API design |

### P3 — Low / Exploratory

| ID | Title | Description | Effort | Blocked By |
|----|-------|-------------|--------|------------|
| P3-1 | Learning-to-rank | Train ranker on human decisions (future) | Very High | P0-1, large dataset |
| P3-2 | Bias mitigation | Subgroup fairness metrics and constraints | High | P0-1, demographic data |
| P3-3 | Active learning | Flag uncertain scores for priority review | Medium | P0-1 |
| P3-4 | Resume versioning | Track candidate profile changes over time | Low | Database schema |
| P3-5 | JD versioning | Track job requirement changes | Low | Database schema |
| P3-6 | Explainable AI | SHAP/LIME for score components | High | Model access |
| P3-7 | Market salary integration | External salary data for salary expectation questions | Medium | External API |

## Completed Items (This Phase)

| ID | Title | Completed In |
|----|-------|--------------|
| — | Resume upload with background processing | Day 16 |
| — | Conservative JD parser with evidence | Day 16 |
| — | ATS scoring with evidence persistence | Day 16 (integrates Day 9-13) |
| — | Persisted shortlisting from saved scores | Day 16 (integrates Day 14) |
| — | Eligibility engine with fingerprint re-eval | Day 21 |
| — | Screening question bank with translations | Day 22 |
| — | Transcript session/segment/interaction storage | Day 23 |
| — | Metric calculation helpers | Day 17 |
| — | Dataset validation CLI | Day 22 |

## Tracking

- **Source of truth:** This document + GitHub Issues (when created)
- **Review cadence:** After each evaluation cycle
- **Owner:** AI/ML Engineering lead

## Related Files

- `docs/day17_ats_testing_report.md` — Test execution results
- `docs/day17_ats_accuracy_metrics.md` — Metric definitions
- `docs/day17_ats_mismatch_analysis.md` — Mismatch taxonomy
- `docs/day16_day23_known_limitations.md` — Current limitations