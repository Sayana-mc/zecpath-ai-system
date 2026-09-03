from __future__ import annotations

import gc
import os
import tracemalloc


def start_monitoring():

    tracemalloc.start()


def get_memory_usage():

    current, peak = tracemalloc.get_traced_memory()

    return {
        "current_mb": round(
            current / (1024 * 1024),
            4,
        ),
        "peak_mb": round(
            peak / (1024 * 1024),
            4,
        ),
    }


def cleanup():

    gc.collect()


def stop_monitoring():

    tracemalloc.stop()


if __name__ == "__main__":

    print("=" * 65)
    print("MEMORY MONITORING")
    print("=" * 65)

    start_monitoring()

    data = [
        "ATS processing test"
        for _ in range(10000)
    ]

    print("\nMemory usage:")

    print(get_memory_usage())

    del data

    cleanup()

    print("\nAfter cleanup:")

    print(get_memory_usage())

    stop_monitoring()

    print("\nMemory monitoring completed.")

    print("=" * 65)