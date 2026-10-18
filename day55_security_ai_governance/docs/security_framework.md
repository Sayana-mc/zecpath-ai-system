# Security Framework — Day 55

## Threats and controls
| Threat | Reference control | Production requirement |
|---|---|---|
| Unauthorized access | Role-based access control | Integrate real authentication, MFA, session expiry |
| Score/decision alteration | Hash-chained audit events | Remote append-only logs, signatures, alerting |
| Data disclosure | Encrypted local payloads | Managed key vault, TLS, encrypted backups |
| Processing without permission | Purpose-specific consent check | Clear notice, withdrawal workflow, legal review |
| Excessive retention | Retention policy and expiry helper | Scheduled deletion, legal holds, deletion verification |
| Excessive data collection | No raw transcript by default | Data inventory and minimization review |
| Unreviewed AI outcome | Human review always required | Enforce approval workflow server-side |
| Key compromise | External environment variable supported | KMS, rotation, least privilege, no key logging |

## Roles
- admin: all permissions; assign sparingly and review regularly.
- hiring_manager: read scores, reports, and decisions.
- reviewer: read relevant candidate material and record a human decision.
- auditor: read audit events and governance documents.
- candidate: read/update consent only.

The demo RBAC layer is authorization logic, not authentication. Never trust a role sent by an untrusted client.

## Secure deployment checklist
- [ ] Authentication and MFA enabled where appropriate.
- [ ] Role claims validated server-side.
- [ ] TLS enforced in transit.
- [ ] Encryption keys stored in KMS/secret manager.
- [ ] Secrets excluded from Git and logs.
- [ ] Audit logs exported to protected storage.
- [ ] Retention and legal-hold process approved.
- [ ] Consent withdrawal and deletion workflow tested.
- [ ] Backups encrypted and restoration tested.
- [ ] Security incident owner and response contacts assigned.
- [ ] Human-review workflow enforced server-side.
