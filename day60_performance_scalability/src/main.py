from pathlib import Path
from .benchmark import run_benchmark
def main():
    root=Path(__file__).resolve().parents[1]
    report=run_benchmark(root)
    print("Day 60 synthetic benchmark completed.")
    for x in report["cases"]:
        print(f"concurrency={x['max_concurrency']} throughput={x['throughput_items_per_second']} items/s cache_hit_rate={x['cache_hit_rate']} peak_bytes={x['peak_traced_bytes']}")
    print(f"Reports: {root/'output'}")
if __name__ == "__main__": main()
