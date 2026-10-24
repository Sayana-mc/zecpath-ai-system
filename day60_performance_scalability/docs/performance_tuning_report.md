# Day 60 — Performance Tuning Report

## Objective
Optimize inference time, API latency, resume throughput, memory use, and cache behavior.

## Prototype evidence
Run `python -m day60_performance_scalability.src.main` to generate the JSON and Markdown benchmark reports. This package uses mock inference, repeated synthetic text, and simulated delay. Results are local engineering evidence only—not production measurements or real AI model latency.

## Techniques
1. **Batching:** `src/batching.py` groups items by configurable batch size.
2. **Bounded concurrency:** `asyncio.Semaphore` limits concurrent simulated calls.
3. **TTL/LRU caching:** `src/cache.py` limits entries and expires old values.
4. **Memory observation:** `tracemalloc` records Python-traced allocation peaks.
5. **Benchmarking:** records elapsed time, throughput, cache hit rate, success/failure counts, and memory.

## Production optimization checklist
- Profile preprocessing, tokenization, inference, serialization, network, and database time separately.
- Reuse clients and connection pools.
- Use provider-supported model batching only where latency permits.
- Cache only deterministic, safe derived results; include content hash and model/rubric version in keys.
- Do not cache raw sensitive documents without approved privacy controls.
- Use bounded queues, request-size limits, timeouts, and backpressure.
- Measure process RSS and GPU memory separately; `tracemalloc` does not capture all native/GPU allocations.
- Test cold and warm cache and repeat runs; report median and p95/p99.
