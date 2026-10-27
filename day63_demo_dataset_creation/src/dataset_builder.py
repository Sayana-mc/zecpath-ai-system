"""Build a demo dataset by joining resumes, jobs, and screening outputs."""

import json
import re
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = BASE_DIR / "output" / "demo_dataset.json"


def _load_json_object(file_path: Path) -> dict[str, Any]:
    try:
        value = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {file_path}: {error}") from error

    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {file_path}")
    return value


def _load_indexed_json(folder: Path, key: str) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for file_path in sorted(folder.glob("*.json")):
        record = _load_json_object(file_path)
        record_id = record.get(key)
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError(f"Missing non-empty '{key}' in {file_path}")
        if record_id in records:
            raise ValueError(f"Duplicate {key} '{record_id}' in {folder}")
        records[record_id] = record
    return records


def build_demo_dataset(
    data_dir: Path = DATA_DIR,
    output_file: Path = OUTPUT_FILE,
) -> dict[str, Any]:
    """Join the sample files and write a JSON dataset to ``output_file``."""
    data_dir = Path(data_dir)
    required_dirs = {
        name: data_dir / name
        for name in ("resumes", "job_descriptions", "screening_outputs")
    }
    for name, folder in required_dirs.items():
        if not folder.is_dir():
            raise FileNotFoundError(f"Required data directory does not exist: {folder}")

    jobs = _load_indexed_json(required_dirs["job_descriptions"], "job_id")
    screenings = _load_indexed_json(required_dirs["screening_outputs"], "candidate_id")

    for candidate_id, screening in screenings.items():
        job_id = screening.get("job_id")
        if not isinstance(job_id, str) or job_id not in jobs:
            raise ValueError(
                f"Screening output for {candidate_id} references unknown job_id "
                f"{job_id!r}"
            )

    candidates = []
    seen_candidate_ids: set[str] = set()
    for resume_path in sorted(required_dirs["resumes"].glob("*.txt")):
        match = re.match(r"resume_(\d+)(?:_|$)", resume_path.stem)
        if match is None:
            raise ValueError(f"Resume filename must start with 'resume_<number>': {resume_path}")

        candidate_id = f"CAND-{match.group(1)}"
        if candidate_id in seen_candidate_ids:
            raise ValueError(f"Multiple resume files found for {candidate_id}")
        seen_candidate_ids.add(candidate_id)

        resume_text = resume_path.read_text(encoding="utf-8").strip()
        if not resume_text:
            raise ValueError(f"Resume is empty: {resume_path}")

        screening = screenings.get(candidate_id)
        job = jobs[screening["job_id"]] if screening is not None else None
        candidates.append(
            {
                "candidate_id": candidate_id,
                "resume_file": resume_path.name,
                "resume_text": resume_text,
                "job_id": job["job_id"] if job is not None else None,
                "job_description": job,
                "screening_output": screening,
            }
        )

    if not candidates:
        raise ValueError(f"No resume .txt files found in {required_dirs['resumes']}")

    unknown_candidates = screenings.keys() - seen_candidate_ids
    if unknown_candidates:
        raise ValueError(
            "Screening output references candidates without resumes: "
            + ", ".join(sorted(unknown_candidates))
        )

    dataset = {
        "dataset_name": "zecpath_demo_dataset",
        "schema_version": 1,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return dataset
