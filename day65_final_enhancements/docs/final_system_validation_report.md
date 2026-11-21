# Day 65 Final System Validation Report

## End-to-End Pipeline Execution (Live FastAPI Server)
- **Live E2E Candidate:** `Aarav Live Demo` (`e6c1c8d6-9ee2-4744-9034-55eef1bd03f1`)
  - `POST /api/v1/resumes/upload` (`resume_strong_python.txt`) -> `202 Accepted`
  - `POST /api/v1/ats/score` -> `200 OK`, **ATS Score: `83.17`**
  - `POST /api/v1/candidates/{id}/cross-round-evaluation` -> **`77.94%`**
  - `POST /api/v1/candidates/{id}/final-recommendation` -> **`HOLD_REVIEW`** (confidence **`82.5`**)
  - `POST /api/v1/final-recommendations/{id}/decision` -> **`APPROVED`**
  - `POST /api/v1/candidates/{id}/hiring-intelligence-report` -> `report_20a28b8f4031`

## 8 Day 63 Candidate Scenarios Evaluated (`day65_final_enhancements/output/day65_8_scenarios_pipeline_results.json`)
| Candidate | ATS Score | Cross-Round Score | Recommendation | Confidence | Human Review |
| :--- | :---: | :---: | :--- | :---: | :--- |
| Aarav Sharma | 100.0 | 73.6 | `HOLD_REVIEW` | 92.5 | `PENDING_REVIEW` |
| Pooja Hegde | 100.0 | 73.6 | `HOLD_REVIEW` | 92.5 | `PENDING_REVIEW` |
| Dr. Fatima Al-Mansoor | 100.0 | 73.6 | `HOLD_REVIEW` | 92.5 | `PENDING_REVIEW` |
| Meera Patel | 60.0 | 56.6 | `REJECTED` | 92.5 | `PENDING_REVIEW` |
| Dev Kapoor | 100.0 | 52.6 | `REJECTED` | 92.5 | `PENDING_REVIEW` |
| Vikram Sen | 100.0 | 52.6 | `REJECTED` | 92.5 | `PENDING_REVIEW` |
| Isha Iyer | 40.0 | 40.6 | `REJECTED` | 92.5 | `PENDING_REVIEW` |
| Rohan Verma | 0.0 | 32.6 | `REJECTED` | 92.5 | `PENDING_REVIEW` |

## Production-Readiness Decision
**Prototype / Demo-Ready (NOT Production-Ready):** Local pipeline, UI, governance, and 16 screenshots are verified; production requires PostgreSQL, container code sandboxing, external SSO/MFA, TLS, and real-world fairness validation.
