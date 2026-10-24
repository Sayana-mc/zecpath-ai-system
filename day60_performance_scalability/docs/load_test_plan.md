# Day 60 — Simulated Load Test Plan

Run:
```powershell
python -m day60_performance_scalability.src.main
python -m unittest discover -s .\day60_performance_scalability\tests -v
```

Scenarios: configurable concurrency levels, repeated text for cache hits, simulated service delay, bounded batch size, and Python allocation tracing.

Metrics: elapsed time, throughput, cache hit rate, success/failure counts, current/peak traced bytes.

Limitations: no live AI provider, production database, deployed queue/load balancer, or actual model latency. `tracemalloc` does not include all native or GPU allocations.

For production-grade testing, use a staging environment with approved tools such as Locust or k6. Use synthetic/anonymized inputs and record p50/p95/p99, throughput, HTTP errors, provider throttling, queue age, CPU/RSS/GPU memory, and cost. Define stop conditions before testing.
