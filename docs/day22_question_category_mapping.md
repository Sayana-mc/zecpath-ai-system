# Day 22 — Question Category Mapping Specification

## Purpose

The Question Category Mapping establishes a normalized schema that maps high-level HR screening categories to evaluation intents, expected answer types, and follow-up rules.

Data location: [`data/screening/question_category_mapping.json`](file:///c:/Users/sayan/Documents/zecpath-ai-system/data/screening/question_category_mapping.json)

---

## 1. Category Definitions & Rules

| Category | Identifier | Expected Answer Type | Evaluation Intent | Default Importance |
|---|---|---|---|---|
| Introduction | `INTRODUCTION` | `TEXT` | Communication clarity, self-summary | LOW |
| Education | `EDUCATION` | `TEXT` / `SINGLE_CHOICE` | Highest degree verification | MEDIUM |
| Experience | `EXPERIENCE` | `DURATION` / `TEXT` | Total and relevant tenure | HIGH |
| Skills | `SKILLS` | `SKILL_LIST` | Technical stack proficiency | HIGH |
| Location | `LOCATION` | `LOCATION` | Work authorization & commute | INFORMATIONAL |
| Salary | `SALARY` | `CURRENCY` | Compensation expectation | INFORMATIONAL |
| Notice Period | `NOTICE_PERIOD` | `NOTICE_PERIOD` | Days to joining | MEDIUM |

---

## 2. Guardrails

1. **Non-Penalizing Protected Categories**: Personal expectations (Salary, Location) are flagged as `INFORMATIONAL`. They cannot be used as negative scoring factors.
2. **Deterministic Validation**: Answer types specify expected validation regexes or numeric ranges (e.g. `NOTICE_PERIOD` parses days/months; `DURATION` parses years of experience).

