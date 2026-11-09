# Day 21 — Eligibility Rule Configuration

## Configuration Format

Eligibility rules are configured per job opening via the API. The configuration is versioned and stored in `eligibility_configurations` table.

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "minimum_ats_score": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 100,
      "description": "Minimum ATS score required. Null = no threshold."
    },
    "mandatory_skills": {
      "type": "array",
      "items": {"type": "string", "minLength": 1, "maxLength": 80},
      "maxItems": 100,
      "uniqueItems": true,
      "description": "Required skills (case-insensitive, normalized). Empty = no requirement."
    },
    "minimum_experience_years": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 80,
      "description": "Minimum years of experience. Null = no minimum."
    },
    "maximum_experience_years": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 80,
      "description": "Maximum years of experience. Exceeding triggers REVIEW. Null = no maximum."
    },
    "location_rules": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "allowed_locations": {
          "type": "array",
          "items": {"type": "string", "minLength": 1, "maxLength": 160},
          "maxItems": 100,
          "description": "Accepted candidate locations. Empty = no restriction."
        },
        "work_mode": {
          "type": ["string", "null"],
          "enum": ["ONSITE", "HYBRID", "REMOTE"],
          "description": "Required work mode. Null = no requirement."
        },
        "remote_allowed": {
          "type": "boolean",
          "default": false,
          "description": "Allow REMOTE candidates as exception to location rules."
        },
        "relocation_required": {
          "type": "boolean",
          "default": false,
          "description": "Require relocation willingness for location mismatches."
        },
        "latest_start_date": {
          "type": ["string", "null"],
          "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
          "format": "date",
          "description": "Latest acceptable start date (YYYY-MM-DD)."
        }
      },
      "description": "Location and work mode constraints."
    },
    "decision_policy": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "manual_review_on_missing_data": {
          "type": "boolean",
          "default": true,
          "description": "Route missing/uncertain evidence to REVIEW instead of assuming negative."
        }
      },
      "description": "Policy for handling missing evidence."
    }
  },
  "required": ["location_rules", "decision_policy"],
  "description": "Per-job eligibility configuration"
}
```

### Validation Rules

| Rule | Enforcement |
|------|-------------|
| `minimum_experience_years` ≤ `maximum_experience_years` | 422 if violated |
| `mandatory_skills` unique (case-insensitive) | 422 if duplicates |
| `latest_start_date` valid ISO date | 422 if invalid |
| `relocation_required` → `allowed_locations` non-empty | 422 if violated |
| `minimum_ats_score` in [0, 100] | 422 if out of range |
| Experience bounds in [0, 80] | 422 if out of range |

## Configuration Examples

### Example 1: Strict Technical Role

```json
{
  "minimum_ats_score": 70,
  "mandatory_skills": ["Python", "SQL", "Docker"],
  "minimum_experience_years": 3,
  "maximum_experience_years": 8,
  "location_rules": {
    "allowed_locations": ["Bangalore", "Hyderabad", "Pune"],
    "work_mode": "HYBRID",
    "remote_allowed": false,
    "relocation_required": true,
    "latest_start_date": "2026-07-01"
  },
  "decision_policy": {
    "manual_review_on_missing_data": true
  }
}
```

### Example 2: Remote-Friendly Role

```json
{
  "minimum_ats_score": 60,
  "mandatory_skills": ["JavaScript", "React", "TypeScript"],
  "minimum_experience_years": 2,
  "maximum_experience_years": null,
  "location_rules": {
    "allowed_locations": [],
    "work_mode": "REMOTE",
    "remote_allowed": true,
    "relocation_required": false,
    "latest_start_date": null
  },
  "decision_policy": {
    "manual_review_on_missing_data": true
  }
}
```

### Example 3: Entry-Level Role

```json
{
  "minimum_ats_score": 50,
  "mandatory_skills": ["Python"],
  "minimum_experience_years": 0,
  "maximum_experience_years": 2,
  "location_rules": {
    "allowed_locations": ["Chennai", "Remote"],
    "work_mode": "ONSITE",
    "remote_allowed": true,
    "relocation_required": false,
    "latest_start_date": "2026-08-01"
  },
  "decision_policy": {
    "manual_review_on_missing_data": true
  }
}
```

### Example 4: Minimal Configuration (Review-Heavy)

```json
{
  "minimum_ats_score": null,
  "mandatory_skills": [],
  "minimum_experience_years": null,
  "maximum_experience_years": null,
  "location_rules": {
    "allowed_locations": [],
    "work_mode": null,
    "remote_allowed": false,
    "relocation_required": false,
    "latest_start_date": null
  },
  "decision_policy": {
    "manual_review_on_missing_data": true
  }
}
```

**Result:** All candidates → REVIEW (missing ATS score, no rules to pass)

## Configuration Lifecycle

### Create/Update
```
PUT /api/v1/openings/{opening_id}/eligibility-config
```
- Increments version counter (starts at 1)
- Preserves `created_at` from previous version
- Updates `updated_at` to now
- Validates all rules before persisting

### Retrieve
```
GET /api/v1/openings/{opening_id}/eligibility-config
```
- Returns current version with full configuration
- 404 if never configured

### Version History
Not directly exposed via API. Query `eligibility_configurations` table:
```sql
SELECT version, configuration_json, created_at, updated_at
FROM eligibility_configurations
WHERE opening_id = '...';
```

## Skill Normalization in Configuration

Mandatory skills in configuration are normalized at evaluation time using the same canonicalizer as resume skills:

```python
def _canonical_skill(value: str) -> str:
    canonical = normalize_skill_name(value)  # Day 9 normalizer
    return (canonical or value).casefold().strip()
```

**Implications:**
- Configuration skills automatically match synonyms
- "PySpark" in config matches "Spark" in resume
- "k8s" in config matches "Kubernetes" in resume
- Case and whitespace ignored

## Location Matching Details

### Exact Match (Case-Insensitive)
```
allowed_locations: ["Bangalore", "Remote"]
candidate_location: "bangalore" → MATCH
candidate_location: "BANGALORE" → MATCH
candidate_location: "Bangalore, Karnataka" → NO MATCH
```

### Remote Exception
```
remote_allowed: true
candidate.work_mode_preference: "REMOTE"
→ PASS regardless of allowed_locations
```

### Relocation Logic
```
relocation_required: true
allowed_locations: ["Bangalore"]
candidate_location: "Mumbai"
candidate.relocation_willingness: true → PASS
candidate.relocation_willingness: null → REVIEW
candidate.relocation_willingness: false → REVIEW (or REJECTED if strict)
```

## Experience Range Behavior

| Candidate Experience | Min Config | Max Config | Result |
|---------------------|------------|------------|--------|
| 3 years | 2 | 5 | PASS |
| 1 year | 2 | 5 | REJECTED (< min) |
| 6 years | 2 | 5 | REVIEW (> max) |
| 3 years | null | 5 | PASS (no min) |
| 3 years | 2 | null | PASS (no max) |
| null (unparsed) | 2 | 5 | REVIEW (uncertain) |

## Decision Policy

### `manual_review_on_missing_data: true` (Default)
- Missing ATS score → REVIEW
- Missing mandatory skills → REVIEW
- Missing experience → REVIEW
- Missing location → REVIEW (if configured)
- Missing availability → REVIEW (if configured)

### `manual_review_on_missing_data: false` (Not Recommended)
- Would treat missing as negative evidence
- Not currently differentiated in engine (always reviews missing)

## Best Practices

1. **Start conservative** — Use REVIEW-heavy config, tighten based on data
2. **Set minimum_ats_score** — Only after baseline established
3. **Limit mandatory_skills** — 3-5 truly required skills
4. **Use experience ranges** — Avoid arbitrary maximums
5. **Enable remote_allowed** — For distributed teams
6. **Set latest_start_date** — Only when business-critical
7. **Test configuration** — Use synthetic candidates before real use
8. **Document rationale** — Why each rule exists

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| 20+ mandatory skills | Over-constrains, most → REVIEW | 3-5 core skills |
| Maximum experience = 5 | Age bias risk, rejects seniors | No maximum, or high (15+) |
| Relocation required, no locations | Config validation fails | Set allowed_locations |
| Minimum ATS = 90 | Arbitrary, excludes good candidates | Data-driven threshold |
| No decision_policy | Defaults to review, but implicit | Explicit true |
| Exact location strings | "Bangalore" ≠ "Bengaluru" | Normalize or use multiple |

## Migration from Manual Review

If currently using manual review only:
1. Start with minimal config (Example 4)
2. Add mandatory_skills for clearly required skills
3. Add minimum_experience_years if role requires it
4. Add location_rules if location matters
5. Set minimum_ats_score ONLY after evaluation data exists
6. Monitor REVIEW rate; adjust rules to reduce noise