# ZecPath AI Hiring System — Developer Onboarding Guide

Welcome to the **ZecPath AI Hiring System** codebase! This guide is designed to get new backend, AI, and full-stack developers up to speed quickly and safely.

---

## 1. Quickstart & Local Setup

### Prerequisites
- **Python:** 3.12 (Python 3.12.4 recommended).
- **Git:** Standard Git CLI.
- **Operating System:** Windows, macOS, or Linux.

### Environment Setup
```powershell
# 1. Clone or navigate to the repository
cd C:\Users\sayan\Documents\zecpath-ai-system

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # On Windows PowerShell
# source .venv/bin/activate    # On Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt
```

### Initializing the Recruiter Account
```powershell
# Create the first local recruiter account
.\.venv\Scripts\python.exe -m src.create_recruiter
# (Follow prompts to enter your recruiter username and secure password)
```

### Running the Application
```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```
- Open your browser at: `http://127.0.0.1:8000/`
- Explore the interactive Swagger API documentation at: `http://127.0.0.1:8000/docs`

---

## 2. Directory Structure & Key Files

| Directory / File | Description |
|---|---|
| `src/main.py` | FastAPI application root, lifespan startup, HTTP observability middleware. |
| `src/api.py` | Consolidated REST API router containing all recruitment routes. |
| `src/database.py` | Relational SQLite schema, migrations, connection context manager, and CRUD functions. |
| `src/schemas.py` | Pydantic request and response models enforcing strict type safety. |
| `src/auth.py` | Recruiter password hashing (PBKDF2), session cookie creation, and Same-Origin checks. |
| `src/ats_scoring_engine.py` | Weighted ATS score formula (Skills 40%, Semantic 25%, Experience 20%, Education 15%). |
| `src/hiring_intelligence_report_generator.py` | Multi-round compiler producing JSON, Markdown, and HTML reports. |
| `src/observability.py` | Centralized structured logging, operational metrics, and decision auditing. |
| `static/index.html` | Recruiter dashboard frontend written in vanilla JS and modern CSS. |
| `tests/` | Complete automated test suite (101 unit and integration tests). |

---

## 3. How the Request Flow Works

```
Browser / Client Request
       │
       ▼
src/main.py (Observability Middleware: starts timer, logs request)
       │
       ▼
src/api.py (Route Handler)
       │
  ├──► src/auth.py (Validates Same-Origin header and recruiter session cookie)
  ├──► src/schemas.py (Validates request body)
  ├──► src/database.py (Executes atomic SQLite transactions)
  └──► src/*_engine.py (Executes AI matching, scoring, or compilation)
       │
       ▼
Response Returned -> Middleware logs duration_ms, status_code to logs/api_logs.jsonl
```

---

## 4. How to Add a New Feature Safely

### Adding a New API Endpoint
1. Define Pydantic request and response models in [`src/schemas.py`](file:///c:/Users/sayan/Documents/zecpath-ai-system/src/schemas.py).
2. Add database helper functions in [`src/database.py`](file:///c:/Users/sayan/Documents/zecpath-ai-system/src/database.py) using the `_connection()` context manager.
3. Add the route handler in [`src/api.py`](file:///c:/Users/sayan/Documents/zecpath-ai-system/src/api.py) with `recruiter: dict = Depends(require_recruiter)` for protection.
4. Add unit and integration tests in `tests/test_*.py`.

### Updating Scoring Logic
- **Rule:** Never introduce hardcoded scores or arbitrary weights without documenting them in [`src/ats_scoring_engine.py`](file:///c:/Users/sayan/Documents/zecpath-ai-system/src/ats_scoring_engine.py) and updating the technical handbook.
- **Rule:** Every score change must be traceable to candidate evidence (skills, parsed text, or interview answers).

---

## 5. Running Tests

```powershell
# Run all tests
.\.venv\Scripts\python.exe -m pytest tests/ -v

# Run dedicated Day 53–60 tests
.\.venv\Scripts\python.exe -m pytest tests/test_day53_day60.py -v
```

---

## 6. Contribution Guidelines

- Preserve existing comments and docstrings.
- Always run `python -m compileall src tests` before committing.
- Ensure all 101 tests pass with zero regressions.
- Do not commit secrets, session tokens, or personal candidate data.

