# Day 21 — Eligibility Decision Engine

## Overview

The Eligibility Decision Engine evaluates whether candidates qualify for further AI screening based on actual ATS results and recruiter-defined job rules. It is integrated into the root application at `src/eligibility.py` and exposed via authenticated API endpoints.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  ELIGIBILITY EVALUATION FLOW                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Recruiter                                                        │
│     │                                                            │
│     ▼                                                            │
│  PUT /openings/{id}/eligibility-config                          │
│     │                                                            │
│     ▼                                                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ eligibility_configurations table (versioned)             │    │
│  │ - minimum_ats_score                                       │    │
│  │ - mandatory_skills[]                                      │    │
│  │ - minimum/maximum_experience_years                        │    │
│  │ - location_rules {allowed_locations, work_mode,           │    │
│  │   remote_allowed, relocation_required, latest_start_date} │    │
│  │ - decision_policy {manual_review_on_missing_data}         │    │
│  └─────────────────────────────────────────────────────────┘    │
│     │                                                            │
│     ▼                                                            │
│  POST /candidates/{id}/eligibility/evaluate                     │
│     │                                                            │
│     ├── GET candidate (with score, resume_data, location...)    │
│     ├── GET opening (with requirements)                         │
│     ├── GET eligibility configuration                           │
│     │                                                            │
│     ▼                                                            │
│  evaluate_eligibility() [src/eligibility.py]                    │
│     │                                                            │
│     ├── Fingerprint: candidate_id, candidate.updated_at,       │
│     │           score, score_evidence, opening_id,             │
│     │           opening.updated_at, config.version              │
│     │                                                            │
│     ├── Rule: Minimum ATS Score                                 │
│     │   ├── No current score → REVIEW                          │
│     │   ├── Score < minimum → REJECTED (explicit)              │
│     │   └── Score ≥ minimum → PASS                             │
│     │                                                            │
│     ├── Rule: Mandatory Skills                                  │
│     │   ├── Candidate skills = profile ∪ resume extraction     │
│     │   ├── Missing skills → REVIEW (not proof of absence)     │
│     │   └── All matched → PASS                                 │
│     │                                                            │
│     ├── Rule: Experience Range                                  │
│     │   ├── No parsed experience → REVIEW                      │
│     │   ├── < minimum → REJECTED                               │
│     │   ├── > maximum → REVIEW                                 │
│     │   └── In range → PASS                                    │
│     │                                                            │
│     ├── Rule: Location / Work Mode                              │
│     │   ├── Checks allowed_locations, remote_allowed,          │
│     │   │   relocation_required, work_mode                     │
│     │   ├── Mismatch → REVIEW                                  │
│     │   └── Match → PASS                                       │
│     │                                                            │
│     ├── Rule: Availability                                      │
│     │   ├── latest_start_date configured                       │
│     │   ├── Candidate availability_date                        │
│     │   ├── Later than required → REVIEW                       │
│     │   └── On time → PASS                                     │
│     │                                                            │
│     ├── Decision Logic                                          │
│     │   ├── Any explicit failure (REJECTED rule) → REJECTED    │
│     │   ├── Any missing/uncertain → REVIEW                     │
│     │   └── All PASS → ELIGIBLE                                │
│     │                                                            │
│     ▼                                                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ eligibility_evaluations table                           │    │
│  │ - evaluation_id, candidate_id, opening_id               │    │
│  │ - configuration_version, input_fingerprint              │    │
│  │ - result_json, evaluated_at                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│     │                                                            │
│     ▼                                                            │
│  Response: ELIGIBLE | REVIEW | REJECTED                        │
│  human_review_required: true                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Decision Logic

### Three Output States

| Status | Meaning | When |
|--------|---------|------|
| **ELIGIBLE** | All configured rules passed with available evidence | No explicit failures, no missing/uncertain data |
| **REVIEW** | Evidence missing, uncertain, or requires human judgment | Mandatory skills missing, no score, location mismatch, availability unknown, experience > max |
| **REJECTED** | Explicit, configured job-related threshold not met | ATS score < minimum, experience < minimum |

### Key Principles

1. **Missing evidence ≠ negative evidence** — Missing mandatory skill routes to REVIEW, not REJECTED
2. **No current ATS score → REVIEW** — Cannot evaluate without recent score
3. **Explicit failures only for configured thresholds** — Only `minimum_ats_score` and `minimum_experience_years` can cause REJECTED
4. **Human review always required** — Every response includes `human_review_required: true`
5. **No application status mutation** — Eligibility is decision support only

## Configuration Schema

```json
{
  "minimum_ats_score": 65,
  "mandatory_skills": ["Python", "SQL"],
  "minimum_experience_years": 1,
  "maximum_experience_years": 5,
  "location_rules": {
    "allowed_locations": ["Bangalore", "Remote"],
    "work_mode": "HYBRID",
    "remote_allowed": true,
    "relocation_required": false,
    "latest_start_date": "2026-06-01"
  },
  "decision_policy": {
    "manual_review_on_missing_data": true
  }
}
```

### Field Details

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `minimum_ats_score` | float (0-100) | No | Minimum ATS score threshold |
| `mandatory_skills` | string[] | No | Required skills (case-insensitive, normalized) |
| `minimum_experience_years` | float (0-80) | No | Minimum years of experience |
| `maximum_experience_years` | float (0-80) | No | Maximum years (exceeds → REVIEW) |
| `location_rules.allowed_locations` | string[] | No | Accepted candidate locations |
| `location_rules.work_mode` | ONSITE/HYBRID/REMOTE | No | Required work mode |
| `location_rules.remote_allowed` | boolean | No | Allow remote exception |
| `location_rules.relocation_required` | boolean | No | Require relocation willingness |
| `location_rules.latest_start_date` | YYYY-MM-DD | No | Latest acceptable start date |
| `decision_policy.manual_review_on_missing_data` | boolean | No | Default: true |

## API Endpoints

### Save Configuration
```
PUT /api/v1/openings/{opening_id}/eligibility-config
Content-Type: application/json
{configuration}
```
**Response (200):** `EligibilityConfigurationResponse` with version

### Get Configuration
```
GET /api/v1/openings/{opening_id}/eligibility-config
```
**Response (200):** `EligibilityConfigurationResponse`

### Evaluate Candidate
```
POST /api/v1/candidates/{candidate_id}/eligibility/evaluate
Content-Type: application/json
{"opening_id": "uuid"}
```
**Response (201):** `EligibilityEvaluationResponse`

### Get Latest Evaluation
```
GET /api/v1/candidates/{candidate_id}/eligibility?opening_id=uuid
```
**Response (200):** `EligibilityEvaluationResponse` (re-evaluates if fingerprint changed)

## Response Structure

```json
{
  "evaluation_id": "uuid",
  "candidate_id": "uuid",
  "opening_id": "uuid",
  "status": "ELIGIBLE|REVIEW|REJECTED",
  "ats_score": 78.5,
  "rules": {
    "minimum_ats_score": {
      "status": "PASS|FAIL|REVIEW|NOT_CONFIGURED",
      "reason": "...",
      "value": 78.5,
      "required": 65
    },
    "mandatory_skills": {
      "status": "PASS|REVIEW",
      "reason": "...",
      "matched": ["Python", "SQL"],
      "missing": [],
      "evidence_sources": {"Python": "candidate_reported", "SQL": "resume_extraction"}
    },
    "experience": {
      "status": "PASS|FAIL|REVIEW|NOT_CONFIGURED",
      "reason": "...",
      "years": 3.0,
      "minimum_years": 1,
      "maximum_years": 5
    },
    "location": {
      "status": "PASS|REVIEW|NOT_CONFIGURED",
      "reason": "...",
      "candidate_location": "Bangalore",
      "candidate_preference": "HYBRID"
    },
    "availability": {
      "status": "PASS|REVIEW|NOT_CONFIGURED",
      "reason": "...",
      "availability_date": "2026-02-01",
      "latest_start_date": "2026-06-01"
    }
  },
  "mandatory_skills_matched": ["Python", "SQL"],
  "mandatory_skills_missing": [],
  "experience_result": {...},
  "location_result": {...},
  "availability_result": {...},
  "missing_information": ["A current ATS score is unavailable."],
  "review_reasons": ["Mandatory-skill evidence requires recruiter review."],
  "decision_explanation": "Evidence is missing, uncertain, or requires recruiter judgment; no employment decision is made automatically.",
  "configuration_version": 1,
  "evaluated_at": "2026-01-01T00:00:00+00:00",
  "human_review_required": true
}
```

## Fingerprint Re-evaluation

The system automatically re-evaluates when relevant inputs change:

**Fingerprint includes:**
- `candidate_id`
- `candidate.updated_at`
- `candidate.score`
- `candidate.score_evidence` (including `scored_at`)
- `opening_id`
- `opening.updated_at`
- `configuration.version`

**Triggers re-evaluation:**
- Resume upload/replace (updates candidate, clears score)
- Candidate skills/name/location change
- Opening requirements change
- New ATS score calculated
- Eligibility configuration updated

**GET `/eligibility` behavior:**
```python
latest = get_latest_eligibility_evaluation(candidate_id, opening_id)
if latest is None or latest.fingerprint != current_fingerprint:
    return _evaluate_and_persist_eligibility(candidate, opening, configuration)
return latest
```

## Skill Matching Details

### Canonicalization
Skills are normalized via `day9_skill_extraction.src.skill_normalizer.normalize_skill_name()`:
- Case-insensitive comparison
- Synonym mapping (e.g., "PySpark" → "Spark")
- Whitespace stripping

### Evidence Sources
Matched skills tagged with source:
- `candidate_reported` — From `candidate.skills` (application form)
- `resume_extraction` — From `resume_data.skills` (parsed resume)

Both sources are unioned for matching; source recorded per skill.

## Experience Handling

- Source: `resume_data.experience_years` (parsed from resume)
- If not a number → REVIEW (missing/uncertain)
- Minimum failure → REJECTED
- Maximum exceeded → REVIEW (not automatic rejection)
- No overlap detection — relies on parser accuracy

## Location/Work Mode Logic

```
IF allowed_locations configured AND NOT remote_exception:
    IF no candidate_location: REVIEW
    ELSE IF location not in allowed:
        IF relocation_required AND relocation_willingness == True: PASS
        ELSE IF relocation_required AND relocation_willingness == None: REVIEW
        ELSE: REVIEW
    ELSE: PASS

IF work_mode configured:
    IF candidate_mode matches OR (candidate_mode == REMOTE AND remote_allowed): PASS
    ELSE: REVIEW

ELSE: NOT_CONFIGURED
```

## Availability Logic

```
IF latest_start_date configured:
    IF no availability_date: REVIEW
    ELSE IF availability_date > latest_start_date: REVIEW
    ELSE: PASS
ELSE: NOT_CONFIGURED
```

## Database Schema

### eligibility_configurations
```sql
CREATE TABLE eligibility_configurations (
    opening_id TEXT PRIMARY KEY REFERENCES openings(opening_id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    configuration_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### eligibility_evaluations
```sql
CREATE TABLE eligibility_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    opening_id TEXT NOT NULL REFERENCES openings(opening_id) ON DELETE CASCADE,
    configuration_version INTEGER NOT NULL,
    input_fingerprint TEXT NOT NULL,
    result_json TEXT NOT NULL,
    evaluated_at TEXT NOT NULL
);
CREATE INDEX eligibility_latest_idx ON eligibility_evaluations(candidate_id, opening_id, evaluated_at);
```

## Testing

### Key Test Scenarios (`tests/test_day16_day23.py`)

```python
# 1. Uses current ATS score, re-evaluates after change
test_eligibility_uses_current_ats_score_and_re_evaluates_after_change

# 2. Rejects only explicit threshold failure, checks ownership
test_eligibility_rejects_only_explicit_failed_threshold_and_checks_ownership

# 3. Configuration validation, authentication required
test_eligibility_configuration_validation_and_authentication
```

### Test Coverage
- ✅ High ATS score + matching skills → ELIGIBLE
- ✅ Low ATS score (< minimum) → REJECTED
- ✅ Missing mandatory skills → REVIEW
- ✅ No ATS score → REVIEW
- ✅ Experience below minimum → REJECTED
- ✅ Experience above maximum → REVIEW
- ✅ Location mismatch → REVIEW
- ✅ Remote allowed exception → PASS
- ✅ Relocation willingness → PASS/REVIEW
- ✅ Availability after latest_start_date → REVIEW
- ✅ Invalid config (min > max exp) → 422
- ✅ Cross-job evaluation → 409
- ✅ Fingerprint re-evaluation on candidate change
- ✅ Authentication required

## Integration Points

| Component | Integration |
|-----------|-------------|
| ATS Scoring | Uses `candidate.score` + `score_evidence.scored_at` |
| Resume Parsing | Uses `resume_data.skills`, `experience_years` |
| Candidate Profile | Uses `candidate.skills`, `location`, `relocation_willingness`, `work_mode_preference`, `availability_date` |
| Job Opening | Uses `opening.required_skills`, `minimum_years_experience` |
| Auth | Requires recruiter session, validates ownership |

## Limitations

1. **No tenant isolation** — Single recruiter, all data visible
2. **Parser-dependent** — Experience/skills from resume parser accuracy
3. **No learning** — Rules static, no ML-based threshold optimization
4. **Binary experience** — No relevant vs total experience distinction
5. **Location matching** — Exact string match (case-insensitive), no geo-distance
6. **Availability** — Self-reported only, no verification

## Future Enhancements

- Soft skill requirements
- Certification/license validation
- Market salary range checks
- Background check integration
- Historical hiring outcome feedback loop
- Configurable rule weights (not just pass/fail)