# Deployment Guide

This is a deployment checklist, not proof of an existing production deployment.

## Pre-deployment
- Confirm runtime and dependency versions.
- Lock dependencies and scan vulnerabilities.
- Configure secrets using deployment environment/secret manager.
- Validate migrations, backup, and restore.
- Configure TLS, authentication, authorization, and rate limits.
- Define queue retry, idempotency, and dead-letter policy.
- Configure model-provider timeouts, quotas, and failure handling.
- Configure logs, metrics, traces, and alert routing.
- Verify privacy, retention, access controls, and audit completeness.
- Test health/readiness and graceful shutdown.

## Suggested stages
Local development → Automated tests → Staging with synthetic/approved anonymized data → Load/failure tests → Limited rollout → Production rollout after acceptance criteria pass.

## Scaling
Scale stateless API replicas behind a load balancer. Scale workers using queue depth/age and resource usage. Separate parsing and inference workloads when measured resource profiles justify it. Monitor p95/p99 latency, errors, backlog, CPU/memory, and provider quotas. Cache only safe, reusable, versioned results.

## Rollback
Keep a known-good artifact, version configuration, define rollback triggers, test database migration compatibility, and verify health after rollback.

## Acceptance criteria
Tests and contracts pass; secrets and raw candidate data are not logged; required audit fields exist; alerts reach owners; staging performance meets approved targets; human review and failure recovery are verified.
