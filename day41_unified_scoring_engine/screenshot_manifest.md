# Day 41 – Unified Scoring Engine Screenshot Manifest

- **Day:** Day 41
- **Verification Date:** 2026-11-15
- **Execution Environment:** Live Running ZecPath Backend (`http://127.0.0.1:8000`)
- **Browser Used:** Chromium (Google Chrome via Playwright)

## SCREENSHOT VERIFICATION TABLE

| Screenshot | Feature | Capture source | Actual execution verified | Status |
|---|---|---|---|---|
| `01_candidate_ats_score.png` | Candidate profile showing existing ATS score | Swagger UI (`GET /candidates/{id}`) | Yes | **VERIFIED** |
| `02_screening_evaluation_score.png` | Screening evaluation score from screening pipeline | Swagger UI (`GET /candidates/{id}/screening-reports`) | Yes | **VERIFIED** |
| `03_hr_interview_score.png` | HR interview score and report retrieval | Swagger UI (`GET /hr-interviews/candidates/{id}/reports`) | Yes | **VERIFIED** |
| `04_cross_round_weight_config.png` | Cross-round weight configuration input (ATS:35%, Screening:25%, HR:40%) | Swagger UI (`POST /candidates/{id}/cross-round-evaluation`) | Yes | **VERIFIED** |
| `05_unified_score_calculation.png` | Unified cross-round score calculation execution | Swagger UI Execution Result | Yes | **VERIFIED** |
| `06_final_hiring_fit_percentage.png` | Final hiring-fit percentage calculation (84.45%) | Swagger UI JSON Response | Yes | **VERIFIED** |
| `07_component_score_breakdown.png` | Component-wise score breakdown with normalized weights | Swagger UI Response Table | Yes | **VERIFIED** |
| `08_unified_candidate_score_swagger.png` | Unified candidate score object retrieval | Swagger UI (`GET /candidates/{id}/cross-round-evaluation`) | Yes | **VERIFIED** |
| `09_missing_score_handling.png` | Missing-score handling with dynamic weight renormalization | Swagger UI Execution Result | Yes | **VERIFIED** |
