# Day 60: Performance Benchmark, Load Test & Scalability Report

## 1. Test Environment & Method
- **Platform:** Local Windows 11, Python 3.12, FastAPI + Uvicorn, SQLite (`data/zecpath.sqlite3`).
- **Benchmark Script:** `scripts/run_day56_60_verification.py`
- **Raw Data:** `day60_performance_scalability/day60_before_after_comparison.json`

## 2. Batch Resume Processing (`TTLCache` Cold vs Warm on `/api/v1/resumes/batch-process`, 20 resumes)
- **Cold Run:** `253.38 ms` (`15` intra-batch cache hits from repeated skills text)
- **Warm Run:** `231.86 ms` (`20 / 20` cache hits, `cache_hit_rate = 0.875`)

## 3. Local In-Process `TTLCache` + `tracemalloc` Benchmark (`50` items)
| Concurrency Level | Elapsed (s) | Throughput (items/s) | Cache Hit Rate | Peak Memory (bytes) | Success Rate |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.0003 | 150,105.07 | 0.80 | 10,937 | 100.0% |
| 5 | 0.0002 | 235,626.77 | 0.80 | 3,193 | 100.0% |
| 10 | 0.0002 | 217,013.89 | 0.80 | 3,193 | 100.0% |
| 25 | 0.0002 | 217,675.23 | 0.80 | 3,193 | 100.0% |

## 4. Live HTTP Concurrent Load Test (`GET /api/v1/candidates/cand_arun_kumar/cross-round-evaluation`)
| Concurrent Workers | Total Requests | Successful | Failed | Avg Latency (ms) | P95 Latency (ms) | Throughput (req/s) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 2 | 0 | 258.88 | 259.01 | 3.85 |
| 5 | 10 | 10 | 0 | 370.25 | 473.27 | 12.25 |
| 10 | 20 | 20 | 0 | 634.91 | 925.29 | 13.84 |
| 25 | 50 | 50 | 0 | 1483.13 | 2245.11 | 14.49 |

## 5. Horizontal Scaling Strategy & Limitations
- **Observed Bottleneck:** At 25 concurrent workers, single-process Uvicorn + SQLite + PBKDF2-SHA256 Basic Auth verification per request increased P95 latency to `2245.11 ms` (triggering the real Observability UI alert `API p95 latency is elevated at 1559.44ms`).
- **Scaling Recommendations:** Use session cookies/JWT instead of per-request PBKDF2 Basic Auth, move `batch_process_resumes()` to true `asyncio.gather()` / Celery/RQ workers, migrate SQLite to PostgreSQL with connection pooling, and deploy behind Nginx/ALB with Redis-backed cache.
