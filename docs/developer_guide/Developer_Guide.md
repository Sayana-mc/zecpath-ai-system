# Developer guide (Windows)

## Requirements

- Windows PowerShell.
- Python 3.12; the current full suite was executed with Python 3.12.4.
- Git.

The root API dependencies are listed in `requirements.txt`. Stage folders may
have their own requirements; do not assume every optional historical-stage
package is installed in the root environment.

## Install and initialize

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.create_recruiter
```

The initializer creates the first recruiter account in the configured SQLite
database, asks for a username and 16+ character password, and saves a salted
PBKDF2 hash. It refuses to overwrite an existing account. To set a new username
and password later, stop Uvicorn and run
`.\.venv\Scripts\python.exe -m src.reset_recruiter`; the reset revokes active
sessions. If using a custom database, set `ZECPATH_DB_PATH` before running the
initializer, reset command, and server.

## Run and inspect the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the dashboard,
`http://127.0.0.1:8000/docs` for Swagger, and
`http://127.0.0.1:8000/api/v1/health` for the public database-backed health
check. The browser URL must use the same port shown by Uvicorn. Do not open
`static/index.html` directly from disk: the dashboard uses same-origin API
URLs.

## Tests and checks

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m py_compile src\api.py src\auth.py src\database.py src\schemas.py src\create_recruiter.py src\reset_recruiter.py
.\.venv\Scripts\python.exe -m pip check
git --no-pager diff --check
```

The root API test suite uses isolated temporary SQLite databases. The full
pytest command also runs stage-level tests; those tests do not imply the
corresponding stage is connected to the root app.

## Troubleshooting and data protection

- `authentication_configured: false`: run
  `.\.venv\Scripts\python.exe -m src.create_recruiter` from the repository
  root. If you have forgotten the credentials, stop Uvicorn and run
  `.\.venv\Scripts\python.exe -m src.reset_recruiter`; passwords cannot be
  retrieved.
- Sign-in is throttled after five failures for a username/client address for
  15 minutes.
- Dashboard session duration is eight hours; sign in again after expiry.
- Resume extraction supports TXT, DOCX, and text-based PDF up to 5 MiB. OCR is
  not configured.
- The database and resume text are unencrypted. Use only synthetic data and
  bind the local service to `127.0.0.1`.
- Stop the API before making a local SQLite file backup. There is no automated
  backup, restore, or versioned migration tool.

For endpoint shapes and the demo journey, see the [root README](../../README.md).