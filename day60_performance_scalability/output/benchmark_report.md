# Day 60 — Performance Benchmark Report

**Important:** Synthetic local simulation only; not production measurements.

| Items | Batch | Concurrency | Elapsed (s) | Throughput/items/s | Cache hit rate | Peak traced bytes |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 8 | 1 | 0.793689 | 125.99 | 0.5 | 65536 |
| 100 | 8 | 2 | 0.403663 | 247.73 | 0.5 | 38719 |
| 100 | 8 | 4 | 0.191453 | 522.32 | 0.5 | 38631 |
| 100 | 8 | 8 | 0.102989 | 970.98 | 0.5 | 37863 |

## Limitations
- Mock inference only; no live AI provider or production database.
- tracemalloc measures Python-traced allocations, not total process or GPU memory.
- Results are not a production SLA or real model-inference benchmark.

## Production benchmark next steps
Run against staging with representative anonymized inputs, actual model/API and database calls. Record p50/p95/p99, throughput, error rate, queue age, CPU/RAM/GPU, and cost per resume.
