# Windows setup and run

From `C:\Users\sayan\Documents\zecpath-ai-system` in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.create_recruiter
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

`src.create_recruiter` interactively prompts for a username and a password
without echoing it. It creates only the first account, enforces the password
policy, and stores a random salt plus PBKDF2-HMAC-SHA256 hash; there are no
default credentials. To replace a forgotten username/password, stop the
server, then run `.\.venv\Scripts\python.exe -m src.reset_recruiter`. Reset
revokes existing sessions. Credentials cannot be displayed/recovered.

Open `http://127.0.0.1:8000/`. Swagger is at
`http://127.0.0.1:8000/docs`; ReDoc at `http://127.0.0.1:8000/redoc`; OpenAPI
at `http://127.0.0.1:8000/openapi.json`. The port in the URL must match
Uvicorn's `--port`.

The default SQLite file is `data/zecpath.sqlite3`. To select another path,
set it before account setup and consistently before reset/server commands:

```powershell
$env:ZECPATH_DB_PATH = "$PWD\data\local-demo.sqlite3"
```

If a resume is to be semantically scored, download/cache the model once while
online:

```powershell
.\.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

Runtime model loading is local-only. If it is absent, resume scoring returns
HTTP 503; it does not pretend semantic inference succeeded. No remote model
service is called.

## Postman

Import `postman/ZecPath Recruiter API.postman_collection.json` and
`postman/ZecPath Local.postman_environment.json`. Set the environment's
recruiter username/password locally; never commit/export/share populated
credentials. Use the Postman cookie jar for the HTTP-only session, follow
request order, and select a synthetic file for the upload request. The
collection JSON is validated but has not been run with Postman/Newman.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_api.py -q
.\.venv\Scripts\python.exe -m pytest -q
```

For a feature/data walkthrough, see the root README and
[integration report](day01_day68_integration_report.md). Use synthetic data;
the local prototype is not production-ready.
