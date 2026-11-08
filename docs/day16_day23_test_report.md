# Days 16–23 test report

## Latest focused verification

Run from the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m compileall -q src
.\.venv\Scripts\python.exe -m pytest -q tests\test_day16_day23.py tests\test_schemas.py
.\.venv\Scripts\python.exe -m src.validate_screening_dataset
```

Latest observed results during this phase:

- `compileall -q src`: passed.
- `pytest -q tests\test_day16_day23.py tests\test_schemas.py`: **11 passed**.
- `pytest -q`: **497 passed in 85.01s** on the final code/test tree.
- screening dataset validator: **17 questions, 13 registered roles, 7
  categories**.
- `git diff --check`: passed after the implementation and documentation edits.

The API test module was also run with the focused API tests before the
end-to-end case was added: **39 passed** across
`tests/test_day16_day23.py` and `tests/test_api.py`. This is a historical
focused result, superseded for overall test coverage by the 497-test full run.

## End-to-end workflow exercised

The focused synthetic TestClient scenario logs in using the existing
recruiter session, parses explicitly labeled JD fields, creates a confirmed
opening and candidate, uploads and extracts a synthetic TXT resume, requests a
score and persisted shortlist, configures and retrieves eligibility, filters
screening questions, and stores/retrieves transcript data. The question and
transcript shapes are checked against the documented schemas where applicable.
Embedding inference is deterministic and monkeypatched in this API fixture;
this is an integration-contract test, not a production model evaluation.

## Not measured or not run

- No browser-driven visual or interaction regression was run.
- No reviewer-labeled ATS performance metrics are available.
- No performance baseline or repeated benchmark was run.
- No subgroup fairness evaluation was run.
- No real audio or speech-recognition workflow exists to test.
