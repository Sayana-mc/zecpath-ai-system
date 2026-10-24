# Day 60 — Code Walkthrough

- `src/batching.py`: fixed-size batches.
- `src/cache.py`: bounded TTL/LRU cache and hit/miss metrics.
- `src/pipeline.py`: explicit mock inference and bounded asynchronous concurrency.
- `src/benchmark.py`: load scenarios, throughput and memory measurements, JSON/Markdown report generation.
- `src/main.py`: benchmark entry point.
- `tests/test_day60.py`: batching, cache, pipeline, and report tests.
- `config/performance_config.json`: batch size, concurrency, cache, synthetic workload, and test levels.

Replace mock inference with a real provider/model call only after documenting timeouts, privacy, provider limits, error handling, and model-versioned cache keys.
