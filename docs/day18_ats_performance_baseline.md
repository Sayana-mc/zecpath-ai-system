# Day 18 — ATS Performance Baseline

## Status: NOT ESTABLISHED

**Reason:** No controlled performance baseline has been collected for the current root API workflow. Previous stage-folder benchmarks (in `day18_ats_optimization/`) measure standalone modules, not the integrated root application endpoints.

## Required Baseline Measurements

Before any optimization claims can be made, the following must be measured on the **root application** (`src/main.py`) using **synthetic fixtures**:

### 1. Resume Upload & Processing

| Operation | Target Metric | Conditions |
|-----------|---------------|------------|
| `POST /resumes/upload` (TXT, 1 KB) | Latency p50, p95 | Cold start, warm start |
| `POST /resumes/upload` (PDF, 100 KB) | Latency p50, p95 | With text extraction |
| `POST /resumes/upload` (DOCX, 100 KB) | Latency p50, p95 | With text extraction |
| Background processing (TXT) | End-to-end time | QUEUED → COMPLETED |
| Background processing (PDF) | End-to-end time | QUEUED → COMPLETED |

### 2. Resume Parsing

| Operation | Target Metric | Conditions |
|-----------|---------------|------------|
| `POST /resumes/parse` | Latency p50, p95 | Completed job |
| Text extraction (TXT) | Time | In-memory |
| Text extraction (PDF) | Time | pymupdf |
| Text extraction (DOCX) | Time | python-docx |
| Section classification | Time | Day 8 segmenter |
| Skill extraction | Time | Day 9 extractor |
| Experience extraction | Time | Day 10 extractor |
| Education extraction | Time | Day 11 extractor |

### 3. ATS Scoring

| Operation | Target Metric | Conditions |
|-----------|---------------|------------|
| `POST /candidates/score` | Latency p50, p95 | With resume, with embeddings |
| Skill matching | Time | Day 9 |
| Experience relevance | Time | Day 10 |
| Education alignment | Time | Day 11 |
| Semantic embeddings | Time | Day 12 (model loaded) |
| Semantic similarity | Time | Day 12 (cosine) |
| Weighted scoring | Time | Day 13 |

### 4. Eligibility & Screening

| Operation | Target Metric | Conditions |
|-----------|---------------|------------|
| Eligibility evaluation | Latency p50, p95 | With config, with score |
| Screening questions filter | Latency p50, p95 | Various filters |
| Transcript segment insert | Latency p50, p95 | Batch of 10, 100, 500 |

### 5. Database Operations

| Operation | Target Metric | Conditions |
|-----------|---------------|------------|
| Candidate list (100) | Latency | With scores |
| Candidate list (1000) | Latency | With scores |
| Shortlist query | Latency | Various thresholds |

### 6. Memory & Resource Usage

| Resource | Measurement Method |
|----------|-------------------|
| Peak RSS (upload) | `memory_profiler` or `/proc` |
| Peak RSS (scoring) | `memory_profiler` |
| Model memory (embeddings) | Process RSS delta |
| Temp file cleanup | Verify no leaks |

### 7. Concurrency (If Supported)

| Scenario | Target Metric |
|----------|---------------|
| 5 concurrent uploads | Throughput, latency |
| 10 concurrent scores | Throughput, latency |
| Mixed workload | Throughput, latency |

## Measurement Protocol

1. **Environment:** Document Python version, OS, CPU, RAM, disk type
2. **Warm-up:** Run each endpoint 5x before measuring
3. **Repetitions:** Minimum 30 runs per measurement
4. **Isolation:** Fresh database per test run (tmp_path)
5. **Fixtures:** Synthetic resumes (TXT, PDF, DOCX) of varying sizes
6. **Model State:** Measure cold (first load) and warm (cached) separately
7. **Reporting:** p50, p95, p99, mean, std dev; not single runs

## Current Test Fixtures

| Fixture | Location | Size | Format |
|---------|----------|------|--------|
| Synthetic TXT resume | `tests/test_api.py` (inline) | ~500 bytes | TXT |
| Demo resume | `data/demo_resume.txt` | ~1 KB | TXT |
| Day 4 resumes | `data/day4_data/resumes/*.json` | ~2-5 KB | JSON |

**No realistic PDF/DOCX fixtures exist for benchmarking.**

## Previous Stage-Folder Benchmarks (NOT ROOT APPLICATION)

The `day18_ats_optimization/output/performance_results.json` contains measurements from standalone modules:
- Text normalization: ~0.012s
- Entity detection: ~0.0003s
- Peak memory: ~912 KB

**These do not represent root API endpoint performance.**

## Blockers

1. No realistic PDF/DOCX test corpus
2. No controlled benchmark harness for FastAPI endpoints
3. Model loading time varies significantly (first load vs cached)
4. Background task timing not captured in endpoint latency
5. No CI/CD performance regression detection

## Next Steps

1. Create synthetic PDF/DOCX fixtures of varying complexity
2. Build benchmark script using `pytest-benchmark` or custom harness
3. Run baseline on current codebase
4. Document environment and results
5. Set up performance regression tracking

## Related Files

- `day18_ats_optimization/src/performance_benchmark.py` — Standalone module benchmarks
- `day18_ats_optimization/src/memory_monitor.py` — Memory tracking utilities
- `tests/test_api.py` — Integration tests (not benchmarks)