# AI Compliance Design — Day 55

## Purpose
Define controls for responsible use of AI-assisted hiring evaluations.

## Core principles
- Purpose limitation: use candidate data only for the stated hiring-evaluation purpose.
- Data minimization: avoid storing raw transcripts by default; retain only what is necessary.
- Human oversight: scores and recommendations are advisory, and a human decision-maker remains responsible.
- No automatic rejection: automated rejection is disabled.
- Traceability: record score and decision events with actor, timestamp, model version, reason codes, and hash-chain linkage.
- Access limitation: users receive only the permissions required for their role.
- Retention limitation: delete or anonymize records when the approved retention period expires, unless a documented legal hold applies.

## Consent
Record candidate ID, purpose, granted/revoked state, timestamp, actor, and consent-policy version. Before processing, verify that consent is active for the exact purpose. Consent text and lawful basis must be reviewed by the organization’s privacy/legal owner.

## Audit trail
Log score and decision events. Do not include full resumes, raw transcript text, passwords, tokens, or other unnecessary sensitive content in audit details. Hash chaining detects modifications but is not tamper-proof if an attacker can rewrite both the log and head file. Production should use append-only storage, signatures, independent log export, and monitored access.

## Retention proposal
- Transcripts: 90 days
- Reports: 365 days
- Audit logs: 730 days
- Consent records: 730 days

These are project defaults, not a legal determination. Confirm the schedule against business needs, applicable law, candidate notices, and legal holds before deployment.

## Secure storage
The reference code encrypts report/transcript-note payloads with Fernet. In production, use a managed KMS/secret vault, restrict key access, rotate keys, encrypt backups, and test restoration. Never commit keys or place them in screenshots.

## Incident response
1. Restrict affected access and preserve relevant audit evidence.
2. Notify the security/privacy owner.
3. Identify affected systems, candidates, data types, and time window.
4. Rotate/revoke credentials or keys if compromise is suspected.
5. Remediate, validate, and document corrective actions.
6. Follow applicable notification requirements and internal policy.

## Limitations
This is a design and local reference implementation, not legal advice, certification, or a production-ready identity system.
