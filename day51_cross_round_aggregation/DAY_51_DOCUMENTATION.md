# Day 51: Cross-Round Unified Aggregation & Scoring Engine

## 1. Objective
Aggregate candidate evaluation scores across all five hiring stages (`ats`, `screening`, `hr_interview`, `technical_interview`, `machine_test`) into a unified Hiring Fit Percentage using configurable role-specific weights, explicit stage statuses, minimum stage gates, anomaly detection, and duplicate evaluation prevention.

## 2. Architecture & Implementation
- **Engine:** `src/cross_round_scoring_engine.py` (`CrossRoundScoringEngine`)
- **Database Tables:** `role_weight_configurations`, `cross_round_evaluations` (extended with `score_version`, `stage_status_json`, `normalized_weights_json`, `calculation_status`, `recalculation_reason`, `version`, `tenant_id`, `input_fingerprint`)
- **API Endpoints (`src/api.py`):**
  - `GET /api/v1/role-weights` — List configured role weight profiles.
  - `PUT /api/v1/role-weights/{role_key}` — Validate (must sum to 100%) and persist role weights + `min_required_stages` (requires `configure_weights` permission).
  - `POST /api/v1/candidates/{candidate_id}/cross-round-evaluation` — Collect persisted stage scores, enforce `min_required_stages` gate, renormalize missing rounds, detect anomalies, prevent duplicates via SHA-256 `input_fingerprint`, and persist versioned evaluation.
  - `GET /api/v1/candidates/{candidate_id}/cross-round-evaluation` — List versioned evaluations for a candidate.
- **Recruiter UI (`static/index.html`):** Tab **Day 51: Cross-Round Evaluation** with candidate selector, stage-by-stage score & status cards (`COMPLETED`, `PENDING`, `NOT_STARTED`, `NOT_APPLICABLE`), role weight editor, anomaly viewer, and recalculation history.

## 3. Stage Status & Renormalization Rules
- Missing or `PENDING` stages are **never** treated as `0`.
- When completed stages < `min_required_stages`, `calculation_status` is set to `INSUFFICIENT_STAGES`.
- Otherwise, remaining stage weights are renormalized proportionally (`effective_weights`) so the unified score remains calibrated on a `0–100%` scale.

## 4. Verification & Evidence
- Standalone Unit Tests: `day51_cross_round_aggregation_engine/tests/test_day51.py` (12 passed).
- Integration Tests: `tests/test_day51_55_comprehensive.py::test_day51_role_weights_stage_status_gate_and_duplicate_prevention` (passed).
- Screenshots: `day51_cross_round_aggregation/screenshots/` (`01`–`09`).
