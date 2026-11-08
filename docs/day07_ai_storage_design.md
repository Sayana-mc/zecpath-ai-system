# Day 7 — AI storage design

| Information | Current storage | Integrity/version limitation |
|---|---|---|
| Job and requirements | `openings` SQLite table | No parsed-JD object or JD revision history |
| Resume binary | Temporary upload path | Deleted after processing; cannot reprocess original |
| Extracted text and profile | `candidates.resume_text`, `resume_data` JSON | Replaced on re-upload; no profile version history |
| Processing status/result | `processing_jobs` | In-process work, no durable queue/retry, candidate ID is not a foreign key |
| Embeddings | Not persisted | Recomputed; no cache invalidation/version metadata |
| ATS score and explanation | `candidates.score`, `score_evidence` JSON | One current value; cleared on input changes, no history |
| Ranking/shortlist | Calculated from saved candidate scores | No ranking snapshot or persisted shortlist |
| Screening report | `screening_reports` JSON | Separate from ATS score |
| Future interviews | No root table | Not implemented |

SQLite foreign keys connect applications and reports to jobs/candidates, and
the application uses transactions and additive startup column checks. These
are not a versioned migration framework. Existing data must not be deleted to
apply changes. The single local account is not tenant isolation or RBAC.

Production needs include encrypted storage/backups, retention and deletion
policy, consent/data export, migration versioning, access audit, and recovery
procedures. None is claimed as implemented.
