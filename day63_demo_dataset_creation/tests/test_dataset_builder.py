import json
import tempfile
import unittest
from pathlib import Path

from src.dataset_builder import BASE_DIR, build_demo_dataset


class BuildDemoDatasetTests(unittest.TestCase):
    def test_builds_dataset_from_sample_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "nested" / "demo.json"
            dataset = build_demo_dataset(BASE_DIR / "data", output_file)

            self.assertEqual(dataset["candidate_count"], 6)
            self.assertEqual(len(dataset["candidates"]), 6)
            self.assertTrue(output_file.is_file())
            self.assertEqual(json.loads(output_file.read_text(encoding="utf-8")), dataset)

    def test_joins_available_screening_and_job_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset = build_demo_dataset(
                BASE_DIR / "data",
                Path(temp_dir) / "demo.json",
            )
        candidates = {
            candidate["candidate_id"]: candidate
            for candidate in dataset["candidates"]
        }

        self.assertEqual(
            candidates["CAND-001"]["job_id"],
            "JOB-DA-001",
        )
        self.assertEqual(
            candidates["CAND-001"]["job_description"]["title"],
            "Junior Data Analyst",
        )
        self.assertTrue(candidates["CAND-001"]["screening_output"]["human_review_required"])
        self.assertIsNone(candidates["CAND-002"]["screening_output"])
        self.assertIsNone(candidates["CAND-002"]["job_description"])

    def test_rejects_missing_data_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(FileNotFoundError):
                build_demo_dataset(Path(temp_dir) / "missing", Path(temp_dir) / "out.json")

    def test_rejects_screening_reference_to_unknown_job(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            for folder in ("resumes", "job_descriptions", "screening_outputs"):
                (data_dir / folder).mkdir(parents=True)
            (data_dir / "resumes" / "resume_001_demo.txt").write_text(
                "Sample resume",
                encoding="utf-8",
            )
            (data_dir / "job_descriptions" / "job.json").write_text(
                json.dumps({"job_id": "JOB-001"}),
                encoding="utf-8",
            )
            (data_dir / "screening_outputs" / "CAND-001.json").write_text(
                json.dumps({"candidate_id": "CAND-001", "job_id": "JOB-MISSING"}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "unknown job_id"):
                build_demo_dataset(data_dir, Path(temp_dir) / "out.json")

    def test_rejects_screening_without_resume(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            for folder in ("resumes", "job_descriptions", "screening_outputs"):
                (data_dir / folder).mkdir(parents=True)
            (data_dir / "resumes" / "resume_001_demo.txt").write_text(
                "Sample resume",
                encoding="utf-8",
            )
            (data_dir / "job_descriptions" / "job.json").write_text(
                json.dumps({"job_id": "JOB-001"}),
                encoding="utf-8",
            )
            (data_dir / "screening_outputs" / "CAND-002.json").write_text(
                json.dumps({"candidate_id": "CAND-002", "job_id": "JOB-001"}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "without resumes"):
                build_demo_dataset(data_dir, Path(temp_dir) / "out.json")


if __name__ == "__main__":
    unittest.main()
