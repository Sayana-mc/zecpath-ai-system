# Data Retention Policy — Day 55

| Data category | Proposed retention | Expiry action |
|---|---:|---|
| Interview transcripts | 90 days | Delete or anonymize |
| Reports | 365 days | Delete or anonymize |
| Audit logs | 730 days | Delete according to approved audit schedule |
| Consent records | 730 days | Retain for accountability, then delete subject to legal requirements |

Rules:
1. The schedule is a proposed project baseline, not a legal requirement.
2. Retention begins at a clearly defined event (for example, application closure); production must specify it.
3. Legal holds and documented investigations may pause deletion.
4. Deletion must cover primary storage, replicas, exports, and backups according to a documented backup-expiry schedule.
5. Audit logs should not contain transcript contents or unnecessary personal data.
6. Record deletion activity without copying deleted sensitive content into the deletion log.
7. Review the schedule with privacy/legal stakeholders before production.
