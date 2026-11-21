# ZecPath Architecture & Honest AI Module Classification (Day 70)

## Module-by-Module Processing Classification

| Module | Processing Type | Honest Technical Explanation |
| :--- | :--- | :--- |
| `src/resume_analysis.py` | Traditional Programmatic + Rule-Based | Parses TXT/DOCX/PDF text, segments sections, and extracts skills/education/experience using regex and keyword dictionaries. |
| `src/ats_scoring_engine.py` | Local NLP Embeddings + Rule-Based | Uses local sentence-embedding similarity (25% weight) alongside deterministic skill (40%), experience (20%), and education (15%) rubrics. |
| `src/eligibility.py` | Rule-Based Logic | Checks mandatory skills, minimum experience, and education against opening rules (`ELIGIBLE`/`REVIEW_REQUIRED`/`REJECTED`). |
| `src/screening_pipeline.py` | Rule-Based + Programmatic | Evaluates clarity, relevance, completeness, and consistency with deterministic scoring and transcript cleaning. |
| `src/hr_interview_pipeline.py` | Rule-Based + Programmatic | Selects role/experience questions, triggers follow-ups, and scores filler words, pacing, and aptitude deterministically. |
| `src/technical_interview_engine.py` | Rule-Based Logic | Scores technical responses on a 5-dimension rubric and classifies depth (`shallow`, `moderate`, `deep`). |
| `src/machine_test_engine.py` | Traditional Programmatic (AST) | Analyzes submitted code via Python `ast` and static rubric heuristics; does **not** execute code in an OS/container sandbox. |
| `src/behavioral_ai_engine.py` & `src/integrity_engine.py` | Rule-Based Safeguards | Computes non-punitive consistency and environment review flags; never auto-rejects candidates. |
| `src/cross_round_scoring_engine.py` | Deterministic Math | Applies configurable role weights with `exclude_and_renormalize` for missing stages and SHA-256 `input_fingerprint`. |
| `src/final_recommendation_engine.py` | Rule-Based + Human Input | Classifies `SELECTED`/`HOLD_REVIEW`/`REJECTED` with eligibility override; requires recruiter `APPROVED`/`OVERRIDDEN`/`REJECTED` input. |
| `src/hiring_intelligence_report_generator.py` | Traditional Programmatic | Compiles persisted DB records into a 14-section report in JSON, HTML, Markdown, and PDF 1.4. |
| `src/init_demo_data.py` & `demo_data/` | Synthetic Demonstration Data | 4 synthetic job descriptions, 8 synthetic candidate profiles, and 8 synthetic resumes for local evaluation. |
