# Day 53–60 Security & AI Governance — ZecPath AI Hiring System

## Overview

The ZecPath AI Hiring System implements enterprise-grade security, cryptographic audit verification, role-based access control, and ethical AI governance standards compliant with EEOC guidelines, GDPR data protection mandates, and EU AI Act high-risk AI system provisions.

---

## 1. Cryptographic Audit Logging (SHA-256 Hash Chaining)

### Ledger Mechanics
- Every critical event (report generation, candidate score change, status update, recruiter decision) is committed to the `audit_events` table.
- Each event row includes:
  - `event_id`: Unique identifier
  - `event_type`, `user_id`, `action`, `resource_type`, `resource_id`
  - `details_json`: Serialized event payload
  - `timestamp`: UTC ISO timestamp
  - `prev_hash`: Cryptographic hash of the immediately preceding event record (or `"GENESIS"` for the initial record)
  - `event_hash`: SHA-256 hash computed over `event_id:timestamp:user_id:action:resource_id:prev_hash`

### Tamper-Evidence Verification
- The `verify_audit_trail()` function traverses the event log in chronological sequence.
- Re-hashes each record and confirms that `prev_hash` matches the preceding record's `event_hash`.
- Any manual database tampering, deleted row, or altered field immediately invalidates the chain, identifying the exact corrupted record index.

---

## 2. Role-Based Access Control (RBAC)

The system enforces strict permission checks across defined roles:

| Role | Permissions |
|---|---|
| `admin` | Full administrative access, tenant settings, purge management, audit trail inspection. |
| `lead_recruiter` | Manage openings, view all candidate evaluations, generate intelligence reports, make hiring decisions. |
| `recruiter` | Create candidates, upload resumes, trigger screening, view candidate evaluation summaries. |
| `interviewer` | Conduct and evaluate assigned technical and HR interview rounds. |
| `auditor` | Read-only access to audit logs, compliance reports, and verification endpoints. |

---

## 3. Data Retention Management (180-Day Compliance)

Under GDPR and SOC-2 hiring regulations, candidate evaluation records should not be indefinitely retained without active business necessity.
- **Retention Limit:** 180 days from creation date.
- **Automated Check:** `check_data_retention()` inspects timestamps across candidates, resumes, and evaluation sessions, returning a manifest of eligible purge records.
- **Purge Safeguard:** Purges require administrative elevation and produce a cryptographically chained audit event documenting the action.

---

## 4. Ethical AI Governance Standards

1. **No Automated Rejection:** The AI system acts purely as an assistive scoring and synthesis tool. All final employment decisions require explicit human recruiter confirmation.
2. **Prohibition of Emotion & Sentiment Disqualification:** Candidate screening does not penalize individuals based on perceived emotion or tone inflections.
3. **Explicit Consent Verification:** Behavioral and voice recording analyses require explicit candidate opt-in recorded in `candidate_behavioral_records`.

