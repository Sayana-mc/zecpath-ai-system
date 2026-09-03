from __future__ import annotations

import time
import tracemalloc

from src.noisy_resume_handler import normalize_noisy_text
from src.entity_optimizer import detect_skills


def benchmark_text_normalization(text: str) -> float:
    start = time.perf_counter()

    normalize_noisy_text(text)

    return time.perf_counter() - start


def benchmark_entity_detection(text: str) -> float:
    start = time.perf_counter()

    detect_skills(text)

    return time.perf_counter() - start


def benchmark_memory(text: str) -> float:
    tracemalloc.start()

    normalize_noisy_text(text)
    detect_skills(text)

    current, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    return peak / 1024


def main() -> None:

    print("=" * 65)
    print("DAY 18 - ATS PERFORMANCE BENCHMARK")
    print("=" * 65)

    text = (
        "Python SQL Power BI "
        "TensorFlow Pandas NumPy "
        "Data Analyst with 3 years of experience. "
        * 1000
    )

    normalization_time = benchmark_text_normalization(text)

    entity_time = benchmark_entity_detection(text)

    memory_usage = benchmark_memory(text)

    print("\nBenchmark Results")
    print("-" * 65)

    print(
        f"Text normalization time : "
        f"{normalization_time:.6f} seconds"
    )

    print(
        f"Entity detection time   : "
        f"{entity_time:.6f} seconds"
    )

    print(
        f"Peak memory usage       : "
        f"{memory_usage:.2f} KB"
    )

    print("\nPerformance checks:")

    if normalization_time < 1.0:
        print("PASS - Text normalization is within target.")

    else:
        print("FAIL - Text normalization exceeds target.")

    if entity_time < 1.0:
        print("PASS - Entity detection is within target.")

    else:
        print("FAIL - Entity detection exceeds target.")

    print("\nBenchmark completed successfully.")

    print("=" * 65)


if __name__ == "__main__":
    main()