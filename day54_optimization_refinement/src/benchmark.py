
from time import perf_counter

from day54_optimization_refinement.src.refined_scoring import (
    evaluate_candidate
)
from day54_optimization_refinement.src.intent_detector import detect_intent


def benchmark_processing(config, iterations=1000):
    if (
        isinstance(iterations, bool)
        or not isinstance(iterations, int)
        or iterations < 1
    ):
        raise ValueError("iterations must be a positive integer.")

    thresholds = config["thresholds"]
    consistency = config["consistency"]
    review = config["review"]

    scores = [82, 85, 79, 88, 84]
    text = "Explain this candidate's role fit"

    start = perf_counter()

    for _ in range(iterations):
        evaluate_candidate(
            score=82.25,
            round_scores=scores,
            completed_rounds=len(scores),
            thresholds=thresholds,
            consistency_config=consistency,
            review_config=review,
            intent="explain_role_fit"
        )

    scoring_seconds = perf_counter() - start

    start = perf_counter()

    for _ in range(iterations):
        detect_intent(text)

    intent_seconds = perf_counter() - start

    return {
        "iterations_per_operation": iterations,
        "scoring": {
            "total_seconds": round(scoring_seconds, 6),
            "average_milliseconds": round(
                scoring_seconds * 1000 / iterations, 6
            )
        },
        "intent_detection": {
            "total_seconds": round(intent_seconds, 6),
            "average_milliseconds": round(
                intent_seconds * 1000 / iterations, 6
            )
        },
        "measurement_note": (
            "Local microbenchmark of in-process Python functions. "
            "It excludes database, network, model inference, file I/O "
            "and end-to-end application latency."
        )
    }
