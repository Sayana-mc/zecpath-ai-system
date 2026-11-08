# Day 1–15 test report

## Commands executed

| Command | Result | Scope |
|---|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q` | **483 passed** in 85.31s | Full repository baseline before this change set |
| `.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py tests/test_fairness.py day8_resume_section_segmentation/tests day11_education_certification/tests` | **50 passed** in 42.43s | Focused integration before adding the Day 10 overlap regression and schema tests |
| Focused suite including API, schemas, synthetic samples, and Day 8/10/11 tests | **58 passed, 1 failed** in 368.31s; the failing overlap test exposed ISO date parsing as year-only | Intermediate run; fixed by parsing ISO dates before year-only dates |
| `.\.venv\Scripts\python.exe -m pytest -q day10_experience_relevance\tests\test_experience_engine.py tests\test_schemas.py tests\test_synthetic_resume_samples.py tests\test_api.py::test_scoring_extracts_sections_certifications_and_masks_personal_data` | **11 passed** in 24.47s | Re-tested overlap fix, schemas, ten synthetic profiles, and upload/scoring integration |
| `.\.venv\Scripts\python.exe -m pytest -q` | **487 passed** in 171.38s | Full repository suite after runtime changes and initial schema tests |
| `.\.venv\Scripts\python.exe -m pytest -q tests\test_schemas.py tests\test_synthetic_resume_samples.py` | **2 passed** in 7.56s | Final schema test also validates all ten extracted synthetic profiles |
| `git diff --check` and `python -m compileall -q` for changed Python modules | **Passed** | Whitespace and syntax checks |
| Built-in JSON parsing of `docs/schemas/*.json` | **4 valid JSON files** | Syntax only; instance contracts are covered by `tests/test_schemas.py` |

## Test evidence and limits

- Root API tests use temporary SQLite paths and a deterministic test embedding
  engine. They do not touch the user's configured database.
- The new API test exercises TXT upload → parsed profile persistence →
  sanitized semantic input → score response and certification profile.
- Day 10 has a regression for overlapping dated intervals.
- Existing tests cover authentication, CRUD, resume formats/errors, scoring,
  persistence, ranking, and stage modules.
- JSON Schema files are checked against Draft 2020-12 and validated with
  synthetic examples in `tests/test_schemas.py`.
- Mermaid diagrams were reviewed for syntax, but no Mermaid renderer/parser
  was run.
- No live browser, production API, OCR, fairness subgroup test, stress/load
  test, or current real-model performance measurement was run in this pass.
