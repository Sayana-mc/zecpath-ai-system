# Day 39: Recruiter Interview Summary Generator & Dossier

## 1. Overview
The Summary Generator condenses multi-turn conversational answers, behavioral observations, communication scores, and aptitude evaluations into an 11-section executive dossier for hiring recruiters.

---

## 2. The 11 Canonical Report Sections

1. **Interview Details:** Session metadata, timestamp, opening ID, title, and candidate identifiers.
2. **Candidate Summary:** High-level candidate profile, skills, experience level, and track.
3. **Performance Breakdown:** Weighted composite score (0–100), sub-scores (relevance, communication, confidence, consistency).
4. **Identified Strengths:** Bulleted summary of demonstrated proficiencies and behavioral highlights.
5. **Areas for Improvement:** Constructive observations where answers lacked depth or required clarification.
6. **Teamwork & Culture:** Observations regarding collaboration style, stakeholder interaction, and workplace fit.
7. **Career Alignment & Goals:** Candidate aspirations, self-directed learning trajectory, and 2-to-3-year objectives.
8. **Availability & Commitments:** Stated notice period, immediate availability, and role commitment.
9. **Aptitude & Situational Judgment:** Multi-dimensional scores on logical reasoning and scenario dilemmas.
10. **Review Flags & Contradictions:** Algorithmic flags highlighting factual contradictions or high uncertainty.
11. **Recruiter Review & Decision:** Suggested recommendation (`PROCEED_TO_FINAL_ROUND`, `MANUAL_RECRUITER_REVIEW`, `HOLD_OR_REJECT`) and final recruiter decision input field.

---

## 3. Dual Export Capabilities
- **Structured JSON (`GET /api/v1/hr-interviews/{id}/report`):** Full machine-readable schema for downstream HRIS and ATS integrations.
- **Print-Ready HTML (`GET /api/v1/hr-interviews/{id}/report?format=html`):** Standalone styled dossier ready for PDF export or browser preview.

