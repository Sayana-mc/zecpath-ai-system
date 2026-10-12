
from pathlib import Path

from .evaluator import run_evaluation


PROJECT_DIR = Path(__file__).resolve().parents[1]


def main():
    input_path = PROJECT_DIR / "data" / "sample_submission.json"
    config_path = PROJECT_DIR / "config" / "scoring_rules.json"
    output_path = PROJECT_DIR / "output" / "machine_test_report.json"

    run_evaluation(input_path, config_path, output_path)


if __name__ == "__main__":
    main()
