import asyncio, json, time, tracemalloc
from pathlib import Path
from .pipeline import process_resumes
from .cache import TTLCache

async def run_case(count, batch_size, concurrency, delay_ms):
    texts = [f"Candidate {i % max(1,count//2)} has Python SQL Excel and pandas." for i in range(count)]
    cache = TTLCache(max_entries=max(128,count), ttl_seconds=120)
    tracemalloc.start(); start = time.perf_counter()
    result = await process_resumes(texts, batch_size, concurrency, delay_ms/1000, cache)
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    return {"items": count, "batch_size": batch_size, "max_concurrency": concurrency,
      "elapsed_seconds": round(elapsed,6),
      "throughput_items_per_second": round(count/elapsed,2) if elapsed else 0,
      "cache_hits": result["cache_hits"], "cache_hit_rate": round(result["cache_hit_rate"],4),
      "current_traced_bytes": current, "peak_traced_bytes": peak,
      "success_count": result["processed"], "failure_count": 0,
      "note": "Synthetic local workload; simulated delay, not real model latency."}

async def make_report(cfg):
    cases=[]
    for c in cfg["load_test_concurrency_levels"]:
        cases.append(await run_case(int(cfg["simulated_resume_count"]), int(cfg["batch_size"]),
                                    int(c), float(cfg["simulated_inference_delay_ms"])))
    return {"title":"Day 60 Performance Benchmark Report", "project":"Zecpath AI Hiring System",
      "environment":"Synthetic local simulation", "configuration":cfg, "cases":cases,
      "limitations":["Mock inference only; no live AI provider or production database.",
      "tracemalloc measures Python-traced allocations, not total process or GPU memory.",
      "Results are not a production SLA or real model-inference benchmark."]}

def run_benchmark(root):
    cfg=json.loads((root/"config/performance_config.json").read_text(encoding="utf-8"))
    report=asyncio.run(make_report(cfg))
    out=root/"output"; out.mkdir(exist_ok=True)
    (out/"benchmark_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    lines=["# Day 60 — Performance Benchmark Report","","**Important:** Synthetic local simulation only; not production measurements.","",
      "| Items | Batch | Concurrency | Elapsed (s) | Throughput/items/s | Cache hit rate | Peak traced bytes |",
      "|---:|---:|---:|---:|---:|---:|---:|"]
    for x in report["cases"]:
        lines.append(f"| {x['items']} | {x['batch_size']} | {x['max_concurrency']} | {x['elapsed_seconds']} | {x['throughput_items_per_second']} | {x['cache_hit_rate']} | {x['peak_traced_bytes']} |")
    lines += ["","## Limitations"] + [f"- {x}" for x in report["limitations"]]
    lines += ["","## Production benchmark next steps","Run against staging with representative anonymized inputs, actual model/API and database calls. Record p50/p95/p99, throughput, error rate, queue age, CPU/RAM/GPU, and cost per resume."]
    (out/"benchmark_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return report
