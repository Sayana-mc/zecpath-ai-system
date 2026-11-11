# Day 24–32 Live Screening Demonstration Guide

## 1. Prerequisites
- Python virtual environment activated (`.\.venv\Scripts\Activate.ps1`).
- Initialized recruiter account (or run `python -m src.auth create-first-recruiter --username recruiter --password <password>`).
- Start FastAPI server:
  ```powershell
  uvicorn src.main:app --host 127.0.0.1 --port 8000
  ```

## 2. Interactive Screening Demo via REST API

### Step 1: Create Opening & Candidate
```powershell
# 1. Login
$login = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/session" -Method Post -Body '{"username":"recruiter","password":"<password>"}' -ContentType "application/json" -SessionVariable sess

# 2. Create Job Opening
$opening = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/openings" -Method Post -WebSession $sess -Body '{"title":"Backend Python Engineer","description":"Python, FastAPI, SQL","required_skills":["Python","FastAPI","SQL"]}' -ContentType "application/json"

# 3. Create Candidate
$cand = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/candidates" -Method Post -WebSession $sess -Body (@{name="Alex Developer"; email="alex@example.test"; opening_id=$opening.opening_id; skills=@("Python","FastAPI")} | ConvertTo-Json) -ContentType "application/json"
```

### Step 2: Initialize Screening Session
```powershell
$session = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/screening/pipeline/sessions" -Method Post -WebSession $sess -Body (@{candidate_id=$cand.candidate_id; opening_id=$opening.opening_id} | ConvertTo-Json) -ContentType "application/json"
$sessionId = $session.session.session_id
```

### Step 3: Start Interview Flow
```powershell
$flow = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/screening/sessions/$sessionId/start" -Method Post -WebSession $sess
```

### Step 4: Submit Candidate Responses
```powershell
# Response to Question HR001
$ans = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/screening/sessions/$sessionId/answers/text" -Method Post -WebSession $sess -Body @{question_id="HR001"; answer_text="I have 5 years experience with Python and FastAPI building high scale APIs."}
```

### Step 5: Conclude Session and Review Final Report
```powershell
$summary = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/screening/sessions/$sessionId/complete" -Method Post -WebSession $sess
$report = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/screening/sessions/$sessionId/report" -Method Get -WebSession $sess
Write-Host "Overall Score:" $report.report_json.screening_score.total_score
```

