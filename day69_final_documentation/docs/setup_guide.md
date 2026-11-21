# ZecPath Setup Guide

## Prerequisites
- Python 3.12+
- Virtual environment (`.venv` or system Python with `requirements.txt` installed)

## Installation & Database Initialization
```powershell
pip install -r requirements.txt
python -m src.create_recruiter
python -m src.init_demo_data
```

## Starting the Application
```powershell
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```
Open:
- Recruiter Workspace UI: `http://127.0.0.1:8000/`
- Swagger API Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/v1/health`

## Running Automated Tests
```powershell
python -m pytest day61_ai_monitoring_observability/tests/ day63_demo_dataset_creation/tests/ day64_internal_review/tests/ day65_final_enhancements_feature_polish/tests/ tests/test_ats_scoring_engine.py tests/test_schemas.py tests/test_fairness.py -v
```
