# Day 63: Demo Dataset Creation & Seeding — ZecPath AI Hiring System

## Executive Summary

Day 63 delivers a comprehensive, repeatable synthetic demo dataset and an automated seeding pipeline (`src/init_demo_data.py`). The dataset is structured under `demo_data/` and provides realistic recruitment scenarios without using any real personal candidate information.

---

## 1. Directory Structure

```
demo_data/
├── jobs/
│   ├── job_python_developer.json      # Senior Python Backend Architect
│   ├── job_data_analyst.json          # Lead Data Analyst
│   ├── job_software_developer.json    # Full Stack Software Developer
│   └── job_ml_engineer.json           # Senior Machine Learning Engineer
├── candidates/
│   └── candidates.json                # 8 candidate profiles across diverse archetypes
├── resumes/
│   ├── resume_strong_python.txt
│   ├── resume_partial_python.txt
│   ├── resume_low_match.txt
│   ├── resume_high_skills_low_exp.txt
│   ├── resume_missing_mandatory_skills.txt
│   ├── resume_formatting_edge_case.txt
│   ├── resume_data_analyst_strong.txt
│   └── resume_ml_engineer_strong.txt
└── interviews/
    └── screening_and_interview_responses.json
```

---

## 2. Job Openings Breakdown

1. **Senior Python Backend Architect (`job_python_developer.json`):**
   - Required Skills: Python, FastAPI, PostgreSQL, Docker, REST API
   - Preferred Skills: Kubernetes, Redis, Celery, AWS, CI/CD
   - Experience: 5+ years, Bachelor's degree minimum, Hybrid work mode.
2. **Lead Data Analyst (`job_data_analyst.json`):**
   - Required Skills: SQL, Python, Tableau, Data Modeling, Excel
   - Experience: 4+ years, Remote allowed.
3. **Full Stack Software Developer (`job_software_developer.json`):**
   - Required Skills: JavaScript, TypeScript, React, Python, SQL
   - Experience: 3+ years, Onsite.
4. **Senior Machine Learning Engineer (`job_ml_engineer.json`):**
   - Required Skills: Python, PyTorch, Machine Learning, NLP, Docker
   - Experience: 4+ years, Hybrid.

---

## 3. Candidate Archetypes & Seeded Results

| Candidate Name | Target Role | Archetype | Fit Score | AI Recommendation |
|---|---|---|---|---|
| **Aarav Sharma** | Senior Python Architect | Strong Match | 92.0% | `SELECTED` |
| **Meera Patel** | Senior Python Architect | Partial Match (lacks Docker/FastAPI) | 72.0% | `HOLD_REVIEW` |
| **Rohan Verma** | Senior Python Architect | Low Match (PHP/CMS background) | 44.0% | `REJECTED` |
| **Dev Kapoor** | Senior Python Architect | High Skills, Low Experience (1.5 yrs) | 64.0% | `REJECTED` |
| **Isha Iyer** | Senior Python Architect | Missing Mandatory Skills (Java/Spring) | 52.0% | `REJECTED` |
| **Vikram Sen** | Senior Python Architect | Formatting Edge Case (noisy text) | 64.0% | `REJECTED` |
| **Pooja Hegde** | Lead Data Analyst | Strong Match (Data Analytics) | 92.0% | `SELECTED` |
| **Dr. Fatima Al-Mansoor** | Senior ML Engineer | Strong Match (ML & PyTorch) | 92.0% | `SELECTED` |

---

## 4. How to Run the Seeding Script

```powershell
# Seed the default live database
.\.venv\Scripts\python.exe -m src.init_demo_data

# Seed a custom local demo database
.\.venv\Scripts\python.exe -m src.init_demo_data --target-db data/live_demo.sqlite3
```

The script performs real application steps:
1. Creates openings.
2. Registers candidates.
3. Parses resume files with `extract_resume_data`.
4. Calculates weighted ATS scores with `calculate_candidate_match`.
5. Evaluates pre-screening eligibility.
6. Simulates screening sessions, technical interviews, and machine coding tests.
7. Calculates unified cross-round hiring fit percentages.
8. Generates explainable recommendations.
9. Compiles complete 15-section Hiring Intelligence Reports with HTML/Markdown export.
10. Generates Candidate AI Coaching records.
11. Writes all actions to the cryptographic audit trail.

