# Day 23 — Screening Interaction Data Structure

## Overview

The `screening_interactions` data model links transcript segments directly to specific screening questions and extracts structured candidate answers.

---

## 1. Database Table Specification

```sql
CREATE TABLE IF NOT EXISTS screening_interactions (
    interaction_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    candidate_answer TEXT NOT NULL,
    answer_type TEXT,
    validation_status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (validation_status IN ('PENDING', 'VALID', 'INVALID', 'AMBIGUOUS')),
    related_segments TEXT NOT NULL DEFAULT '[]',
    display_order INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS screening_interactions_session_idx
    ON screening_interactions(session_id, display_order);
```

---

## 2. Relationships

- **Parent**: `screening_sessions(session_id)`
- **Linked Question**: `question_id` (references question bank, e.g. `HR001`)
- **Related Segments**: JSON array of `segment_id`s that contributed to this answer.
- **Cascade Deletion**: When a session is deleted, all interactions and segments are automatically purged.

