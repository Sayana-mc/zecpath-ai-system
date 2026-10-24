# Day 60 — Scalability Strategy

## 1. Architecture
Keep API replicas stateless. Use a durable queue and worker pool for long-running resume parsing. Scale APIs, workers, and model services independently.

## 2. Load balancing
- Put a managed Layer 7 load balancer/API gateway before backend replicas.
- Enable health/readiness checks and remove unhealthy replicas.
- Enforce TLS, auth, rate limits, request-size limits, and timeouts.
- Prefer round-robin or least-request where supported; avoid sticky sessions unless required.
- Return controlled 429/503 responses during saturation.

## 3. Microservice scaling
- Backend: scale on request rate, CPU, and p95 latency.
- Resume workers: scale on queue depth and oldest-job age.
- ATS/Screening/Interview/Decision: scale separately using request rate, inference latency, provider quotas, and CPU/GPU.
- Database: optimize indexes and queries, use bounded connection pools, then evaluate read replicas.
- Cache: local bounded TTL for process-local use; shared cache only when cross-replica behavior and privacy policy are addressed.

## 4. Backpressure
Use bounded queues, worker concurrency limits, retry limits, and dead-letter handling. Separate interactive interview traffic from background resume batches so batch workloads cannot starve real-time requests.

## 5. Autoscaling signals
Use CPU, memory, p95/p99 latency, request rate, queue depth, oldest message age, provider throttling, and GPU utilization. Configure min/max replicas and cooldown windows based on staging measurements.

## 6. Cache and memory
Cache only deterministic derived results; include content hash and model/rubric version in the key; enforce TTL and size limits; invalidate when content changes. Stream large documents, release buffers promptly, paginate database reads, and monitor RSS/GPU memory.

## 7. Rollout
1. Establish a measured baseline.
2. Change one bottleneck at a time.
3. Load-test in staging.
4. Compare p50/p95/p99, throughput, error rate, memory, and cost.
5. Canary release and monitor.
6. Roll back if latency, errors, memory, or quality regress beyond approved limits.

This is a proposed strategy, not a deployed autoscaler/load balancer. Thresholds depend on the actual hosting and model environment.
