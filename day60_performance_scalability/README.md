# Day 60 — Performance Tuning & Scalability
Project: Zecpath AI Hiring System

This is a local performance-engineering prototype, not a production AI service. It demonstrates bounded batching, concurrency, a TTL/LRU cache, synthetic load testing, memory tracing, and scalability planning. The benchmark uses mock inference and simulated delays; do not report its values as real model or production performance.

Run from `C:\Users\sayan\Documents\zecpath-ai-system`:
```powershell
python -m day60_performance_scalability.src.main
python -m unittest discover -s .\day60_performance_scalability\tests -v
```
Outputs: `day60_performance_scalability/output/benchmark_report.json` and `.md`.
