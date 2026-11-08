# Day 3 — Environment and repository setup

## Verified environment

The repository includes `.venv`; root `requirements.txt` pins pytest and
constrains FastAPI, HTTPX, python-docx, python-multipart, pypdf,
sentence-transformers, and Uvicorn. The documented and previously verified
runtime is Python 3.12. The complete repository suite passed before this
change set; this run also uses the existing `.venv`. Do not recreate the
environment or modify dependency versions just to repeat setup.

## Windows PowerShell

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
.\.venv\Scripts\python.exe -m pytest -q
```

The install command is only needed when restoring a new environment or after
dependency changes. Initialize the first recruiter through
`python -m src.create_recruiter`; the script prompts for credentials and
stores a salted password hash. `ZECPATH_DB_PATH` may point to a disposable
test database. Do not initialize/reset accounts against a production or
unintended database.

## Repository and standards

`src/` is the actual FastAPI/SQLite application; `day*` packages are
stage-specific exercises unless imported by `src/`. Tests use pytest,
HTTPX, and isolated databases. Use type hints on maintained root code,
Pydantic request/response validation, parameterized SQL, explicit API errors,
and synthetic data. Logs must not contain credentials, tokens, or full resume
text. Secrets are not loaded from a committed `.env`; keep credentials in
interactive setup or an approved secret manager.

See [project structure](project_structure.md) and the existing
[setup guide](setup_and_run.md). Central log configuration exists in
`src/logging_config.py`; it logs to `logs/ats_api.log` and console. Log
rotation, structured correlation IDs, and model timing metrics are not
implemented.
