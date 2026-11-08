# Day 22 — HR screening question bank

The root question bank at `data/screening/hr_screening_questions.json` retains
the 17 available source questions with stable IDs, role/category metadata,
answer type, mandatory flag, order, version, follow-up flag, and translation
status. The validator is `python -m src.validate_screening_dataset`; the root
API filters by role, category, language, mandatory state, and active state.

Questions currently exist for Data Analyst (10) and Software Developer (7).
Thirteen roles are registered but the remaining eleven have no authored
questions. English text is available for all existing questions; Malayalam
and Hindi are available only for HR001 and HR006. Pending translations are
excluded rather than generated or mislabeled.

Questions are interview prompts, not validated assessment instruments.
