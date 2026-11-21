# ZecPath AI Hiring System – Final Internship Submission Package

## Package Structure
- `01_Project_Overview/` — Executive summary & portfolio index
- `02_System_Architecture/` — Architecture & workflow specifications
- `03_Technical_Documentation/` — Technical handbook & developer onboarding
- `04_API_Documentation/` — REST API & integration mapping
- `05_AI_Scoring_and_Models/` — ATS, cross-round, recommendation & optimization logic
- `06_Demo_Dataset/` — Synthetic candidate profiles, jobs & seeding guide
- `07_Test_Reports/` — Automated verification & edge-case test reports
- `08_Day_61_to_70_Reports/` — Daily reports for Days 61–70 (`day61`..`day70`) + Screenshot Evidence Register
- `09_Presentation/` — `day66_zecpath_demo_presentation.pptx` + `day66_demo_script.md`
- `10_Screenshots_and_Evidence/` — Verified browser, Swagger, PDF & terminal screenshots (`Day_61_Monitoring`..`Day_70_Final_Demo`)

## Quick Start (Local Development)
1. Seed demo data: `python scripts/seed_days51_55_demo_data.py`
2. Start FastAPI server: `python -m uvicorn src.main:app --host 127.0.0.1 --port 8000`
3. Open Recruiter UI: `http://127.0.0.1:8000` (`recruiter-d41-52` / `Password123!LongEnough`)
4. Open Swagger API Docs: `http://127.0.0.1:8000/docs`

## Known Limitations
- Candidate-facing Screening, HR Interview, Technical Interview, Machine Test, and Coaching portals are **API-only** (no candidate-facing browser UI).
- Machine test code evaluation uses static AST/test-case validation; **OS/container sandbox isolation is not implemented**.
- Synthetic validation metrics do not prove real-world hiring accuracy.
