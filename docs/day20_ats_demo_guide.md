# Day 20 — ATS Demo Guide

## Prerequisites

```powershell
# 1. Activate virtual environment
. .venv/Scripts/Activate.ps1

# 2. Ensure model is cached (first run downloads ~90MB)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 3. Start server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Demo Data

All demo data is **synthetic**. No real candidate information is used.

### Demo Job Description

```
Required skills: Python, SQL
Preferred skills: Tableau, Power BI
Experience: 2+ years
Education: Bachelor's degree in Computer Science, Statistics, or related field
Responsibilities:
- Build and maintain data pipelines
- Create dashboards and reports
- Collaborate with stakeholders on analytics needs
```

### Demo Resume (TXT)

```
Synthetic Candidate
Email: candidate@example.com
Location: Bangalore
Relocation Willingness: Yes
Work Mode Preference: HYBRID
Availability Date: 2026-02-01

SKILLS
Python, SQL, Tableau, Pandas, NumPy, Power BI, Excel

EXPERIENCE
Data Analyst at Synthetic Corp (2021-2024)
- Built ETL pipelines using Python and SQL
- Created Tableau dashboards for executive reporting
- Analyzed customer behavior data

Junior Analyst at Demo Inc (2019-2021)
- SQL query optimization
- Weekly report automation

EDUCATION
Bachelor of Science in Computer Science (2019)
University of Synthetic Example

CERTIFICATIONS
Tableau Desktop Specialist (2022)
```

## Demo Workflow

### 1. Login

```bash
# Via Swagger UI: http://localhost:8000/docs
POST /api/v1/auth/session
{
  "username": "your-username",
  "password": "your-password"
}
# Sets cookie: zecpath_session
```

### 2. Parse Job Description

```bash
POST /api/v1/openings/parse-description
{
  "description": "Required skills: Python, SQL\nPreferred skills: Tableau\nExperience: 2+ years\nEducation: Bachelor's degree"
}

# Response shows extracted requirements + evidence + warnings
# human_confirmation_required: true
```

### 3. Create Job Opening

```bash
POST /api/v1/openings
{
  "title": "Data Analyst",
  "description": "Analyze synthetic business data...",
  "required_skills": ["Python", "SQL"],
  "preferred_skills": ["Tableau", "Power BI"],
  "minimum_education": "Bachelor's degree",
  "minimum_years_experience": 2.0
}
# → opening_id
```

### 4. Create Candidate Application

```bash
POST /api/v1/candidates
{
  "name": "Synthetic Candidate",
  "email": "candidate@example.com",
  "opening_id": "<opening_id>",
  "skills": ["Python", "SQL", "Tableau"],
  "location": "Bangalore",
  "relocation_willingness": true,
  "work_mode_preference": "HYBRID",
  "availability_date": "2026-02-01"
}
# → candidate_id
```

### 5. Upload Resume

```bash
# Multipart form upload
POST /api/v1/resumes/upload
file: synthetic_resume.txt
candidate_id: <candidate_id>

# Response: job_id, status: QUEUED
```

### 6. Wait for Processing

```bash
GET /api/v1/jobs/<job_id>
# Poll until status: COMPLETED
```

### 7. View Parsed Resume

```bash
POST /api/v1/resumes/parse
{
  "job_id": "<job_id>"
}
# Returns: parsed_text, extracted_data (skills, experience, education)
```

### 8. Calculate ATS Score

```bash
POST /api/v1/candidates/score
{
  "job_id": "<opening_id>",
  "candidate_id": "<candidate_id>"
}
# Returns: score (0-100), evidence breakdown, ranking, human_review_required
```

### 9. Generate Shortlist

```bash
POST /api/v1/openings/<opening_id>/shortlist
{
  "minimum_score": 60.0
}
# Returns: ranked candidates from saved scores
```

### 10. Configure Eligibility Rules

```bash
PUT /api/v1/openings/<opening_id>/eligibility-config
{
  "minimum_ats_score": 65,
  "mandatory_skills": ["Python", "SQL"],
  "minimum_experience_years": 1,
  "maximum_experience_years": 5,
  "location_rules": {
    "allowed_locations": ["Bangalore", "Remote"],
    "remote_allowed": true,
    "relocation_required": false
  },
  "decision_policy": {"manual_review_on_missing_data": true}
}
```

### 11. Evaluate Eligibility

```bash
POST /api/v1/candidates/<candidate_id>/eligibility/evaluate
{
  "opening_id": "<opening_id>"
}
# Returns: ELIGIBLE/REVIEW/REJECTED with detailed rule results
```

### 12. Get Screening Questions

```bash
GET /api/v1/screening/questions?role_id=DATA_ANALYST&language=en
# Returns: 10 questions for Data Analyst
```

### 13. Create Screening Session

```bash
POST /api/v1/screening/sessions
{
  "candidate_id": "<candidate_id>",
  "opening_id": "<opening_id>",
  "language": "en",
  "source": "MANUAL"
}
# → session_id
```

### 14. Add Transcript Segments

```bash
PATCH /api/v1/screening/sessions/<session_id>
{"status": "IN_PROGRESS"}

POST /api/v1/screening/sessions/<session_id>/segments
[
  {
    "segment_id": "SEG-1",
    "question_id": "HR001",
    "speaker": "RECRUITER",
    "text": "Please introduce yourself.",
    "sequence_number": 1
  },
  {
    "segment_id": "SEG-2",
    "question_id": "HR001",
    "speaker": "CANDIDATE",
    "text": "I am a data analyst with 3 years experience.",
    "sequence_number": 2
  }
]
```

### 15. Add Screening Interaction

```bash
POST /api/v1/screening/sessions/<session_id>/interactions
{
  "question_id": "HR001",
  "candidate_answer": "I am a data analyst with 3 years experience.",
  "validation_status": "VALID",
  "display_order": 1
}
```

### 16. Complete Session & View Transcript

```bash
PATCH /api/v1/screening/sessions/<session_id>
{"status": "COMPLETED"}

GET /api/v1/screening/sessions/<session_id>
# Returns: session, segments[], interactions[]
```

## Dashboard Demo

Open `http://localhost:8000/` in browser.

Features:
- Login form (uses same session cookie)
- Job openings list with create/edit/delete
- Candidates list with status filters
- Resume upload with progress
- Score display with evidence breakdown
- Eligibility configuration panel
- Screening questions browser
- Transcript viewer

## Expected Outputs

| Step | Success Indicator |
|------|-------------------|
| Login | Cookie set, `authenticated: true` |
| JD Parse | `required_skills: ["Python", "SQL"]`, `human_confirmation_required: true` |
| Upload | `status: QUEUED`, `job_id` returned |
| Processing | `status: COMPLETED`, `result.parsed_text` contains resume content |
| Scoring | `score: 0-100`, `evidence.components` present, `ranking` assigned |
| Shortlist | `candidates[]` with ranks, `human_review_required: true` |
| Eligibility | `status: ELIGIBLE/REVIEW/REJECTED`, `rules` detail, `human_review_required: true` |
| Questions | 10 questions for DATA_ANALYST, translations available |
| Transcript | Segments stored with `normalized_text`, interactions linked |

## Troubleshooting Demo Issues

| Issue | Fix |
|-------|-----|
| 503 on scoring | Model not cached: run `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"` |
| 409 on score | Candidate not linked to job: verify `candidate.opening_id == job_id` |
| 409 on eligibility | No config: PUT eligibility-config first |
| 422 on transcript | Sequence gap: ensure sequence_number starts at 1, increments by 1 |
| Questions empty for ml/hi | Only HR001, HR006 have translations; others PENDING |

## Cleanup

```bash
# Stop server: Ctrl+C
# Database persists in data/zecpath.sqlite3
# Uploads in uploads/ (auto-cleaned on processing)
```