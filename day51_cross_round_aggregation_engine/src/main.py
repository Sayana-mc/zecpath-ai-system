
from pathlib import Path

from .aggregation_engine import run_aggregation


PROJECT_DIR = Path(__file__).resolve().parents[1]


def main():
    input_path = PROJECT_DIR / "data" / "candidate_evaluations.json"
    config_path = PROJECT_DIR / "config" / "role_weights.json"
    output_path = PROJECT_DIR / "output" / "unified_candidate_score.json"

    run_aggregation(input_path, config_path, output_path)


if __name__ == "__main__":
    main()
