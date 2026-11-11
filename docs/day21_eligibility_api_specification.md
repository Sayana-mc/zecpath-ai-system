# Day 21 — Eligibility API Specification

## Base URL

All endpoints: `/api/v1`

Authentication: Required (recruiter session cookie)

---

## Endpoints

### 1. Save Eligibility Configuration

**PUT** `/openings/{opening_id}/eligibility-config`

Saves or updates eligibility rules for a job opening. Increments version.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `opening_id` | string | Yes | Job opening UUID |

#### Request Body
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

#### Success Response (200)
```json
{
  "opening_id": "uuid",
  "version": 1,
  "configuration": {
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
  },
  "created_at": "2026-01-01T00:00:00+00:00",
  "updated_at": "2026-01-01T00:00:00+00:00"
}
```

#### Error Responses
| Status | Condition |
|--------|-----------|
| 404 | Opening not found |
| 422 | Validation failed (see Validation Errors) |
| 401 | Authentication required |
| 500 | Database error |

#### Validation Errors (422)
| Field | Error Condition |
|-------|-----------------|
| `minimum_experience_years` | > `maximum_experience_years` |
| `mandatory_skills` | Duplicate (case-insensitive) |
| `latest_start_date` | Invalid date format (not YYYY-MM-DD) |
| `location_rules` | `relocation_required` true but `allowed_locations` empty |
| `minimum_ats_score` | Not in [0, 100] |
| Experience fields | Not in [0, 80] |

---

### 2. Get Eligibility Configuration

**GET** `/openings/{opening_id}/eligibility-config`

Retrieves current eligibility configuration for a job opening.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `opening_id` | string | Yes | Job opening UUID |

#### Success Response (200)
Same as PUT response.

#### Error Responses
| Status | Condition |
|--------|-----------|
| 404 | Opening not found OR configuration not set |
| 401 | Authentication required |

---

### 3. Evaluate Candidate Eligibility

**POST** `/candidates/{candidate_id}/eligibility/evaluate`

Evaluates a candidate against the job's eligibility rules. Creates new evaluation record.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `candidate_id` | string | Yes | Candidate UUID |

#### Request Body
```json
{
  "opening_id": "uuid"
}
```

#### Success Response (201)
```json
{
  "evaluation_id": "uuid",
  "candidate_id": "uuid",
  "opening_id": "uuid",
  "status": "ELIGIBLE",
  "ats_score": 78.5,
  "rules": {
    "minimum_ats_score": {
      "status": "PASS",
      "reason": "The current ATS score meets the configured threshold.",
      "value": 78.5,
      "required": 65
    },
    "mandatory_skills": {
      "status": "PASS",
      "reason": "All configured mandatory skills have profile or resume evidence.",
      "matched": ["Python", "SQL"],
      "missing": [],
      "evidence_sources": {
        "Python": "candidate_reported",
        "SQL": "resume_extraction"
      }
    },
    "experience": {
      "status": "PASS",
      "reason": "Parsed experience is within the configured range.",
      "years": 3.0,
      "minimum_years": 1,
      "maximum_years": 5
    },
    "location": {
      "status": "PASS",
      "reason": "Candidate location and supplied work-mode preference meet configured rules.",
      "candidate_location": "Bangalore",
      "candidate_preference": "HYBRID"
    },
    "availability": {
      "status": "NOT_CONFIGURED"
    }
  },
  "mandatory_skills_matched": ["Python", "SQL"],
  "mandatory_skills_missing": [],
  "experience_result": {
    "status": "PASS",
    "reason": "Parsed experience is within the configured range.",
    "years": 3.0,
    "minimum_years": 1,
    "maximum_years": 5
  },
  "location_result": {
    "status": "PASS",
    "reason": "Candidate location and supplied work-mode preference meet configured rules.",
    "candidate_location": "Bangalore",
    "candidate_preference": "HYBRID"
  },
  "availability_result": {
    "status": "NOT_CONFIGURED"
  },
  "missing_information": [],
  "review_reasons": [],
  "decision_explanation": "Configured rules were met using available evidence. Recruiter review is still required.",
  "configuration_version": 1,
  "evaluated_at": "2026-01-01T00:00:00+00:00",
  "human_review_required": true
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `evaluation_id` | string | Unique evaluation UUID |
| `candidate_id` | string | Candidate UUID |
| `opening_id` | string | Job opening UUID |
| `status` | enum | `ELIGIBLE`, `REVIEW`, `REJECTED` |
| `ats_score` | float/null | Current ATS score (null if not current) |
| `rules` | object | Per-rule evaluation details |
| `mandatory_skills_matched` | string[] | Skills with evidence |
| `mandatory_skills_missing` | string[] | Required skills without evidence |
| `experience_result` | object | Experience rule result |
| `location_result` | object | Location rule result |
| `availability_result` | object | Availability rule result |
| `missing_information` | string[] | Human-readable missing data list |
| `review_reasons` | string[] | Reasons requiring human review |
| `decision_explanation` | string | Overall decision rationale |
| `configuration_version` | int | Config version used |
| `evaluated_at` | string | ISO timestamp |
| `human_review_required` | boolean | Always true |

#### Rule Status Values
| Status | Meaning |
|--------|---------|
| `PASS` | Rule satisfied |
| `FAIL` | Explicit threshold not met (causes REJECTED) |
| `REVIEW` | Missing/uncertain evidence |
| `NOT_CONFIGURED` | Rule not in configuration |

#### Error Responses
| Status | Condition |
|--------|-----------|
| 404 | Candidate or opening not found |
| 409 | Candidate doesn't belong to opening |
| 409 | No eligibility configuration for opening |
| 401 | Authentication required |
| 500 | Database error |

---

### 4. Get Latest Eligibility Evaluation

**GET** `/candidates/{candidate_id}/eligibility`

Retrieves the latest eligibility evaluation. Re-evaluates if inputs changed (fingerprint mismatch).

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `candidate_id` | string | Yes | Candidate UUID |

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `opening_id` | string | Yes | Job opening UUID |

#### Success Response (200)
Same as POST evaluation response.

#### Re-evaluation Logic
```python
fingerprint = hash(candidate_id, candidate.updated_at, score, score_evidence,
                   opening_id, opening.updated_at, configuration.version)

latest = get_latest_eligibility_evaluation(candidate_id, opening_id)
if latest is None or latest.fingerprint != fingerprint:
    return evaluate_and_persist(candidate, opening, configuration)
return latest
```

**Triggers re-evaluation when:**
- Candidate updated (skills, name, location, etc.)
- Resume uploaded/replaced (clears score, updates candidate)
- New ATS score calculated
- Opening requirements changed
- Eligibility configuration updated

#### Error Responses
| Status | Condition |
|--------|-----------|
| 404 | Candidate or opening not found |
| 409 | Candidate doesn't belong to opening |
| 404 | No eligibility configuration for opening |
| 401 | Authentication required |

---

## Data Models

### EligibilityConfigurationRequest
```python
class EligibilityConfigurationRequest(BaseModel):
    minimum_ats_score: float | None = Field(default=None, ge=0, le=100)
    mandatory_skills: list[Skill] = Field(default_factory=list, max_length=100)
    minimum_experience_years: float | None = Field(default=None, ge=0, le=80)
    maximum_experience_years: float | None = Field(default=None, ge=0, le=80)
    location_rules: EligibilityLocationRules = Field(default_factory=EligibilityLocationRules)
    decision_policy: EligibilityDecisionPolicy = Field(default_factory=EligibilityDecisionPolicy)
```

### EligibilityLocationRules
```python
class EligibilityLocationRules(BaseModel):
    allowed_locations: list[str] = Field(default_factory=list, max_length=100)
    work_mode: Literal["ONSITE", "HYBRID", "REMOTE"] | None = None
    remote_allowed: bool = False
    relocation_required: bool = False
    latest_start_date: str | None = Field(default=None, max_length=10)
```

### EligibilityDecisionPolicy
```python
class EligibilityDecisionPolicy(BaseModel):
    manual_review_on_missing_data: bool = True
```

### EligibilityConfigurationResponse
```python
class EligibilityConfigurationResponse(BaseModel):
    opening_id: str
    version: int
    configuration: EligibilityConfigurationRequest
    created_at: str
    updated_at: str
```

### EligibilityEvaluationRequest
```python
class EligibilityEvaluationRequest(BaseModel):
    opening_id: str = Field(min_length=1, max_length=80)
```

### EligibilityEvaluationResponse
```python
class EligibilityEvaluationResponse(BaseModel):
    evaluation_id: str
    candidate_id: str
    opening_id: str
    status: Literal["ELIGIBLE", "REVIEW", "REJECTED"]
    ats_score: float | None
    rules: dict[str, Any]
    mandatory_skills_matched: list[str]
    mandatory_skills_missing: list[str]
    experience_result: dict[str, Any]
    location_result: dict[str, Any]
    availability_result: dict[str, Any]
    missing_information: list[str]
    review_reasons: list[str]
    decision_explanation: str
    configuration_version: int
    evaluated_at: str
    human_review_required: Literal[True] = True
```

---

## Example Workflows

### Workflow 1: Configure and Evaluate

```bash
# 1. Configure eligibility for opening
PUT /api/v1/openings/abc-123/eligibility-config
{
  "minimum_ats_score": 65,
  "mandatory_skills": ["Python", "SQL"],
  "minimum_experience_years": 2,
  "location_rules": {
    "allowed_locations": ["Bangalore"],
    "remote_allowed": true
  }
}

# 2. Create candidate and score them
POST /api/v1/candidates {name: "John", opening_id: "abc-123", skills: ["Python", "SQL"]}
POST /api/v1/resumes/upload {file: resume.pdf, candidate_id: "cand-456"}
# ... wait for processing ...
POST /api/v1/candidates/score {candidate_id: "cand-456", job_id: "abc-123"}

# 3. Evaluate eligibility
POST /api/v1/candidates/cand-456/eligibility/evaluate {"opening_id": "abc-123"}
# → {status: "ELIGIBLE", ...}

# 4. Later: candidate updates skills
PATCH /api/v1/candidates/cand-456 {"skills": ["Python"]}

# 5. Get eligibility (auto re-evaluates)
GET /api/v1/candidates/cand-456/eligibility?opening_id=abc-123
# → {status: "REVIEW", missing_information: ["Mandatory skill evidence is not present for: SQL"]}
```

### Workflow 2: Check Configuration Exists

```bash
GET /api/v1/openings/abc-123/eligibility-config
# 200 → config exists
# 404 → not configured
```

### Workflow 3: Cross-Job Ownership Check

```bash
# Candidate cand-456 belongs to opening abc-123
POST /api/v1/candidates/cand-456/eligibility/evaluate {"opening_id": "xyz-789"}
# → 409 "Candidate application does not belong to this job opening."
```

---

## Rate Limits & Constraints

| Limit | Value |
|-------|-------|
| Config versions per opening | Unlimited (integer counter) |
| Evaluations per candidate/opening | Unlimited (indexed by evaluated_at) |
| Mandatory skills per config | 100 max |
| Allowed locations per config | 100 max |
| Evaluation retention | Indefinite (no auto-cleanup) |

---

## Security

- All endpoints require valid recruiter session
- Ownership validated: `candidate.opening_id == opening_id`
- No cross-opening data access
- SQL injection prevented via parameterized queries
- No sensitive data in error responses