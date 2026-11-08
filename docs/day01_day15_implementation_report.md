# Day 1–15 implementation report

## A. Executive summary

The root application already had a local recruiter workflow with resume
upload, Day 9–13 scoring, persisted evidence, and job-specific review
suggestions. This implementation pass connected Day 8 segmentation and Day 11
certification parsing to the resume profile, removed common labeled personal
data from semantic matching input, corrected full-name certification
normalization, and prevented double-counting overlapping dated roles. Ten
clearly synthetic resume fixtures and three synthetic job-description
fixtures were added.

**Overall status: PARTIAL.** The product PRD is unavailable, the Day 6 parser
is not integrated into job creation, Day 5 OCR is absent, and no validated
fairness or hiring-performance evaluation exists. This report does not claim
all Day 1–15 acceptance criteria are met.

## Work completed in this pass

- Updated `src/resume_analysis.py` to segment resumes and extract skills,
  experience, education, and certifications from relevant sections with
  fallback behavior.
- Updated `src/integrated_scoring.py` to use sanitized resume matching text,
  use that same text for exact-match evidence, and surface limited fairness
  safeguard metadata.
- Expanded Day 8 section names for summary/objective/achievements/publications/
  languages.
- Fixed Day 11 credential normalization so canonical prefixes do not truncate
  the rest of the certificate name.
- Changed Day 10 total experience to merge overlapping dated intervals and
  added a regression test.
- Added an upload-to-score integration regression test for segmentation,
  certification persistence, and personal-data masking.
- Added JSON Schema contract tests for all four Day 4 schemas and a synthetic
  resume extraction smoke test.
- Added ten synthetic resume text fixtures and three synthetic job
  descriptions.
- Added the requested Day 1–15 docs, schemas, and Mermaid diagrams. They
  explicitly report incomplete or blocked requirements rather than presenting
  prototypes as live features.

No API route or database table was added in this pass. `jsonschema` was added
to `requirements.txt` for schema validation tests. Existing database records
are not modified by tests.

## B. Day-by-day status

Detailed task-level evidence, status, and remaining work are in
[`day01_day15_implementation_audit.md`](day01_day15_implementation_audit.md).

| Day | Final status | Key evidence |
|---:|---|---|
| 1 | PARTIAL / PRD BLOCKED | Overview, module inventory, lifecycle diagram |
| 2 | PARTIAL | Current modular-monolith architecture and I/O docs |
| 3 | PARTIAL | Existing environment, logging, repository map |
| 4 | PARTIAL | Synthetic fixtures and JSON schemas |
| 5 | PARTIAL | Root text extraction/upload; no OCR or layout guarantee |
| 6 | PARTIAL | Prototype normalization; raw JD parser not root-integrated |
| 7 | PARTIAL | Root persistence path documented; version history absent |
| 8 | PARTIAL | Segmenter integrated; no evaluated accuracy |
| 9 | PARTIAL | Rule-based dictionary integrated; no corpus metrics |
| 10 | PARTIAL | Date parser integrated; overlap union fixed; relevance incomplete |
| 11 | PARTIAL | Education/certification extraction integrated; scoring relevance partial |
| 12 | PARTIAL | Local semantic model integrated; no validated thresholds/cache |
| 13 | PARTIAL | Explainable weighted heuristic integrated; no validated model |
| 14 | PARTIAL | Persisted job-scoped ranking; one cutoff only |
| 15 | PARTIAL / FAIRNESS METRICS BLOCKED | Basic masking applied; no lawful subgroup data or audit |

## C. Implementation details

New docs/diagrams/schemas:

- `docs/day01_zecpath_ai_responsibilities_overview.md`
- `docs/day01_ai_module_inventory.md`
- `docs/diagrams/day01_hiring_lifecycle.mmd`
- `docs/day02_ai_system_architecture.md`
- `docs/diagrams/day02_ai_architecture.mmd`
- `docs/diagrams/day02_ai_data_flow.mmd`
- `docs/day02_ai_engine_input_output_specification.md`
- `docs/day03_environment_and_repository_setup.md`
- `docs/project_structure.md`
- `docs/day04_ai_data_entity_design.md`
- `docs/schemas/resume_schema.json`
- `docs/schemas/job_description_schema.json`
- `docs/schemas/skill_schema.json`
- `docs/schemas/experience_schema.json`
- `docs/day05_resume_text_extraction.md`
- `docs/day06_job_description_parsing.md`
- `docs/day07_ai_data_pipeline.md`
- `docs/diagrams/day07_ai_data_pipeline.mmd`
- `docs/day07_ai_storage_design.md`
- `docs/day07_ai_metadata_standards.md`
- `docs/day08_resume_section_segmentation.md`
- `docs/day09_skill_extraction.md`
- `docs/day10_experience_parsing_and_relevance.md`
- `docs/day11_education_and_certification_parsing.md`
- `docs/day12_semantic_matching.md`
- `docs/day13_ats_scoring_methodology.md`
- `docs/day14_candidate_ranking_and_shortlisting.md`
- `docs/day15_fairness_normalization_and_bias_reduction.md`
- This report, audit, test report, known limitations, and progress tracker.

Modified runtime/test files:

- `src/resume_analysis.py`
- `src/integrated_scoring.py`
- `day8_resume_section_segmentation/src/section_patterns.py`
- `day8_resume_section_segmentation/src/segmentation_engine.py`
- `day10_experience_relevance/src/experience_parser.py`
- `day10_experience_relevance/tests/test_experience_engine.py`
- `day11_education_certification/src/certification_parser.py`
- `day11_education_certification/tests/test_education_engine.py`
- `tests/test_api.py`
- `tests/test_schemas.py`
- `tests/test_synthetic_resume_samples.py`
- `requirements.txt` (`jsonschema>=4.22,<5.0`)

Synthetic data lives in `datasets/test/resumes/` and
`datasets/test/job_descriptions.json`.

### Database, APIs, UI, and dependencies

No database migration or endpoint was added. Existing resume upload, scoring,
and shortlist APIs are used as-is.
Certification and section data flow through existing resume profile JSON.
The existing local `all-MiniLM-L6-v2` model remains required for semantic
scoring of resumes; no new model or external provider was added.

## D. Test results

The full repository suite passed **487 tests** after runtime changes. A
subsequent targeted run of the strengthened schema/profile checks passed
**2 tests**, and focused overlap/API regressions passed **11 tests**. Exact
commands, an intermediate failure and its fix, compile checks, and unrun
validation gates are in [`day01_day15_test_report.md`](day01_day15_test_report.md).

## E. Deliverables

All 32 requested Day 1–15 documentation, schema, and diagram deliverables
exist. The task-level audit records evidence/status for each requirement. The
[synthetic test dataset](../datasets/test/) contains ten resumes and three job
profiles.

## F. Remaining limitations

The PRD, robust raw-JD parsing/integration, OCR, complete extraction metadata,
versioned score history, complete role-relevance scoring, confidence-aware
shortlist zones, full personal-data de-identification, fairness evaluation,
and production privacy/operations controls remain open. The next
implementation steps are recorded in
[`day01_day15_implementation_progress.md`](day01_day15_implementation_progress.md).

## G. How to run

From the repository root in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.create_recruiter
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Only run the install command when setting up a new environment or after a
dependency change. The account initializer prompts securely and creates an
account only when none exists; it does not display or change an existing
password. Open Swagger at `http://127.0.0.1:8000/docs`.

In another PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q tests\test_api.py::test_scoring_extracts_sections_certifications_and_masks_personal_data
```

The API tests use a temporary database and synthetic data. There is no
standalone end-to-end CLI or browser automation command in this change set;
the focused API test exercises upload, profile persistence, scoring, and
personal-data filtering.
