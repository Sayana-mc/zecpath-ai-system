# Day 53–60 Hiring Intelligence Report Documentation — ZecPath AI Hiring System

## Overview

The Hiring Intelligence Report compiles all candidate evaluation data gathered across the five hiring stages (ATS Resume Screening, Voice Phone Screening, HR Structured Interview, Technical Depth Interview, and Machine Coding Test) into a single, cohesive, recruiter-friendly intelligence document.

---

## 1. Report Architecture & Data Sources

The report aggregates data across 11 key dimensions:
1. **Candidate Profile:** Candidate name, contact email, opening ID, target role title.
2. **Resume ATS Analysis:** Required skill matching percentage, keyword density, missing qualifications, and experience relevance.
3. **Pre-Screening Eligibility:** Binary and threshold eligibility verification (experience years, mandatory certifications, education requirements).
4. **Voice / Phone Screening:** Communication clarity, answer relevance, hesitation rate, and screening summary notes.
5. **HR Structured Interview:** Phase progression, situational judgment, cultural alignment, and consistency score.
6. **Technical Depth Assessment:** Conceptual depth classification (deep vs. moderate vs. shallow), technical topic coverage, and architectural reasoning.
7. **Machine Coding Test:** Automated unit test correctness, code quality score, algorithmic efficiency, and completion time.
8. **Behavioral Observations:** Candidate consent confirmation, observed workplace behaviors, and human review flags.
9. **Integrity Assessment:** Plagiarism indicators, identity verification checkpoints, and auxiliary anomaly alerts.
10. **Unified Cross-Round Fit Score:** Weighted percentage calculated across completed stages with dynamic re-weighting for missing stages.
11. **Final Recommendation:** Prescriptive decision (`SELECTED`, `HOLD_REVIEW`, `REJECTED`), evidence confidence score (0.00–1.00), and rationale bullet points.

---

## 2. Report Output Formats

### JSON Structured Payload
Machine-readable format accessible via API for programmatic consumption, ATS integrations, and frontend rendering. Contains explicit nested summaries for all evaluation rounds.

### Markdown (`.md`)
Clean, readable format suited for Git storage, text editors, and recruiter notes.

### Standalone HTML (`.html`)
Polished, production-ready document styled with clean modern CSS, responsive KPI cards, color-coded status badges, and printable layouts.

---

## 3. Versioning & Historical Tracking

Every time a Hiring Intelligence Report is generated for a candidate:
- If a prior report exists, the system retrieves the previous version number and increments it (e.g. `1.0` -> `1.1`).
- The new report is saved as an independent record in the `hiring_intelligence_reports` table.
- Recruiters can view the complete version history at `/api/v1/candidates/{id}/hiring-intelligence-report/history`.

---

## 4. Ethical & Human-in-the-Loop Safeguards

Every generated report, in all formats, includes the mandatory advisory notice:
> **Advisory Notice:** This report is advisory only. A qualified human reviewer must verify the underlying evidence before making any employment decision. Automated systems do not make final hiring or rejection choices.

