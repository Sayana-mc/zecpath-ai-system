# Day 19 — ATS Developer Guide

## Quick Start

### Prerequisites
- Python 3.12+
- Virtual environment (`.venv/`)
- sentence-transformers model cached locally

### Setup

```powershell
# Activate virtual environment
. .venv/Scripts/Activate.ps1

# Verify dependencies
python -m compileall -q src

# Initialize database (auto on startup)
python -m src.main
```

### Running the Server

```powershell
# Development (auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1
```

### First Recruiter Account

```powershell
# Create first account (run once)
python -m src.create_recruiter <username> <password>

# Or reset existing
python -m src.reset_recruiter <username> <new_password>
```

### Access Points

- **API:** `http://localhost:8000/api/v1/`
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Dashboard:** `http://localhost:8000/`

## Project Structure

```
zecpath-ai-system/
├── src/                      # Root application
│   ├── main.py              # FastAPI app entry point
│   ├── api.py               # All API routes
│   ├── schemas.py           # Pydantic models
│   ├── database.py          # SQLite persistence
│   ├── auth.py              # Authentication
│   ├── services.py          # Core business logic
│   ├── resume_analysis.py   # Data extraction
│   ├── integrated_scoring.py # Day 9-13 scoring
│   ├── eligibility.py       # Eligibility engine
│   ├── screening_questions.py # Question bank
│   ├── job_description_parser.py # JD parsing
│   ├── ats_evaluation.py    # Metric helpers
│   ├── validate_screening_dataset.py # Dataset validator
│   └── __init__.py
├── data/                    # Persistent data
│   ├── zecpath.sqlite3     # Database
│   ├── uploads/            # Resume files (temp)
│   └── screening/          # Question bank JSON
├── static/                  # Frontend
│   └── index.html          # Dashboard
├── tests/                   # Test suite
├── docs/                    # Documentation
├── day*/                    # Historical day modules
└── .venv/                   # Virtual environment
```

## Common Development Tasks

### Adding a New API Endpoint

1. Define request/response schemas in `src/schemas.py`
2. Add route function in `src/api.py`
3. Add database operations in `src/database.py` if needed
4. Write test in `tests/test_api.py`
5. Run tests: `python -m pytest tests/test_api.py::test_new_endpoint -v`

### Modifying Scoring Weights

Scoring weights are defined in `day13_ats_scoring/src/scoring_parameters.py`. The root application uses these via `integrated_scoring.py`.

**To change weights safely:**
1. Update `scoring_parameters.py`
2. Increment scoring version in `integrated_scoring.py`
3. Run scoring tests: `python -m pytest tests/test_api.py::test_score_uses_saved_candidate_and_job_evidence -v`
4. Verify existing scores are invalidated (opening update clears candidate scores)

### Adding a New Skill

Skills are normalized via `day9_skill_extraction.src.skill_normalizer.normalize_skill_name()`.

**To add a skill synonym:**
1. Update the normalizer's mapping in `day9_skill_extraction/src/skill_normalizer.py`
2. Test: `python -m pytest tests/test_ats_scoring_engine.py -v`
3. Re-score affected candidates (opening update triggers invalidation)

### Adding a New Job Category

1. Add role to `data/screening/hr_screening_questions.json`:
   ```json
   "roles": {
     "NEW_ROLE": "New Role Label"
   }
   ```
2. Add questions for the role (see Day 22 documentation)
3. Validate: `python -m src.validate_screening_dataset`
4. Test API: `GET /api/v1/screening/questions?role_id=NEW_ROLE`

### Adding a New Question Category

1. Add category to `data/screening/hr_screening_questions.json`:
   ```json
   "categories": [..., "NEW_CATEGORY"]
   ```
2. Add to `data/screening/question_category_mapping.json`:
   ```json
   "NEW_CATEGORY": {
     "label": "New Category",
     "purpose": "...",
     "permitted_answer_types": ["TEXT"]
   }
   ```
3. Update `src/schemas.py` `ScreeningQuestionResponse` category enum if needed
4. Validate and test

### Modifying Eligibility Rules

Eligibility rules are configured per-job via API, not hardcoded.

**To add a new rule type:**
1. Update `EligibilityConfigurationRequest` in `src/schemas.py`
2. Add evaluation logic in `src/eligibility.py`
3. Update `EligibilityEvaluationResponse` with new result fields
4. Add database migration if new columns needed
5. Write tests in `tests/test_day16_day23.py`

## Testing

### Run All Tests
```powershell
python -m pytest tests/ -v
```

### Run Specific Test Modules
```powershell
# API tests
python -m pytest tests/test_api.py -v

# Day 16-23 integration tests
python -m pytest tests/test_day16_day23.py -v

# Schema validation
python -m pytest tests/test_schemas.py -v

# Scoring engine
python -m pytest tests/test_ats_scoring_engine.py -v

# Fairness
python -m pytest tests/test_fairness.py -v
```

### Test with Coverage
```powershell
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Validate Screening Dataset
```powershell
python -m src.validate_screening_dataset
# Output: 17 questions, 13 registered roles, 7 categories
```

## Database Operations

### Direct SQLite Access
```powershell
# Open database
sqlite3 data/zecpath.sqlite3

# Useful queries
.tables
.schema candidates
SELECT opening_id, title, status FROM openings;
SELECT candidate_id, name, score, application_status FROM candidates;
SELECT * FROM processing_jobs ORDER BY created_at DESC LIMIT 10;
```

### Reset Database (Development Only)
```powershell
# Delete database file (recreated on startup)
Remove-Item data/zecpath.sqlite3
# Recreate first recruiter account
python -m src.create_recruiter <username> <password>
```

### Migrations
Migrations are additive and run on startup in `database.py::_connection()`.
- New columns: `ALTER TABLE ... ADD COLUMN`
- New tables: `CREATE TABLE IF NOT EXISTS`
- **No rollback support** — backup before schema changes

## Debugging

### Enable Debug Logging
```python
# In code or environment
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: src` | Running from wrong directory | Run from repo root: `python -m src.main` |
| `ScoringModelUnavailableError` | Model not cached | `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"` |
| `sqlite3.OperationalError: database is locked` | Concurrent access | Use single worker, check for unclosed connections |
| `401 Unauthorized` | Session expired/missing | Login via `/api/v1/auth/session`, include cookie |
| `409 Conflict: Candidate not in opening` | Wrong job_id in request | Verify `candidate.opening_id == job_id` |

### Inspect Processing Jobs
```python
# Via API
GET /api/v1/jobs/{job_id}

# Via database
SELECT * FROM processing_jobs WHERE job_id = '...';
```

### Inspect Score Evidence
```python
# Via API (includes full breakdown)
POST /api/v1/candidates/score {candidate_id, job_id}

# Key evidence fields:
# - evidence.components.semantic_similarity.score
# - evidence.matching_required_skills
# - evidence.missing_required_skills
# - evidence.weights, evidence.breakdown
```

## Adding Dependencies

```powershell
# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Install in venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt

# Update lock file if using pip-tools
pip-compile requirements.txt -o requirements.lock.txt
```

## Code Style

- **Formatter:** Black (line length 88)
- **Linter:** Ruff or pyright
- **Type Checking:** pyright (strict)
- **Imports:** Absolute from `src.` or relative within package

```powershell
# Format
black src/ tests/

# Type check
pyright src/
```

## Git Workflow

```powershell
# Check status
git status

# Diff (no whitespace errors)
git diff --check

# Commit
git add -A
git commit -m "Descriptive message"

# Pre-push validation
python -m compileall -q src
python -m pytest tests/ -q
git diff --check
```

## Performance Profiling

```python
# In code
import cProfile, pstats
profiler = cProfile.Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(20)
```

Or use `py-spy` for sampling:
```powershell
pip install py-spy
py-spy record -o profile.svg -- python -m pytest tests/test_api.py::test_score_uses_saved_candidate_and_job_evidence -v
```

## Useful Commands Reference

| Task | Command |
|------|---------|
| Start server | `uvicorn src.main:app --reload` |
| Run all tests | `python -m pytest tests/ -v` |
| Run ATS tests | `python -m pytest tests/test_day16_day23.py -v` |
| Validate questions | `python -m src.validate_screening_dataset` |
| Create recruiter | `python -m src.create_recruiter user pass` |
| Reset recruiter | `python -m src.reset_recruiter user newpass` |
| Open SQLite | `sqlite3 data/zecpath.sqlite3` |
| Format code | `black src/ tests/` |
| Type check | `pyright src/` |
| Swagger UI | `http://localhost:8000/docs` |

## Related Documentation

- `docs/day16_ats_api_specification.md` — API reference
- `docs/day16_ats_integration_flow.md` — Data flows
- `docs/day21_eligibility_decision_engine.md` — Eligibility details
- `docs/day22_hr_screening_dataset.md` — Question bank
- `docs/day23_transcript_data_architecture.md` — Transcript storage