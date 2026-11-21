# ZecPath AI Hiring System — Stakeholder Q&A (Day 67)

1. **Why is ZecPath needed?**
   Traditional ATS and interview workflows fragment evidence across disconnected tools and often penalize uncompleted rounds as zero. ZecPath unifies all stages with transparent rubrics, missing-stage renormalization, and mandatory human sign-off.
2. **How does ATS scoring work?**
   4-factor weighted formula in `src/ats_scoring_engine.py`: `0.40 * Skills + 0.25 * Semantic + 0.20 * Experience + 0.15 * Education`, returning matched evidence snippets.
3. **How are required skills matched?**
   Whole-word boundary matching combined with normalized skill extraction (`day9_skill_extraction` / `src/resume_analysis.py`) to avoid false substring matches (e.g. `C` vs `CSS`).
4. **How is eligibility determined?**
   `src/eligibility.py` checks opening-specific mandatory requirements (required skills, minimum experience, education) and outputs `ELIGIBLE`, `REVIEW_REQUIRED`, or `REJECTED` without auto-deleting applications.
5. **How are interview scores calculated?**
   - **Screening:** 4-factor rubric (Clarity, Relevance, Completeness, Consistency).
   - **HR Interview:** Communication fluency, filler/hesitation analysis, and aptitude scoring.
   - **Technical Interview:** 5-dimension rubric + depth classification (`shallow`, `moderate`, `deep`).
6. **How does cross-round aggregation work?**
   `src/cross_round_scoring_engine.py` combines available stages using configurable `role_weight_configurations` and applies `exclude_and_renormalize` for missing rounds so candidates are never silently penalized with zero.
7. **How are final recommendations generated?**
   `src/final_recommendation_engine.py` classifies `SELECTED`, `HOLD_REVIEW`, or `REJECTED` via role thresholds, enforces a mandatory eligibility override (`ELIGIBILITY REJECTED` overrides high scores), and computes confidence (`50%` coverage + `30%` evidence quality + `20%` consistency).
8. **How are false positives and false negatives handled?**
   Cross-round anomaly detection flags divergent round scores, missing info triggers `HOLD_REVIEW`, and recruiters can `OVERRIDE` any AI recommendation with an audited rationale.
9. **How is human review maintained?**
   Every recommendation starts in human-review workflow; final decisions (`APPROVE`, `OVERRIDE`, `REJECT`) require an authenticated recruiter action logged to `recommendation_decision_history`.
10. **How is candidate data protected?**
    PBKDF2-SHA256 authentication, HTTP-only session cookies, 4 RBAC roles, tenant isolation (`403`), consent tracking, 180-day retention policies, anonymization, and SHA-256 hash-chained `audit_events`.
11. **What is genuinely AI-powered vs. rule-based?**
    - **Local ML/NLP:** Sentence-embedding semantic similarity in ATS scoring (with deterministic fallback).
    - **Rule-Based / Deterministic:** Eligibility checks, whole-word skill matching, cross-round weighted renormalization, threshold classification, AST-based machine-test checks, and Day 54 grid search.
    - **Supplied Reviewer Inputs:** Recruiter `APPROVE` / `OVERRIDE` / `REJECT` decisions and rubric inputs.
    - **Synthetic Data:** Day 63 dataset (`demo_data/`) and Day 54 12-case benchmark.
12. **What limitations remain & what is required for production?**
    Single-node SQLite, AST-only machine test (no OS container sandbox), API-only interview/test stages (no candidate portal UI), and synthetic-only validation. Production requires PostgreSQL pooling, micro-VM code execution, external SSO/MFA, TLS, and real-world fairness auditing.
