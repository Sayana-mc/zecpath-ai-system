# Day 22 — HR Screening Question Dataset Documentation

## Overview

The HR Screening Question Dataset provides a validated, standardized, and reusable bank of interview screening questions designed for initial conversational qualification before technical evaluation.

Data location: [`data/screening/hr_screening_questions.json`](file:///c:/Users/sayan/Documents/zecpath-ai-system/data/screening/hr_screening_questions.json)

---

## 1. Dataset Summary & Statistics

- **Total Questions:** 17
- **Role Coverage:**
  - `DATA_ANALYST`: 10 questions
  - `SOFTWARE_DEVELOPER`: 7 questions
- **Category Coverage:** 7 standardized categories
  1. `INTRODUCTION` (Personal elevator pitch and overview)
  2. `EDUCATION` (Highest academic qualification and relevance)
  3. `EXPERIENCE` (Years in industry, responsibilities, projects)
  4. `SKILLS` (Core technical tools, languages, and competencies)
  5. `LOCATION` (Current work location, commute, relocation)
  6. `SALARY` (Expected CTC / salary requirements)
  7. `NOTICE_PERIOD` (Availability timeline and joining window)
- **Mandatory vs. Optional Distribution:**
  - Mandatory questions: 12
  - Optional / conditional questions: 5
- **Scoring Importance Levels:**
  - `HIGH`: Skills, Experience
  - `MEDIUM`: Education, Notice Period
  - `LOW`: Introduction
  - `INFORMATIONAL`: Salary, Location (strictly non-penalizing)

---

## 2. Question Schema Structure

Each question is structured as a typed JSON object adhering to the Day 22 specification:

```json
{
  "question_id": "HR001",
  "role_id": "DATA_ANALYST",
  "category": "SKILLS",
  "question_text": "Which data visualization tools (such as Power BI or Tableau) have you used?",
  "expected_answer_type": "SKILL_LIST",
  "mandatory": true,
  "scoring_importance": "HIGH",
  "display_order": 1,
  "is_active": true,
  "version": 1,
  "translations": {
    "en": "Which data visualization tools (such as Power BI or Tableau) have you used?",
    "ml": null,
    "hi": null
  }
}
```

---

## 3. Multilingual Readiness

To prepare for future voice and multilingual screening without fabricating translations:
- The `translations` object contains keys for English (`en`), Malayalam (`ml`), and Hindi (`hi`).
- Non-English entries remain explicitly `null` until certified translations are recorded and validated.
- The API transparently falls back to `en` if a requested language is not yet translated.

---

## 4. API Endpoints

- `GET /api/v1/screening/questions`: Query questions by role, category, language, and mandatory status.
- Validated via `tests/test_day16_day23.py::test_screening_question_bank_filters_and_pending_translations`.

