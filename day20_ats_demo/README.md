# Day 20 ATS Demo Assets

This directory contains standalone synthetic evaluation and demonstration data for the ZecPath ATS subsystem:

- `demo_job.json`: Synthetic job opening requirements (Senior Python Developer).
- `demo_candidates.json`: 3 synthetic candidate resumes with varying levels of match (Strong Match, Partial Match, Mismatch).
- `run_demo.py`: Automated Python script executing the live demonstration flow:
  1. Recruiter authentication.
  2. Job opening registration.
  3. Candidate profile registration and resume text ingestion.
  4. Real ATS semantic and weighted scoring calculation.
  5. Candidate ranking.
  6. Shortlist generation.

### Running the Demo
```powershell
.\.venv\Scripts\python.exe day20_ats_demo/run_demo.py
```

